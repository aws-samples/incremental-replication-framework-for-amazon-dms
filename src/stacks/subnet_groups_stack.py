from aws_cdk import (
    Stack
)

from constructs import Construct
from src.constructs.dms_subnet_group import DmsSubnetGroupConstruct

class ReplicationSubnetGroupsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, subnet_groups_props: list, **kwargs) -> None:
        
        super().__init__(scope, construct_id, **kwargs)

        for subnet_group_construct_id, subnet_group_props in subnet_groups_props.items():

            DmsSubnetGroupConstruct(
                scope= self, 
                construct_id= subnet_group_construct_id,
                subnet_group_props= subnet_group_props
            )
