from config.common_config import COMMON_PROPS, VPC_PROPS

""" Dict representing the structure to define workflows' properties. Every key value pair in the root
represents a single workflow configuration. The key is the id that will be used from within the stack and the
value is a dict with the set of properties for that particular workflow. 

Properties are described per workflow:
- 'create_instance' workflow will be used to ramp-up new DMS replication instances based on instance definition stored in DynamoDB.
Note that this is a workflow that is fully based on a step function state machine. Properties for this workflow include:
    - 'state_machine_name': str. Representing the name of the state machine that will be orchestrating all the process. 
    - 'workflow_replication_common_role_name': str. Representing the name of the role that the state machine will be assuming on execution.
    - 'replication_instances_table_name': str. Name of the DynamoDB table where instance configurations are going to be stored.
    - 'replication_event_bus_name': str. Name of the EventBridge event bus where success finish event will be sent for subsequent workflow execution.

- 'execute_task' workflow will be used to create, start and wait till completion DMS replication tasks based on job definition stored in DynamoDB.
Note that this is a workflow that is based on a step function state machine and supporting lambda functions. Properties for this workflow include:
    - 'state_machine_name': str. Representing the name of the state machine that will be orchestrating all the process. 
    - 'workflow_replication_common_role_name': str. Representing the name of the role that the state machine will be assuming on execution.
    - 'lambda_replication_common_role_name': str. Representing the name of the role that lambda functions will be assuming on execution.
    - 'replication_jobs_table_name': str. Name of the DynamoDB table where jobs configurations are going to be stored.
    - 'replication_checkpoints_table_name': str. Name of the DynamoDB table where jobs checkpoints are going to be stored.
    - 'replication_metrics_table_name': str. Name of the DynamoDB table where jobs metrics are going to be stored.
    - 'artifact_bucket_name': str. Name of the S3 bucket where task settings and mappings json files are stored.
    - 'replication_jobs_config_prefix': str. Prefix inside S3 bucket where task settings and mappings json files are stored.
    - 'replication_event_bus_name': str. Name of the EventBridge event bus where success finish event will be sent for subsequent workflow execution.
    - 'notifications_topic_name': str. Name of the SNS topic where notifications are going to be sent.

- 'post_full_task_postgres' workflow will be used to execute postgres specific tasks after a full load replication task termination. This includes the duplication
of the replication slot so that it can be leveraged by subsequent cdc tasks. Note that in order to achieve such duplication, a lambda function needs to connect to the source db
because of which it needs to be deployed in a vpc with network configuration that allows such connection. Note that this is a workflow that is based on a step function state machine 
and supporting lambda functions. Properties for this workflow include:
    - 'state_machine_name': str. Representing the name of the state machine that will be orchestrating all the process. 
    - 'workflow_replication_common_role_name': str. Representing the name of the role that the state machine will be assuming on execution.
    - 'lambda_replication_common_role_name': str. Representing the name of the role that lambda functions will be assuming on execution.
    - 'replication_jobs_table_name': str. Name of the DynamoDB table where jobs configurations are going to be stored.
    - 'replication_event_bus_name': str. Name of the EventBridge event bus where success finish event will be sent for subsequent workflow execution.
    - 'notifications_topic_name': str. Name of the SNS topic where notifications are going to be sent.
    - 'lambda_layer_region': str. Lambda connecting to source database leverages a public psycopg2 lambda layer. This property represents the region where lambda function
    is going to be deployed to map the right lambda layer arn.
    - 'vpc_id': str. Representing the id of the vpc where the lambda function will be deployed.
    - 'vpc_private_subnet_ids': list. Representing the list of ids of the subnets where the lambda function will be deployed.
    - 'vpc_security_group_id': list. Representing the id of the vpc to assign to the lambda function when deployed.

- 'delete_task' workflow will be used to delete a DMS replication tasks.
Note that this is a workflow that is based on a step function state machine. Properties for this workflow include:
    - 'state_machine_name': str. Representing the name of the state machine that will be orchestrating all the process. 
    - 'workflow_replication_common_role_name': str. Representing the name of the role that the state machine will be assuming on execution.
    - 'replication_event_bus_name': str. Name of the EventBridge event bus where success finish event will be sent for subsequent workflow execution.

- 'delete_instance' workflow will be used to delete a DMS replication instances.
Note that this is a workflow that is based on a step function state machine. Properties for this workflow include:
    - 'state_machine_name': str. Representing the name of the state machine that will be orchestrating all the process. 
    - 'workflow_replication_common_role_name': str. Representing the name of the role that the state machine will be assuming on execution.
    - 'replication_event_bus_name': str. Name of the EventBridge event bus where success finish event will be sent for subsequent workflow execution.
"""
WORKFLOW_PROPS = {
    'create_instance': {
        'state_machine_name': 'create_instance_workflow',
        
        'workflow_replication_common_role_name': COMMON_PROPS['workflow_replication_common_role_name'],
        'replication_instances_table_name': COMMON_PROPS['replication_instances_table_name'],
        'replication_event_bus_name': COMMON_PROPS['replication_event_bus_name']
    },
    'execute_task': {
        'state_machine_name': 'execute_job_workflow',

        'workflow_replication_common_role_name': COMMON_PROPS['workflow_replication_common_role_name'],
        'lambda_replication_common_role_name': COMMON_PROPS['lambda_replication_common_role_name'],
        'replication_jobs_table_name': COMMON_PROPS['replication_jobs_table_name'],
        'replication_checkpoints_table_name': COMMON_PROPS['replication_checkpoints_table_name'],
        'replication_metrics_table_name': COMMON_PROPS['replication_metrics_table_name'],
        'artifact_bucket_name': COMMON_PROPS['artifact_bucket_name'],
        'replication_jobs_config_prefix': COMMON_PROPS['replication_jobs_config_prefix'],
        'replication_event_bus_name': COMMON_PROPS['replication_event_bus_name'],
        'notifications_topic_name': COMMON_PROPS['notifications_topic_name']
    },
    'post_full_task_postgres': {
        'state_machine_name': 'post_full_task_postgres',
        
        'workflow_replication_common_role_name': COMMON_PROPS['workflow_replication_common_role_name'],
        'lambda_replication_common_role_name': COMMON_PROPS['lambda_replication_common_role_name'],
        'replication_jobs_table_name': COMMON_PROPS['replication_jobs_table_name'],
        'replication_event_bus_name': COMMON_PROPS['replication_event_bus_name'],
        'notifications_topic_name': COMMON_PROPS['notifications_topic_name'],
        
        'lambda_layer_region': VPC_PROPS['region'],
        'vpc_id': VPC_PROPS['vpc_id'],
        'vpc_private_subnet_ids': VPC_PROPS['private_subnets'],
        'vpc_security_group_id': VPC_PROPS['security_groups']['security_group_01'],
    },
    'delete_task': {
        'state_machine_name': 'delete_task_workflow',

        'workflow_replication_common_role_name': COMMON_PROPS['workflow_replication_common_role_name'],
        'replication_event_bus_name': COMMON_PROPS['replication_event_bus_name']
    },
    'delete_instance': {
        'state_machine_name': 'delete_instance_workflow',
        
        'workflow_replication_common_role_name': COMMON_PROPS['workflow_replication_common_role_name'],
        'replication_event_bus_name': COMMON_PROPS['replication_event_bus_name']
    }
}