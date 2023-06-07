from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_dms as dms,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    aws_events as events
)

from constructs import Construct

class ReplicationCommonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, common_props: dict, **kwargs) -> None:
        
        super().__init__(scope, construct_id, **kwargs)

        env = kwargs['env']

        # ---------------- SNS ------------------------
        notifications_topic = sns.Topic(
            scope= self, 
            id= 'notifications_topic',
            topic_name= common_props['notifications_topic_name']
        )

        notification_emails = common_props['notification_emails']
        for email in notification_emails:
            notifications_topic.add_subscription(
                sns_subscriptions.EmailSubscription(email)
            )

        # ---------------- S3 ------------------------
        artifact_bucket= s3.Bucket(
            scope= self,
            id= 'artifact-bucket',
            bucket_name= common_props['artifact_bucket_name'],
            encryption= s3.BucketEncryption.S3_MANAGED,
            enforce_ssl= True,
            auto_delete_objects= True,
            removal_policy= RemovalPolicy.DESTROY
        )
        
        # ---------------- IAM for DMS ------------------------
        if ('dms_cloudwatch_logs_role' in common_props) and (common_props['dms_cloudwatch_logs_role']):
            
            dms_cloudwatch_role = iam.Role(
                scope= self,
                id= 'dms-cloudwatch-logs-role',
                role_name= 'dms-cloudwatch-logs-role',
                assumed_by= iam.ServicePrincipal('dms.amazonaws.com')
            )

            dms_cloudwatch_role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonDMSCloudWatchLogsRole')
            )

        if ('dms_vpc_role' in common_props) and (common_props['dms_vpc_role']):
            
            dms_vpc_role = iam.Role(
                scope= self,
                id= 'dms-vpc-role',
                role_name= 'dms-vpc-role',
                assumed_by= iam.ServicePrincipal('dms.amazonaws.com')
            )

            dms_vpc_role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonDMSVPCManagementRole')
            )
        
        dms_secrets_common_role = iam.Role(
            scope= self,
            id= 'dms-secrets-common-role',
            role_name= common_props['dms_secrets_common_role_name'],
            assumed_by= iam.ServicePrincipal(f'dms.{env.region}.amazonaws.com')
        )

        dms_secrets_common_policy = iam.ManagedPolicy(
            scope= self,
            id= 'dms-secrets-common-policy',
            managed_policy_name= 'dms-secrets-common-policy',
            roles= [dms_secrets_common_role],
            statements= [
                iam.PolicyStatement(
                    actions=['secretsmanager:GetSecretValue'],
                    resources=[f'arn:aws:secretsmanager:{env.region}:{env.account}:secret:*']
                ),
                iam.PolicyStatement(
                    actions=['kms:Decrypt', 'kms:DescribeKey'],
                    resources=[f'arn:aws:kms:{env.region}:{env.account}:key/', f'arn:aws:kms:{env.region}:{env.account}:alias/']
                )
            ]
        )
        
        # ---------------- IAM for EVENTBRIDGE ------------------------
        eventbridge_common_role = iam.Role(
            scope= self, 
            id= 'eventbridge-common-role',
            role_name= common_props['eventbridge_replication_common_role_name'],
            assumed_by= iam.ServicePrincipal('events.amazonaws.com')
        )

        eventbridge_common_policy = iam.ManagedPolicy(
            scope= self,
            id= 'eventbridge-common-policy',
            managed_policy_name= 'eventbridge-common-policy',
            roles= [eventbridge_common_role],
            statements= [
                iam.PolicyStatement(
                    actions=['states:StartExecution'],
                    resources=[f'arn:aws:states:{env.region}:{env.account}:stateMachine:*']
                ),
                iam.PolicyStatement(
                    actions=['sns:Publish', 'sns:GetTopicAttributes'],
                    resources=[f'arn:aws:sns:{env.region}:{env.account}:*']
                ),
                iam.PolicyStatement(
                    actions=['lambda:InvokeFunction'],
                    resources=[f'arn:aws:lambda:{env.region}:{env.account}:*']
                )
            ]
        )

        # ----------------------- EVENTBRIDGE ---------------------------
        replication_event_bus = events.EventBus(
            scope= self,
            id= 'replication-event-bus',
            event_bus_name= common_props['replication_event_bus_name']
        )
        
        # ----------------------- DYNAMODB ---------------------------
        
        replication_checkpoint_table = dynamodb.Table(
            scope= self, 
            id= 'replication-checkpoints-table',
            table_name= common_props['replication_checkpoints_table_name'],
            partition_key= dynamodb.Attribute(
                name= 'job_checkpoint_name', 
                type= dynamodb.AttributeType.STRING
            ),
            sort_key= dynamodb.Attribute(
                name= 'job_start',
                type= dynamodb.AttributeType.STRING
            ),
            billing_mode= dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy= RemovalPolicy.DESTROY
        )

        replication_metrics_table = dynamodb.Table(
            scope= self, 
            id= 'replication-metrics-table',
            table_name= common_props['replication_metrics_table_name'],
            partition_key= dynamodb.Attribute(
                name= 'job_checkpoint_name', 
                type= dynamodb.AttributeType.STRING
            ),
            sort_key= dynamodb.Attribute(
                name= 'job_start',
                type= dynamodb.AttributeType.STRING
            ),
            billing_mode= dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy= RemovalPolicy.DESTROY
        )

        replication_jobs_table = dynamodb.Table(
            scope= self, 
            id= 'replication-jobs-table',
            table_name= common_props['replication_jobs_table_name'],
            partition_key= dynamodb.Attribute(
                name= 'job_name', 
                type= dynamodb.AttributeType.STRING
            ),
            billing_mode= dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy= RemovalPolicy.DESTROY
        )

        replication_instances_table = dynamodb.Table(
            scope= self, 
            id= 'replication-instances-table',
            table_name= common_props['replication_instances_table_name'],
            partition_key= dynamodb.Attribute(
                name= 'instance_name', 
                type= dynamodb.AttributeType.STRING
            ),
            billing_mode= dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy= RemovalPolicy.DESTROY
        )
        
        dynamodb_tables = [replication_checkpoint_table, replication_metrics_table, replication_jobs_table, replication_instances_table]

        # ----------------------- IAM for LAMBDA / STEP FUNCTIONS ---------------------------        
        lambda_common_role = iam.Role(
            scope= self,
            id= 'lambda-common-role',
            role_name= common_props['lambda_replication_common_role_name'],
            assumed_by= iam.ServicePrincipal('lambda.amazonaws.com')
        )

        lambda_common_policy = iam.ManagedPolicy(
            scope= self,
            id= 'lambda-common-policy',
            managed_policy_name= 'lambda-common-policy',
            roles= [lambda_common_role],
            statements= [
                iam.PolicyStatement(
                    actions=['s3:*'],
                    resources=[artifact_bucket.bucket_arn, artifact_bucket.arn_for_objects('*')]
                ),
                iam.PolicyStatement(
                    actions=['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
                    resources=[f'arn:aws:logs:{env.region}:{env.account}:*']
                ),
                iam.PolicyStatement(
                    actions=['dynamodb:Query', 'dynamodb:GetItem', 'dynamodb:putItem', 'dynamodb:UpdateItem', 'dynamodb:BatchWriteItem'],
                    resources=[dynamodb_table.table_arn for dynamodb_table in dynamodb_tables]
                ),
                iam.PolicyStatement(
                    actions=['dms:CreateReplicationTask', 'dms:StartReplicationTask', 'dms:DeleteReplicationTask', 'dms:CreateReplicationInstance', 'dms:DeleteReplicationInstance', 'dms:DescribeTableStatistics'],
                    resources=[f'arn:aws:dms:{env.region}:{env.account}:*']
                ),
                iam.PolicyStatement(
                    actions=['dms:DescribeReplicationTasks', 'dms:DescribeReplicationInstances', 'dms:DescribeEndpoints'],
                    resources=['*']
                ),
                iam.PolicyStatement(
                    actions=['ec2:ModifyNetworkInterfaceAttribute', 'ec2:CreateNetworkInterface', 'ec2:DeleteNetworkInterface'],
                    resources=[f'arn:aws:ec2:{env.region}:{env.account}:*']
                ),
                iam.PolicyStatement(
                    actions=['ec2:DescribeVpcs', 'ec2:DescribeNetworkInterfaces', 'ec2:DescribeInternetGateways', 'ec2:DescribeAvailabilityZones', 'ec2:DescribeSubnets', 'ec2:DescribeSecurityGroups'],
                    resources=['*']
                ),
                iam.PolicyStatement(
                    actions=['states:StartExecution', 'states:StopExecution', 'states:ListExecutions'],
                    resources=[f'arn:aws:states:{env.region}:{env.account}:stateMachine:*']
                ),
                iam.PolicyStatement(
                    actions=['events:Put*', 'events:Describe*'],
                    resources=[replication_event_bus.event_bus_arn, f'arn:aws:states:{env.region}:{env.account}:event-bus/default']
                ),
                iam.PolicyStatement(
                    actions=['secretsmanager:GetSecretValue'],
                    resources=[f'arn:aws:secretsmanager:{env.region}:{env.account}:secret:*']
                ),
                iam.PolicyStatement(
                    actions=['kms:Decrypt', 'kms:DescribeKey'],
                    resources=[f'arn:aws:kms:{env.region}:{env.account}:key/', f'arn:aws:kms:{env.region}:{env.account}:alias/']
                )
            ]
        )

        workflow_common_role = iam.Role(
            scope= self,
            id= 'workflow-common-role',
            role_name= common_props['workflow_replication_common_role_name'],
            assumed_by= iam.ServicePrincipal('states.amazonaws.com')
        )

        workflow_common_policy = iam.ManagedPolicy(
            scope= self,
            id= 'workflow-common-policy',
            managed_policy_name= 'workflow-common-policy',
            roles= [workflow_common_role],
            statements= [
                iam.PolicyStatement(
                    actions=['s3:*'],
                    resources=[artifact_bucket.bucket_arn, artifact_bucket.arn_for_objects('*')]
                ),
                iam.PolicyStatement(
                    actions=['states:StartExecution'],
                    resources=[f'arn:aws:states:{env.region}:{env.account}:stateMachine:*']
                ),
                iam.PolicyStatement(
                    actions=['sns:Publish'],
                    resources=[f'arn:aws:sns:{env.region}:{env.account}:*']
                ),
                iam.PolicyStatement(
                    actions=['lambda:InvokeFunction'],
                    resources=[f'arn:aws:lambda:{env.region}:{env.account}:*']
                ),
                iam.PolicyStatement(
                    actions=['ec2:DescribeVpcs', 'ec2:DescribeNetworkInterfaces', 'ec2:DescribeInternetGateways', 'ec2:DescribeAvailabilityZones', 'ec2:DescribeSubnets', 'ec2:DescribeSecurityGroups', 'ec2:ModifyNetworkInterfaceAttribute', 'ec2:CreateNetworkInterface', 'ec2:DeleteNetworkInterface'],
                    resources=[f'arn:aws:ec2:{env.region}:{env.account}:*']
                ),
                iam.PolicyStatement(
                    actions=['dms:CreateReplicationTask', 'dms:StartReplicationTask', 'dms:DeleteReplicationTask', 'dms:CreateReplicationInstance', 'dms:DeleteReplicationInstance'],
                    resources=[f'arn:aws:dms:{env.region}:{env.account}:*']
                ),
                iam.PolicyStatement(
                    actions=['dms:DescribeReplicationTasks', 'dms:DescribeReplicationInstances', 'dms:DescribeEndpoints'],
                    resources=['*']
                ),
                iam.PolicyStatement(
                    actions=['dynamodb:Query', 'dynamodb:GetItem','dynamodb:putItem', 'dynamodb:UpdateItem', 'dynamodb:BatchWriteItem'],
                    resources=[dynamodb_table.table_arn for dynamodb_table in dynamodb_tables]
                ),
                iam.PolicyStatement(
                    actions=['events:Put*', 'events:Describe*'],
                    resources=[replication_event_bus.event_bus_arn, f'arn:aws:states:{env.region}:{env.account}:event-bus/default']
                )
            ]
        )


        



