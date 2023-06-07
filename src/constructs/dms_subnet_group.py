from aws_cdk import (
    aws_dms as dms
)

from constructs import Construct

class DmsSubnetGroupConstruct(Construct):
    """ Class to represent a DMS Subnet Group"""

    def __init__(self, scope: Construct, construct_id: str, subnet_group_props: dict, **kwargs) -> None:
        """ Class Constructor. Will create a DMS subnet group based on properties specified as parameter
        
        Parameters
        ----------
        subnet_group_props : dict
            dict with required properties for subnet group creation.
            For more details check config/subnet_groups_config.py documentation and examples.
        """

        super().__init__(scope, construct_id, **kwargs)
        
        endpoint = dms.CfnReplicationSubnetGroup(
            scope= self, 
            id= subnet_group_props['id'],
            replication_subnet_group_identifier= subnet_group_props['id'],
            replication_subnet_group_description= subnet_group_props['description'],
            subnet_ids= subnet_group_props['subnet_ids']
        )

