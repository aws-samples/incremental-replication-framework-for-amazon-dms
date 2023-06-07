""" Variable representing the account number for cases when it is not resolvable before deployment by cdk"""
ACCOUNT_NUMBER = '' # Include your account number details

""" Dict representing the network configuration so that it is easily referenced throughout the deployment and keeps
consistency between all the elements in the architecture. 

Supported properties are:
    - 'vpc_id': str. Id of the vpc
    - 'region': str. Region of the vpc. Also used for referencing the region when needed.
    - 'availability_zones': list. List of availability zones where resources will be deployed. Aligned with subnet structure.
    - 'private_subnets': list. List of private subnet ids.
    - 'security_groups': dict. Dict with keys representing ids to be used on job execution and values representing the actual
    security group id of the aws resource.
"""
VPC_PROPS = {
    'vpc_id': '', # Include your vpc details
    'region': '', # Include your vpc details
    'availability_zones': [], # Include your vpc details
    'private_subnets': [], # Include your vpc details
    'security_groups': {
        'security_group_01': '' # Include your vpc details
    }
}

""" Dict representing the common properties so that they are easily referenced throughout the deployment and keeps
consistency between all the elements in the architecture. 

Supported properties are:
    - 'notifications_topic_name': str. Name of the topic to be used for notification purposes.
    - 'notification_emails': list. List of emails that will be subscribed into notifications topic. 
    - 'artifact_bucket_name': str. Name of the s3 bucket were artifacts will be deployed.
    - 'replication_jobs_config_prefix': str. String representing the prefix to the folder from within the s3 bucket 
    where DMS task files (settings and mappings) will be stored partitioned by job name.
    - 'replication_checkpoints_table_name': str. Name of the DynamoDB table where checkpoints will be stored.
    - 'replication_metrics_table_name': str. Name of the DynamoDB table where metrics will be stored.
    - 'replication_jobs_table_name': str. Name of the DynamoDB table where job definition will be stored.
    - 'replication_instances_table_name': str. Name of the DynamoDB table where instance definition will be stored.
    - 'replication_event_bus_name': str. Name of the EventBridge event bus where completion events will be send for workflow choreography.
    - 'dms_cloudwatch_logs_role': bool. If DMS role for interacting with ClodWatch logs needs to be created.
    - 'dms_vpc_role': bool. If DMS role for interacting with VPC needs to be created.
    - 'dms_secrets_common_role_name': str. Name of the role that will allow DMS to access secrets in Secrets Manager.
    - 'lambda_replication_common_role_name': str. Name of the role that will allow lambda functions to interact with other AWS services on execution.
    - 'workflow_replication_common_role_name': str. Name of the role that will allow state machines (step functions) to interact with other AWS services on execution.
    - 'eventbridge_replication_common_role_name': str. Name of the role that will allow EventBridge rules to interact with other AWS services on execution.
"""
COMMON_PROPS = {
    'notifications_topic_name': 'increp-notifications_topic',
    'notification_emails': [
        # Include your notification emails
    ],
    'artifact_bucket_name': f"increp-{ACCOUNT_NUMBER}-{VPC_PROPS['region']}-artifact",
    'replication_jobs_config_prefix': 'increp-jobs-config',
    'replication_checkpoints_table_name': 'increp-checkpoints',
    'replication_metrics_table_name': 'increp-metrics',
    'replication_jobs_table_name': 'increp-jobs',
    'replication_instances_table_name': 'increp-instances',
    'replication_event_bus_name': 'increp-event-bus',
    'dms_cloudwatch_logs_role': True, # Only leave as true if no dms-cloudwatch-logs-role role in your account
    'dms_vpc_role': True, # Only leave as true if no dms-vpc-logs-role role in your account
    'dms_secrets_common_role_name': 'increp-dms-secrets-common-role',
    'lambda_replication_common_role_name': 'increp-lambda-common-role',
    'workflow_replication_common_role_name': 'increp-workflow-common-role',
    'eventbridge_replication_common_role_name': 'increp-eventbridge-common-role'
}