from aws_cdk import (
    Stack
)

from constructs import Construct
from src.constructs.instance_config import InstanceConfigConstruct
from src.constructs.job_config import JobConfigConstruct
from src.constructs.job_flow import JobFlowConstruct

class ReplicationConfigStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, config_props: list, **kwargs) -> None:
        
        super().__init__(scope, construct_id, **kwargs)

        instances_config_props = config_props['instances_config']
        InstanceConfigConstruct(
            scope = self, 
            construct_id = f'InstanceConfigConstruct',
            instances_config_props = instances_config_props
        )

        jobs_config_props = config_props['jobs_config']
        JobConfigConstruct(
            scope = self, 
            construct_id = f'JobConfigConstruct',
            jobs_config_props= jobs_config_props
        )

        jobs_flow_props = config_props['jobs_flow_config']
        for index, jobs_flow_props in enumerate(jobs_flow_props):
            JobFlowConstruct(
                scope = self, 
                construct_id = f'JobFlowConstruct{index:02d}',
                jobs_flow_props= jobs_flow_props
            )

