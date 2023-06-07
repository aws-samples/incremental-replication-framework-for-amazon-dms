from aws_cdk import (
    Stack
)

from constructs import Construct
from src.constructs.instance_workflow import CreateInstanceWorkflowConstruct, DeleteInstanceWorkflowConstruct
from src.constructs.task_workflow import ExecuteTaskWorkflowConstruct, DeleteTaskWorkflowConstruct
from src.constructs.postgres_workflow import PostFullTaskWorkflowConstruct

class ReplicationWorkflowsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, workflows_props: list, **kwargs) -> None:
        
        super().__init__(scope, construct_id, **kwargs)

        create_instance_workflow_props = workflows_props['create_instance']
        execute_task_workflow_props = workflows_props['execute_task']
        post_full_task_postgres_workflow_props = workflows_props['post_full_task_postgres']
        delete_task_workflow_props = workflows_props['delete_task']
        delete_instance_workflow_props = workflows_props['delete_instance']

        CreateInstanceWorkflowConstruct(
            scope = self, 
            construct_id = 'CreateInstanceWorkflowConstruct',
            workflow_props = create_instance_workflow_props
        )

        ExecuteTaskWorkflowConstruct(
            scope = self, 
            construct_id = 'ExecuteTaskWorkflowConstruct',
            workflow_props = execute_task_workflow_props,
            env = kwargs.get('env')
        )

        PostFullTaskWorkflowConstruct(
            scope = self, 
            construct_id = 'PostFullTaskWorkflowConstruct',
            workflow_props = post_full_task_postgres_workflow_props,
            env = kwargs.get('env')
        )

        DeleteTaskWorkflowConstruct(
            scope = self, 
            construct_id = 'DeleteTaskWorkflowConstruct',
            workflow_props = delete_task_workflow_props
        )

        DeleteInstanceWorkflowConstruct(
            scope = self, 
            construct_id = 'DeleteInstanceWorkflowConstruct',
            workflow_props = delete_instance_workflow_props
        )
