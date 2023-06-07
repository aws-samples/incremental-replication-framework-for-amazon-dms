from aws_cdk import (
    custom_resources as cr,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy
)

from constructs import Construct

class JobConfigConstruct(Construct):
    """ Class to represent a Job Configuration. Not to be confused as a DMS task, but the records in DynamoDB
    containing details of each DMS task configuration (named Job in this framework)
    """

    def __init__(self, scope: Construct, construct_id: str, jobs_config_props: dict, **kwargs) -> None:
        """ Class Constructor. Will create a set of records in DynamoDB representing a job configuration each.
        
        Parameters
        ----------
        jobs_config_props : dict
            dict with required properties for jobs configuration creation.
            For more details check config/job_instances_config.py documentation and examples.
        """

        super().__init__(scope, construct_id, **kwargs)
        
        lambda_common_role_name = jobs_config_props['lambda_replication_common_role_name']
        lambda_common_role = iam.Role.from_role_name(
            scope= self,
            id= 'lambda-common-role',
            role_name= lambda_common_role_name
        )
        
        artifact_bucket_name = jobs_config_props['artifact_bucket_name']
        artifact_bucket = s3.Bucket.from_bucket_name(
            scope= self,
            id= 'artifact_bucket',
            bucket_name= artifact_bucket_name
        )

        replication_jobs_config_prefix = jobs_config_props['replication_jobs_config_prefix']
        replication_jobs_config_loader = s3_deploy.BucketDeployment(
            scope= self,
            id= 'replication-jobs-config-s3-lambda',
            role= lambda_common_role,
            destination_bucket= artifact_bucket,
            destination_key_prefix= replication_jobs_config_prefix,
            sources= [
                s3_deploy.Source.asset('src/code/dms')
            ],
            retain_on_delete= False
        )
        
        replication_jobs_table_name = jobs_config_props['replication_jobs_table_name']
        request_items = self.get_request_items(jobs_config_props['replication_jobs_records'])
        replication_jobs_record_loader = cr.AwsCustomResource(
            scope= self,
            id= 'replication-jobs-config-lambda',
            function_name= 'replication_jobs_config_lambda',
            role= lambda_common_role,
            on_update= cr.AwsSdkCall(
                service= 'DynamoDB',
                action= 'batchWriteItem',
                parameters= {
                    'RequestItems': {
                        replication_jobs_table_name: request_items
                    }
                },
                physical_resource_id= cr.PhysicalResourceId.of('replication-jobs-config-lambda')
            )
        )

    def get_request_items(self, records):
        """ Function to format job config records into a DynamoDB command-ready format """

        request_items = []
        for record in records:
            request_item = {
                'PutRequest': {
                    'Item': { attribute: {'S': value} for attribute, value in record.items() }
                }
            }
            request_items.append(request_item)
        
        return request_items
