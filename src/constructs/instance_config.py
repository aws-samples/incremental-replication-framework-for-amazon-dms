from aws_cdk import (
    custom_resources as cr,
    aws_iam as iam
)

from constructs import Construct

class InstanceConfigConstruct(Construct):
    """ Class to represent a Instance Configuration. Not to be confused as a DMS instance, but the records in DynamoDB
    containing details of each DMS instance configuration
    """

    def __init__(self, scope: Construct, construct_id: str, instances_config_props: dict, **kwargs) -> None:
        """ Class Constructor. Will create a set of records in DynamoDB representing a instance configuration each.
        
        Parameters
        ----------
        instances_config_props : dict
            dict with required properties for instances configuration creation.
            For more details check config/job_instances_config.py documentation and examples.
        """

        super().__init__(scope, construct_id, **kwargs)
        
        lambda_common_role = iam.Role.from_role_name(
            scope= self,
            id= 'lambda-common-role',
            role_name= instances_config_props['lambda_replication_common_role_name']
        )
        
        replication_instances_table_name = instances_config_props['replication_instances_table_name']
        request_items = self.get_request_items(instances_config_props['replication_instances_records'])
        replication_instances_record_loader = cr.AwsCustomResource(
            scope= self,
            id= 'replication-instances-config-lambda',
            function_name= 'replication_instances_config_lambda',
            role= lambda_common_role,
            on_update= cr.AwsSdkCall(
                service= 'DynamoDB',
                action= 'batchWriteItem',
                parameters= {
                    'RequestItems': {
                        replication_instances_table_name: request_items
                    }
                },
                physical_resource_id= cr.PhysicalResourceId.of('replication-instances-config-lambda')
            )
        )

    def get_request_items(self, records):
        """ Function to format instance config records into a DynamoDB command-ready format """
        
        request_items = []
        for record in records:
            request_item = {
                'PutRequest': {
                    'Item': { attribute: {'S': value} for attribute, value in record.items() }
                }
            }
            request_items.append(request_item)
        
        return request_items
