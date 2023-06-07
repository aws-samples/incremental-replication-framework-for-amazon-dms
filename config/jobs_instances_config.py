from config.common_config import COMMON_PROPS, VPC_PROPS
from config.subnet_groups_config import SUBNET_GROUPS_PROPS
from config.endpoints_config import ENDPOINTS_CONFIG
from config.workflows_config import WORKFLOW_PROPS

# --------------------- EXAMPLES -------------------------
POSTGRES_TO_MYSQL_JOBS_INSTANCES_PROPS = {
    'instances_config': {
        'replication_instances_records': [
            {
                'instance_name': 'replication-instance-01',
                'instance_type': 'dms.t2.small',
                'publicly_accessible': 'false',

                'subnet_group': SUBNET_GROUPS_PROPS['subnet_group_01']['id'],
                
                'security_group': VPC_PROPS['security_groups']['security_group_01'],
                'availability_zone': VPC_PROPS['availability_zones'][0]
            }
        ],

        'lambda_replication_common_role_name': COMMON_PROPS['lambda_replication_common_role_name'],
        'replication_instances_table_name': COMMON_PROPS['replication_instances_table_name']
    },
    'jobs_config': {
        'replication_jobs_records': [
            {
                'job_name': 'postgres-mysql-job-01-full',
                'job_checkpoint_name': 'postgres_to_mysql_job_01',
                'migration_type': 'full-load-and-cdc',

                'source_endpoint_id': ENDPOINTS_CONFIG['source_endpoint_01']['endpoint']['id'],
                'target_endpoint_id': ENDPOINTS_CONFIG['target_endpoint_01']['endpoint']['id']
            },
            {
                'job_name': 'postgres-mysql-job-01-incremental',
                'job_checkpoint_name': 'postgres_to_mysql_job_01',
                'migration_type': 'cdc',

                'source_endpoint_id': ENDPOINTS_CONFIG['source_endpoint_02']['endpoint']['id'],
                'target_endpoint_id': ENDPOINTS_CONFIG['target_endpoint_01']['endpoint']['id']
            }
        ],

        'artifact_bucket_name': COMMON_PROPS['artifact_bucket_name'],
        'replication_jobs_config_prefix': COMMON_PROPS['replication_jobs_config_prefix'],
        'lambda_replication_common_role_name': COMMON_PROPS['lambda_replication_common_role_name'],
        'replication_jobs_table_name': COMMON_PROPS['replication_jobs_table_name']
    },
    'jobs_flow_config': [
        {
            'job_name': 'postgres-mysql-job-01-full',
            'instance_name': 'replication-instance-01',
            'job_steps_details': [
                {
                    'state_machine_name': WORKFLOW_PROPS['create_instance']['state_machine_name'],
                    'enabled': True
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['execute_task']['state_machine_name'],
                    'enabled': True
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['post_full_task_postgres']['state_machine_name'],
                    'enabled': True
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['delete_task']['state_machine_name'],
                    'enabled': True
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['delete_instance']['state_machine_name'],
                    'enabled': True
                }
            ],

            'eventbridge_replication_common_role_name': COMMON_PROPS['eventbridge_replication_common_role_name'],
            'replication_event_bus_name' : COMMON_PROPS['replication_event_bus_name']
        },
        {
            'job_name': 'postgres-mysql-job-01-incremental',
            'instance_name': 'replication-instance-01',
            'job_steps_details': [
                {
                    'state_machine_name': WORKFLOW_PROPS['create_instance']['state_machine_name'],
                    'enabled': True,
                    'cron': {'hour': '13', 'minute': '0'}
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['execute_task']['state_machine_name'],
                    'enabled': True
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['delete_task']['state_machine_name'],
                    'enabled': True
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['delete_instance']['state_machine_name'],
                    'enabled': True
                }
            ],

            'eventbridge_replication_common_role_name': COMMON_PROPS['eventbridge_replication_common_role_name'],
            'replication_event_bus_name' : COMMON_PROPS['replication_event_bus_name']
        }
    ] 
}

