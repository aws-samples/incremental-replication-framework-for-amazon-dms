import os
import json
import boto3
from boto3.dynamodb.types import TypeSerializer
import re
from datetime import datetime

# Constant: Represents the keys to keep from DMS API response when requesting DMS task details.
REPLICATION_TASK_KEYS = [
    'ReplicationTaskIdentifier', 'SourceEndpointArn', 'TargetEndpointArn', 'ReplicationInstanceArn', 
    'MigrationType', 'Status', 'StopReason', 'ReplicationTaskCreationDate', 'ReplicationTaskStartDate', 
    'CdcStopPosition', 'RecoveryCheckpoint', 'ReplicationTaskArn', 'ReplicationTaskStats' 
]

# Constant: Represents default values to include when key is not found in DMS API response when requesting DMS task details.
DEFAULT_OUTPUT_VALUES = {
    'CdcStopPosition': ''
}

# Constant: Value to be used to identify mos recent checkpoint for a job in the job checkpoints table
LATEST_CHECKPOINT_JOB_START_VALUE = 'latest'

# Constants: Lambda environment variables
REPLICATION_METRICS_TABLE_NAME = os.getenv('REPLICATION_METRICS_TABLE_NAME')
REPLICATION_CHECKPOINTS_TABLE_NAME = os.getenv('REPLICATION_CHECKPOINTS_TABLE_NAME')

# Boto3 Clients: DMS, DynamoDB
dms = boto3.client('dms')
dynamodb = boto3.client('dynamodb')
dynamodb_serializer = TypeSerializer()

def handler(event, context):
    """ Function handler: 1/ Will retrieve Task details from DMS API. 2/ Persist checkpoint value in DynamoDB (preserving DMS
    original value). 3/ Persist task metrics in DynamoDB. 4/ Format DMS API response and return DMS task details.

    Parameters
    ----------
    event : dict
        input event dictionary. Should include 'JobName', 'JobConfig' and 'TaskDetails' keys

    context: dict
        input context. Not used on function

    Returns
    -------
        replication_task_details : dict
            dict with all details of DMS task as returned from DMS API and formatted for ease of use and standardization.
    """

    # Get key elements from event
    job_name = event['JobName']
    job_config = event['JobConfig']
    job_details = event['TaskDetails']

    # Get final task details from DMS
    replication_task_arn = job_details['ReplicationTaskArn']
    dms_response = dms.describe_replication_tasks(
        Filters= [{'Name': 'replication-task-arn', 'Values':[replication_task_arn]}]
    )

    dms_response = json.loads(json.dumps(dms_response, default=json_datetime_encoder))
    job_task_details = {
        key: dms_response['ReplicationTasks'][0][key] for key in REPLICATION_TASK_KEYS if key in dms_response['ReplicationTasks'][0]
    }

    # Save checkpoints in DynamoDB (both for current execution and latest)
    job_checkpoint_name = job_config['job_checkpoint_name']
    job_start = job_task_details['ReplicationTaskStartDate'] 
    job_checkpoint = job_task_details['RecoveryCheckpoint'] 

    dynamo_response = dynamodb.batch_write_item(
        RequestItems= {
            REPLICATION_CHECKPOINTS_TABLE_NAME: [
                {
                    'PutRequest': {
                        'Item': {
                            'job_checkpoint_name': dynamodb_serializer.serialize(job_checkpoint_name),
                            'job_start':  dynamodb_serializer.serialize(job_start),
                            'job_name': dynamodb_serializer.serialize(job_name),
                            'checkpoint': dynamodb_serializer.serialize(job_checkpoint)
                        }
                    }
                },
                {
                    'PutRequest': {
                        'Item': {
                            'job_checkpoint_name': dynamodb_serializer.serialize(f'{job_checkpoint_name}'),
                            'job_start':  dynamodb_serializer.serialize(LATEST_CHECKPOINT_JOB_START_VALUE),
                            'job_name': dynamodb_serializer.serialize(job_name),
                            'checkpoint': dynamodb_serializer.serialize(job_checkpoint)
                        }
                    }
                } 
            ]
                
        }
    )

    # Save metrics in DynamoDB
    job_metrics = {camel_to_snake(key): value for key, value in job_task_details['ReplicationTaskStats'].items()}
    dynamo_response = dynamodb.batch_write_item(
        RequestItems= {
            REPLICATION_METRICS_TABLE_NAME: [
                {
                    'PutRequest': {
                        'Item': {
                            'job_checkpoint_name': dynamodb_serializer.serialize(job_checkpoint_name),
                            'job_start':  dynamodb_serializer.serialize(job_start),
                            'job_name': dynamodb_serializer.serialize(job_name),
                            **{key: dynamodb_serializer.serialize(value) for key, value in job_metrics.items()}
                        }
                    }
                } 
            ]
                
        }
    )

    # Create and return response with all final details (merge of details and dms task describe results)
    replication_task_details = {
        **job_task_details,
        **job_details
    }

    # Include default values for certain keys that state machines step output expects
    for key, default_value in DEFAULT_OUTPUT_VALUES.items():
        if key not in replication_task_details: replication_task_details[key] = default_value

    return replication_task_details


def json_datetime_encoder(obj):
    """ Complementary function to encode JSON values into DynamoDB attribute values """
    
    if isinstance(obj, (datetime)): return obj.strftime("%Y-%m-%dT%H:%M:%S")

def camel_to_snake(name):
    """ Complementary function to transform a string from Camel to Snake format """

    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

