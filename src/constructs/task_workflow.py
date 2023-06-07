from aws_cdk import (
    Environment,
    aws_lambda as lambda_,
    aws_stepfunctions as stepfunctions,
    aws_iam as iam
)

from os import path;
import json;

from constructs import Construct

class ExecuteTaskWorkflowConstruct(Construct):
    """ Class to represent the workflow (state machine and belonging lambda functions) that will create and run (until completion) a new DMS task """

    def __init__(self, scope: Construct, construct_id: str, workflow_props: dict, env: Environment, **kwargs) -> None:
        """ Class Constructor. Will create a workflow (state machine and belonging lambdas) based on properties specified as parameter
        Lambdas include: 1/ for task creation and 2/ for persisting checkpoint / metrics details in DynamoDB after DMS task completion
        
        Parameters
        ----------
        workflow_props : dict
            dict with required properties for workflow creation.
            For more details check config/workflows_config.py documentation and examples.

        env: Environment
            Environment object with region and account details (available only on deployment time)
        """

        super().__init__(scope, construct_id, **kwargs)
        
        lambda_common_role = iam.Role.from_role_name(
            scope= self,
            id= 'lambda-common-role',
            role_name= workflow_props['lambda_replication_common_role_name']
        )
        
        create_task_lambda = lambda_.Function(
            scope= self,
            id= 'create_task_lambda',
            function_name= 'create_task',
            runtime= lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset(path.join('src/code/lambda', "create_task")),
            handler= "create_task.handler",
            role= lambda_common_role,
            environment= {
                'REPLICATION_CHECKPOINTS_TABLE_NAME': workflow_props['replication_checkpoints_table_name'],
                'ARTIFACTS_BUCKET_NAME': workflow_props['artifact_bucket_name'],
                'REPLICATION_JOBS_CONFIG_PREFIX': workflow_props['replication_jobs_config_prefix']
            }
        )

        persist_task_outputs_lambda = lambda_.Function(
            scope= self,
            id= 'persist_task_outputs_lambda',
            function_name= 'persist_task_outputs',
            runtime= lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset(path.join('src/code/lambda', "persist_task_outputs")),
            handler= "persist_task_outputs.handler",
            role= lambda_common_role,
            environment= {
                'REPLICATION_CHECKPOINTS_TABLE_NAME': workflow_props['replication_checkpoints_table_name'],
                'REPLICATION_METRICS_TABLE_NAME': workflow_props['replication_metrics_table_name'],
            }
        )

        notifications_topic_arn = f"arn:aws:sns:{env.region}:{env.account}:{workflow_props['notifications_topic_name']}"
        
        workflow_common_role = iam.Role.from_role_name(
            scope= self,
            id= 'workflow-common-role',
            role_name= workflow_props['workflow_replication_common_role_name']
        )
        
        create_instance_state_machine_file = open('src/code/stepfunctions/execute_job_workflow.asl.json')
        create_instance_state_machine_definition = json.load(create_instance_state_machine_file)
        
        execute_task_state_machine = stepfunctions.CfnStateMachine(
            scope= self,
            id= 'execute_task_state_machine',
            state_machine_name= workflow_props['state_machine_name'],
            definition= create_instance_state_machine_definition,
            definition_substitutions= {
                'job-config-table': workflow_props['replication_jobs_table_name'],
                'create_replication_task_lambda_arn': create_task_lambda.function_arn,
                'persist_task_outputs_lambda_arn': persist_task_outputs_lambda.function_arn,
                'replication-event-bus-name': workflow_props['replication_event_bus_name'],
                'notifications-topic-arn': notifications_topic_arn
            },
            role_arn= workflow_common_role.role_arn
        )


class DeleteTaskWorkflowConstruct(Construct):
    """ Class to represent the workflow (state machine) that will delete an existing DMS task """

    def __init__(self, scope: Construct, construct_id: str, workflow_props: dict, **kwargs) -> None:
        """ Class Constructor. Will create a workflow (state machine) based on properties specified as parameter
        
        Parameters
        ----------
        workflow_props : dict
            dict with required properties for workflow creation.
            For more details check conifg/workflows_config.py documentation and examples.
        """

        super().__init__(scope, construct_id, **kwargs)

        workflow_common_role = iam.Role.from_role_name(
            scope= self,
            id= 'workflow-common-role',
            role_name= workflow_props['workflow_replication_common_role_name']
        )
        
        delete_task_state_machine_file = open('src/code/stepfunctions/delete_task_workflow.asl.json')
        delete_task_state_machine_definition = json.load(delete_task_state_machine_file)
        
        delete_task_state_machine = stepfunctions.CfnStateMachine(
            scope= self,
            id= 'delete_task_state_machine',
            state_machine_name= workflow_props['state_machine_name'],
            definition= delete_task_state_machine_definition,
            definition_substitutions= {
                'replication-event-bus-name': workflow_props['replication_event_bus_name']
            },
            role_arn= workflow_common_role.role_arn
        )