MYSQL_TO_POSTGRES_JOBS_INSTANCES_PROPS = {
    'instances_config': {
        'replication_instances_records': [
            {
                'instance_name': 'replication-instance-01',
                'instance_type': 'dms.t2.small',
                'publicly_accessible': 'false',

                'subnet_group': SUBNET_GROUPS_PROPS['subnet_group_01']['id'],
                
                'security_group': VPC_PROPS['security_groups']['security_group_01'],
                'availability_zone': VPC_PROPS['availability_zones'][0]
            }
        ],

        'lambda_replication_common_role_name': COMMON_PROPS['lambda_replication_common_role_name'],
        'replication_instances_table_name': COMMON_PROPS['replication_instances_table_name']
    },
    'jobs_config': {
        'replication_jobs_records': [
            {
                'job_name': 'mysql-postgres-job-01-full',
                'job_checkpoint_name': 'mysql_to_postgres_job_01',
                'migration_type': 'full-load-and-cdc',

                'source_endpoint_id': ENDPOINTS_CONFIG['source_endpoint_01']['endpoint']['id'],
                'target_endpoint_id': ENDPOINTS_CONFIG['target_endpoint_01']['endpoint']['id']
            },
            {
                'job_name': 'mysql-postgres-job-01-incremental',
                'job_checkpoint_name': 'mysql_to_postgres_job_01',
                'migration_type': 'cdc',

                'source_endpoint_id': ENDPOINTS_CONFIG['source_endpoint_01']['endpoint']['id'],
                'target_endpoint_id': ENDPOINTS_CONFIG['target_endpoint_01']['endpoint']['id']
            }
        ],

        'artifact_bucket_name': COMMON_PROPS['artifact_bucket_name'],
        'replication_jobs_config_prefix': COMMON_PROPS['replication_jobs_config_prefix'],
        'lambda_replication_common_role_name': COMMON_PROPS['lambda_replication_common_role_name'],
        'replication_jobs_table_name': COMMON_PROPS['replication_jobs_table_name']
    },
    'jobs_flow_config': [
        {
            'job_name': 'mysql-postgres-job-01-full',
            'instance_name': 'replication-instance-01',
            'job_steps_details': [
                {
                    'state_machine_name': WORKFLOW_PROPS['create_instance']['state_machine_name'],
                    'enabled': True
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['execute_task']['state_machine_name'],
                    'enabled': True
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['delete_task']['state_machine_name'],
                    'enabled': True
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['delete_instance']['state_machine_name'],
                    'enabled': True
                }
            ],

            'eventbridge_replication_common_role_name': COMMON_PROPS['eventbridge_replication_common_role_name'],
            'replication_event_bus_name' : COMMON_PROPS['replication_event_bus_name']
        },
        {
            'job_name': 'mysql-postgres-job-01-incremental',
            'instance_name': 'replication-instance-01',
            'job_steps_details': [
                {
                    'state_machine_name': WORKFLOW_PROPS['create_instance']['state_machine_name'],
                    'enabled': True,
                    'cron': {'hour': '13', 'minute': '0'}
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['execute_task']['state_machine_name'],
                    'enabled': True
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['delete_task']['state_machine_name'],
                    'enabled': True
                },
                {
                    'state_machine_name': WORKFLOW_PROPS['delete_instance']['state_machine_name'],
                    'enabled': True
                }
            ],

            'eventbridge_replication_common_role_name': COMMON_PROPS['eventbridge_replication_common_role_name'],
            'replication_event_bus_name' : COMMON_PROPS['replication_event_bus_name']
        }
    ] 
}

