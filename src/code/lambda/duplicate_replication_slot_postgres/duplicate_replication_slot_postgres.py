
import json
import boto3
import re
from datetime import datetime
import psycopg2

# Constant: Represents the postgres regex to use to format DMS checkpoint
CHECKPOINT_REGEX = '[A-Z|0-9]{1}\/[A-Z|0-9]*'

# Boto3 Clients: DMS, Secrets Manager
dms = boto3.client('dms')
secrets_manager = boto3.client('secretsmanager') 

def handler(event, context):
    """ Function handler: Function that will duplicate postgres replication slot on source after full replication task 
    completion so that slot is not lost when eliminating DMS task and future CDC tasks are enabled.
    1/ Will retrieve Task details from DMS API. 2/ Retrieve secret value for DMS source endpoints from DMS API. 
    3/ Retrieve secret value (source connection details) from Secrets Manager. 4/ Connect to source database and execute 
    queries to duplicate replication slot using checkpoint name for job as slot name.

    Parameters
    ----------
    event : dict
        input event dictionary. Should include 'JobName', and 'JobConfig' keys

    context: dict
        input context. Not used on function

    Returns
    -------
        response : dict
            custom dict with 'slot_name' and 'checkpoint' keys representing the duplicated slot created in source postgres 
            database.
    """

    # Get key elements from event
    job_name = event['JobName']
    job_config = event['JobConfig']
    
    job_source_endpoint_id = job_config['source_endpoint_id']
    job_checkpoint_name = job_config['job_checkpoint_name']

    # Get task details from DMS
    task_details = get_task_details(job_name)
    task_checkpoint = task_details['RecoveryCheckpoint']

    # Get source endpoint details from DMS and Secrets Manager
    job_source_endpoint_id = job_config['source_endpoint_id']
    job_source_endpoint_details = get_endpoint_details(job_source_endpoint_id)
    job_source_endpoint_arn = job_source_endpoint_details['EndpointArn']

    job_source_endpoint_secret_arn = job_source_endpoint_details['PostgreSQLSettings']['SecretsManagerSecretId']
    job_source_endpoint_secret = get_secret(job_source_endpoint_secret_arn)

    # Connect to source database
    conn_source = psycopg2.connect(
        dbname= job_source_endpoint_details['DatabaseName'],
        user= job_source_endpoint_secret['username'],
        password= job_source_endpoint_secret['password'],
        host= job_source_endpoint_secret['host'],
        port= job_source_endpoint_secret['port']
    )
    cur_source = conn_source.cursor()

    # Query slot with task endpoint
    query_checkpoint = re.findall(CHECKPOINT_REGEX, task_checkpoint)[0]
    cur_source.execute(f"SELECT * FROM pg_replication_slots WHERE restart_lsn='{query_checkpoint}';")
    slot_record = cur_source.fetchall()[0]
    slot_id = slot_record[0]
    
    # Duplicate slot so that it is not lost when deleting full task
    duplicate_slot_name = job_checkpoint_name.replace('-', '_')
    cur_source.execute(f"SELECT * FROM pg_copy_logical_replication_slot('{slot_id}', '{duplicate_slot_name}');")
    duplicate_slot_record = cur_source.fetchall()[0]

    # Close connection to the source database
    cur_source.close()
    conn_source.close()

    response = {
        'slot_name': duplicate_slot_record[0],
        'checkpoint': duplicate_slot_record[1]
    }
    
    return response

def json_datetime_encoder(obj):
    """ Complementary function to transform dict objects delivered by DMS API into JSONs """
    
    if isinstance(obj, (datetime)): return obj.strftime("%Y-%m-%dT%H:%M:%S")

def get_task_details(task_name):
    """ Complementary function to retrieve DMS task details from DMS API """

    dms_response = dms.describe_replication_tasks(
        Filters= [{'Name': 'replication-task-id', 'Values':[task_name]}]
    )

    dms_response = json.loads(json.dumps(dms_response, default=json_datetime_encoder))
    task_details = dms_response['ReplicationTasks'][0]
    
    return task_details

def get_endpoint_details(endpoint_id):
    """ Complementary function to retrieve DMS endpoint details from DMS API """

    dms_response = dms.describe_endpoints(
        Filters= [{'Name': 'endpoint-id', 'Values':[endpoint_id]}]
    )

    dms_response = json.loads(json.dumps(dms_response, default=json_datetime_encoder))
    endpoint_details = dms_response['Endpoints'][0]
    
    return endpoint_details

def get_secret(secret_arn):
    """ Complementary function to retrieve secret value from Secrets Manager """
    
    secrets_manager_response = secrets_manager.get_secret_value(
        SecretId= secret_arn
    )

    secrets_manager_response = json.loads(json.dumps(secrets_manager_response, default=json_datetime_encoder))
    secret_details = json.loads(secrets_manager_response['SecretString'])
    
    return secret_details
