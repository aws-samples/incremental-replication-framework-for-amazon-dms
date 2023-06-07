from aws_cdk import (
    aws_stepfunctions as stepfunctions,
    aws_iam as iam
)

from os import path;
import json;

from constructs import Construct

class CreateInstanceWorkflowConstruct(Construct):
    """ Class to represent the workflow (state machine) that will create a new DMS instance """

    def __init__(self, scope: Construct, construct_id: str, workflow_props: dict, **kwargs) -> None:
        """ Class Constructor. Will create a workflow (state machine) based on properties specified as parameter
        
        Parameters
        ----------
        workflow_props : dict
            dict with required properties for workflow creation.
            For more details check config/workflows_config.py documentation and examples.
        """

        super().__init__(scope, construct_id, **kwargs)

        workflow_common_role = iam.Role.from_role_name(
            scope= self,
            id= 'workflow-common-role',
            role_name= workflow_props['workflow_replication_common_role_name']
        )
        
        create_instance_state_machine_file = open('src/code/stepfunctions/create_instance_workflow.asl.json')
        create_instance_state_machine_definition = json.load(create_instance_state_machine_file)
        
        create_instance_state_machine = stepfunctions.CfnStateMachine(
            scope= self,
            id= 'create_instance_state_machine',
            state_machine_name= workflow_props['state_machine_name'],
            definition= create_instance_state_machine_definition,
            definition_substitutions= {
                'instance-config-table': workflow_props['replication_instances_table_name'],
                'replication-event-bus-name': workflow_props['replication_event_bus_name']
            },
            role_arn= workflow_common_role.role_arn
        )

class DeleteInstanceWorkflowConstruct(Construct):
    """ Class to represent the workflow (state machine) that will delete an existing DMS instance """

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
        
        delete_instance_state_machine_file = open('src/code/stepfunctions/delete_instance_workflow.asl.json')
        delete_instance_state_machine_definition = json.load(delete_instance_state_machine_file)
        
        delete_instance_state_machine = stepfunctions.CfnStateMachine(
            scope= self,
            id= 'delete_instance_state_machine',
            state_machine_name= workflow_props['state_machine_name'],
            definition= delete_instance_state_machine_definition,
            definition_substitutions= {
                'replication-event-bus-name': workflow_props['replication_event_bus_name']
            },
            role_arn= workflow_common_role.role_arn
        )