# --------------------- IMPORTANT VARIABLE -------------------------
""" Dict representing the structure to define job and instance configuration properties. Root dictionary include the three core elements of the framework

1- 'instances_config' includes all instance configurations. This allows you to ramp-up different independent instances (with specific configurations) in parallel and distribute replication tasks between them.
All following an incremental approach; meaning that instances are transient so that tasks can be resumed without any underlying dependency on the original instance where it was executed. This also means that 
instance deployments will be single AZ as of now considering their short-lasting feature. Configurations defined here will be stored in DynamoDB table via a CDK managed lambda function on deployment. The properties of 
this section are:
    - 'lambda_replication_common_role_name': str. Representing the name of the role to be assigned to the lambda function that will store instance configuration records in the DynamoDB table.
    - 'replication_instances_table_name': str. Representing the name of the DynamoDB table where records are going to be stored.
    - 'replication_instances_records': list. Every dict in this list represent a DynamoDB record for an instance configuration. Properties include:
        - 'instance_name': str. Name of the instance. Will be used to identify instance on creation and map tasks to it. Should be unique.
        - 'instance_type': str. EC2 instance type for the instance.
        - 'publicly_accessible' str. If instance should be accessible or not. Possible values are 'true' or 'false'.
        - 'subnet_group': str. Id of the DMS subnet group where instance wil be deployed.
        - 'availability_zone': str. Name of the availability zone where the instance is going to be deployed.

2- 'jobs_config' includes all jobs configurations. This allows you to define replication tasks that will be executed on replication instances following a incremental approach and without any dependency on the
underlying instance. Incremental means that all full replication tasks should be configured to stop after full replication, and cdc tasks will be stopped so that only cdc changes up to task start time are replicated.
When a task successfully finishes; checkpoints and metrics will be persisted in DynamoDB so that task and underlying instance can be eliminated and tasks can be resumed from the point that it should. Configurations defined 
here will be stored in DynamoDB table via a CDK managed lambda function on deployment. Additionally, settings and mappings json files will be synced to specified S3 bucket and prefix, partitioned by job name.
The properties of this section are:
    - 'artifact_bucket_name': str. Representing the name of the bucket where settings and mapping files will be stored.
    - 'replication_jobs_config_prefix': str. Representing the prefix of the bucket where settings and mapping files will be stored, partitioned by job name.
    - 'lambda_replication_common_role_name': str. Representing the name of the role to be assigned to the lambda function that will store instance configuration records in the DynamoDB table.
    - 'replication_jobs_table_name': str. Representing the name of the DynamoDB table where records are going to be stored.
    - 'replication_jobs_records': list. Every dict in this list represent a DynamoDB record for a job configuration. Properties include:
        - 'job_name': str. Name of the job. Will be used to identify replication task on creation and refer to it on execution. Should be unique.
        - 'job_checkpoint_name': str. Name of the checkpoint that the job will update. Should be unique. Note that full and cdc jobs of the same source objects should share the same 'job_checkpoint_name'.
        - 'migration_type' str. Type of replication task. Possible values are 'full-load-and-cdc' or 'cdc'.
        - 'source_endpoint_id': str. Id of the DMS source endpoint.
        - 'target_endpoint_id': str. Id of the DMS target endpoint.

3- 'jobs_flow_config' defines the workflow sequence for each job defined in 'jobs_config'. Workflows are decoupled to allow different execution patterns. For example, executing two or more tasks in the same instance before
instance deletion, or adding new custom workflows in between the sequence (as done with the 'post_full_task_postgres' workflow for instance). As of by now, definition only allows sequential execution of workflows, and definitions
are independent between jobs. Each element of the list is a dict that represent a workflow sequence configuration and should be associated to a job. 

Note that workflow choreography is based on an event-driven architecture leveraging EventBridge's event bus, rules and targets. Messages between workflows follow a standard in which output message of a successfully executed
workflow is sent as input message for the execution of the subsequent workflow.

The properties supported by each dict are:
    - 'job_name': str. Name of the job associated to the workflow sequence.
    - 'instance_name': str. Name of the instance where the job will be executed.
    - 'eventbridge_replication_common_role_name': str. Name of the eventbridge role to be used on event bus rules for executing actions and targets (subsequent state machines)
    - 'replication_event_bus_name': str. Name of the event bus where rules and targets will be deployed.
    - 'job_steps_details': list. Ordered list with sequence of workflow execution. Each element in the list is a dict representing the workflow to be executed. Properties of each element are:
        - 'state_machine_name': Name of the state machine to execute on current step.
        - 'enabled': bool. If finish rule of this workflow is enabled or not. When disabled means that no subsequent workflows will be executed when successfully finished.
        - 'cron': dict [OPTIONAL]. Representing if the workflow should be executed on a schedule instead of a previous workflow execution. Normally used for first step on CDC jobs. Possible keys of dict are described in 
        https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_events/CronOptions.html. When specified, and additional rule following cron definition will be created in default event bus. Current workflow will be defined as target
        and input messages will include 'JobName' and 'InstanceName'. Status of this event will be the same as defined in 'enabled'.

"""
JOBS_INSTANCES_PROPS = POSTGRES_TO_MYSQL_JOBS_INSTANCES_PROPS