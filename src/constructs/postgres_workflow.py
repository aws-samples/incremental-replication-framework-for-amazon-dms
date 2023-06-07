from aws_cdk import (
    Environment,
    Fn,
    aws_lambda as lambda_,
    aws_stepfunctions as stepfunctions,
    aws_iam as iam,
    aws_ec2 as ec2,
)

from os import path;
import json;

from constructs import Construct

class PostFullTaskWorkflowConstruct(Construct):
    """ Class to represent the workflow (state machine and belonging lambda functions) that will execute postgres specific tasks after DMS task completion (when full replication) 
    The workflow leverages a public PSYCOPG2 lambda layer. Use must be evaluated before deploying.
    """

    # Constant: Account of the public PSYCOPG2 lambda layer
    PSYCOPG2_ACCOUNT_NUMBER = '898466741470'

    # Constant: Version map per region for the public PSYCOPG2 lambda layer
    PSYCOPG2_DEFAULT_VERSION = 1
    PSYCOPG2_VERSION_BY_REGION = {
        'us-east-1': 2
    }
    
    def __init__(self, scope: Construct, construct_id: str, workflow_props: dict, env: Environment, **kwargs) -> None:
        """ Class Constructor. Will create a workflow (state machine and belonging lambdas) based on properties specified as parameter
        Lambdas include: 1/ for duplicating replication slot of source postgres database so that checkpoint is preserved with the database
        after task deletion (when it is a full load task)
        
        Parameters
        ----------
        workflow_props : dict
            dict with required properties for workflow creation.
            For more details check config/workflows_config.py documentation and examples.

        env: Environment
            Environment object with region and account details (available only on deployment time)
        """

        super().__init__(scope, construct_id, **kwargs)
        
        lambda_vpc = ec2.Vpc.from_vpc_attributes( 
            scope= self, 
            id= 'lambda_vpc',
            vpc_id= workflow_props['vpc_id'],
            availability_zones = Fn.get_azs(),
            private_subnet_ids = workflow_props['vpc_private_subnet_ids']
        )
        
        lambda_common_role = iam.Role.from_role_name(
            scope= self,
            id= 'lambda-common-role',
            role_name= workflow_props['lambda_replication_common_role_name']
        )

        lambda_security_group = ec2.SecurityGroup.from_security_group_id(
            scope= self, 
            id= 'lambda_security_group',
            security_group_id= workflow_props['vpc_security_group_id'],
        )
        
        lambda_layer_region = workflow_props['lambda_layer_region']
        psycopg2_layer_number = self.PSYCOPG2_VERSION_BY_REGION[lambda_layer_region] if lambda_layer_region in self.PSYCOPG2_VERSION_BY_REGION else self.PSYCOPG2_DEFAULT_VERSION
        psycopg2_layer_version_arn = f"arn:aws:lambda:{lambda_layer_region}:{self.PSYCOPG2_ACCOUNT_NUMBER}:layer:psycopg2-py38:{psycopg2_layer_number}"
        
        psycopg2_lamba_layer = lambda_.LayerVersion.from_layer_version_attributes(
            scope=self,
            id='psycopg2_lamba_layer',
            layer_version_arn= psycopg2_layer_version_arn
        )

        duplicate_replication_slot_lambda = lambda_.Function(
            scope= self,
            id= 'duplicate-replication-slot-lambda',
            function_name= 'duplicate_replication_slot_postgres',
            runtime= lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset(path.join('src/code/lambda', "duplicate_replication_slot_postgres")),
            handler= "duplicate_replication_slot_postgres.handler",
            layers= [psycopg2_lamba_layer],
            role= lambda_common_role,
            vpc= lambda_vpc,
            security_groups= [lambda_security_group]
        )

        notifications_topic_arn = f"arn:aws:sns:{env.region}:{env.account}:{workflow_props['notifications_topic_name']}"
        
        workflow_common_role = iam.Role.from_role_name(
            scope= self,
            id= 'workflow-common-role',
            role_name= workflow_props['workflow_replication_common_role_name']
        )
        
        post_full_task_postgres_state_machine_file = open('src/code/stepfunctions/post_full_task_postgres_workflow.asl.json')
        post_full_task_postgres_state_machine_definition = json.load(post_full_task_postgres_state_machine_file)
        
        post_full_task_postgres_state_machine = stepfunctions.CfnStateMachine(
            scope= self,
            id= 'post_full_task_postgres_state_machine',
            state_machine_name= workflow_props['state_machine_name'],
            definition= post_full_task_postgres_state_machine_definition,
            definition_substitutions= {
                'job-config-table': workflow_props['replication_jobs_table_name'],
                'duplicate_replication_slot_lambda_arn': duplicate_replication_slot_lambda.function_arn,
                'replication-event-bus-name': workflow_props['replication_event_bus_name'],
                'notifications-topic-arn': notifications_topic_arn
            },
            role_arn= workflow_common_role.role_arn
        )

