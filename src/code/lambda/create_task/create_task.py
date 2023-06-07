import os
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer
import re
from datetime import datetime, timedelta

# Constant: Represents the regex to use by engine type to format DMS checkpoint accordingly on task creation
CHECKPOINT_REGEX_BY_SOURCE_TYPE = {
    'postgresql': '[A-Z|0-9]{3}\/[A-Z|0-9]*',
    'aurora-postgresql': '[A-Z|0-9]{3}\/[A-Z|0-9]*',
    'mysql': '.*',
    'aurora': '.*',
}

# Constant: Represents the start operation according to migration type
START_REPLICATION_TASK_TYPE_BY_MIGRATION_TYPE = {
    'full-load-and-cdc': 'reload-target',
    'cdc': 'start-replication'
}

# Constant: Value to be used to identify mos recent checkpoint for a job in the job checkpoints table
LATEST_CHECKPOINT_JOB_START_VALUE = 'latest'

# Constants: Lambda environment variables
REPLICATION_CHECKPOINTS_TABLE_NAME = os.getenv('REPLICATION_CHECKPOINTS_TABLE_NAME')
ARTIFACTS_BUCKET_NAME = os.getenv('ARTIFACTS_BUCKET_NAME')
REPLICATION_JOBS_CONFIG_PREFIX = os.getenv('REPLICATION_JOBS_CONFIG_PREFIX')

# Boto3 Clients: DMS, S3, DynamoDB
dms = boto3.client('dms')
s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')
dynamodb_deserializer = TypeDeserializer()

def handler(event, context):
    """ Function handler: 1/ Will retrieve Job Details for task creation from event. 2/ Retrieve complementary values for
    DMS instance and endpoints from DMS API. 3/ Retrieve task settings and mappings from S3. 4/ create a DMS task with all 
    retrieved details. When creating a CDC task in DMS, checkpoint values will be retrieved and checkpoint data will be 
    included as well.

    Parameters
    ----------
    event : dict
        input event dictionary. Should include 'JobName', 'InstanceName' and 'JobConfig' keys

    context: dict
        input context. Not used on function

    Returns
    -------
        replication_task_details : dict
            dict with all details of DMS created task as returned from DMS API and formatted for ease of use.
            Also including a 'StartReplicationTaskType' key for starting task accordingly on next steps.
    """
    
    # Get key elements from event
    job_name = event['JobName']
    instance_name = event['InstanceName']
    job_config = event['JobConfig']
    
    job_source_endpoint_id = job_config['source_endpoint_id']
    job_target_endpoint_id = job_config['target_endpoint_id']
    job_migration_type = job_config['migration_type']
    job_checkpoint_name = job_config['job_checkpoint_name']

    # Get instance details from DMS
    instance_details = get_instance_details(instance_name)
    instance_arn = instance_details['ReplicationInstanceArn']

    # Get source endpoint details from DMS
    job_source_endpoint_details = get_endpoint_details(job_source_endpoint_id)
    job_source_endpoint_arn = job_source_endpoint_details['EndpointArn']
    job_source_type = job_source_endpoint_details['EngineName']

    # Get target endpoint details from DMS
    job_target_endpoint_details = get_endpoint_details(job_target_endpoint_id)
    job_target_endpoint_arn = job_target_endpoint_details['EndpointArn']

    # Get DMS task settings from S3
    job_settings_key = f'{REPLICATION_JOBS_CONFIG_PREFIX}/{job_name}/settings.json'
    job_settings = read_s3_json_file(ARTIFACTS_BUCKET_NAME, job_settings_key)

    # Get DMS task mappings from S3
    job_mappings_key = f'{REPLICATION_JOBS_CONFIG_PREFIX}/{job_name}/mappings.json'
    job_mappings = read_s3_json_file(ARTIFACTS_BUCKET_NAME, job_mappings_key)

    # Set CDC parameters - Get strat checkpoint when cdc task and stablish stop commit
    job_cdc_parameters = {}

    if job_migration_type == 'cdc':
        checkpoint_item = get_checkpoint_item(job_checkpoint_name)
        checkpoint_regex = CHECKPOINT_REGEX_BY_SOURCE_TYPE[job_source_type]
        job_cdc_parameters['CdcStartPosition'] = re.findall(checkpoint_regex, checkpoint_item['checkpoint'])[0]

        job_stop_commit_time = datetime.now() + timedelta(minutes=5)
        job_stop_commit_time_str = job_stop_commit_time.strftime('%Y-%m-%dT%H:%M:%S')
        job_cdc_parameters['CdcStopPosition']= f'commit_time:{job_stop_commit_time_str}'

    # Create DMS replication task
    dms_response = dms.create_replication_task(
        ReplicationTaskIdentifier= job_name,
        SourceEndpointArn= job_source_endpoint_arn,
        TargetEndpointArn= job_target_endpoint_arn,
        ReplicationInstanceArn= instance_arn,
        MigrationType= job_migration_type,
        ReplicationTaskSettings= json.dumps(job_settings),
        TableMappings= json.dumps(job_mappings),
        **job_cdc_parameters
    )

    dms_response = json.loads(json.dumps(dms_response, default=json_datetime_encoder))

    # Format response - Replication task details (formatting Status for state machine use and adding start replication task type)
    replication_task_details = dms_response['ReplicationTask']
    replication_task_details['Status'] = {'LatestStatus': replication_task_details['Status']}
    replication_task_details['StartReplicationTaskType'] = START_REPLICATION_TASK_TYPE_BY_MIGRATION_TYPE[job_migration_type]

    return replication_task_details


def json_datetime_encoder(obj):
    """ Complementary function to transform dict objects delivered by DMS API into JSONs """
    
    if isinstance(obj, (datetime)): return obj.strftime("%Y-%m-%dT%H:%M:%S")

def get_instance_details(instance_id):
    """ Complementary function to retrieve DMS instance details from DMS API """

    dms_response = dms.describe_replication_instances(
        Filters= [{'Name': 'replication-instance-id', 'Values':[instance_id]}]
    )

    dms_response = json.loads(json.dumps(dms_response, default=json_datetime_encoder))
    instance_details = dms_response['ReplicationInstances'][0]
    
    return instance_details

def get_endpoint_details(endpoint_id):
    """ Complementary function to retrieve DMS endpoint details from DMS API """

    dms_response = dms.describe_endpoints(
        Filters= [{'Name': 'endpoint-id', 'Values':[endpoint_id]}]
    )

    dms_response = json.loads(json.dumps(dms_response, default=json_datetime_encoder))
    endpoint_details = dms_response['Endpoints'][0]
    
    return endpoint_details

def read_s3_json_file(bucket_name, key_path):
    """ Complementary function to retrieve json from S3 file """
    
    object = s3.get_object(
        Bucket= bucket_name, 
        Key= key_path
    )

    json_object = json.loads(object["Body"].read().decode())

    return json_object

def get_checkpoint_item(checkpoint_name):
    """ Complementary function to retrieve latest checkpoint record for job from DynamoDB """

    dynamodb_response = dynamodb.get_item(
        TableName= REPLICATION_CHECKPOINTS_TABLE_NAME,
        Key= {
            'job_checkpoint_name': {
                'S': f'{checkpoint_name}'
            },
            'job_start': {
                'S': LATEST_CHECKPOINT_JOB_START_VALUE
            }
        }
    )

    checkpoint_item = {key: dynamodb_deserializer.deserialize(value) for key, value in dynamodb_response['Item'].items()}
    
    return checkpoint_item
