#!/usr/bin/env python3
import os
import aws_cdk as cdk

from config.common_config import COMMON_PROPS
from config.endpoints_config import ENDPOINTS_CONFIG
from config.subnet_groups_config import SUBNET_GROUPS_PROPS
from config.workflows_config import WORKFLOW_PROPS
from config.jobs_instances_config import JOBS_INSTANCES_PROPS


from src.stacks.endpoints_stack import ReplicationEndpointsStack
from src.stacks.subnet_groups_stack import ReplicationSubnetGroupsStack
from src.stacks.common_stack import ReplicationCommonStack
from src.stacks.workflows_stack import ReplicationWorkflowsStack
from src.stacks.config_stack import ReplicationConfigStack

app = cdk.App()
account = cdk.Aws.ACCOUNT_ID
region = cdk.Aws.REGION

env =cdk.Environment(
    account= account,
    region= region
)

ReplicationCommonStack(
    scope= app,
    construct_id = "incremental-replication-common-stack",
    common_props = COMMON_PROPS,
    env = env
)

ReplicationEndpointsStack(
    scope = app, 
    construct_id = "incremental-replication-endpoints-stack",
    endpoints_props = ENDPOINTS_CONFIG,
    env = env
)

ReplicationSubnetGroupsStack(
    scope = app, 
    construct_id = "incremental-replication-subnet-groups-stack",
    subnet_groups_props = SUBNET_GROUPS_PROPS,
    env = env
)

ReplicationWorkflowsStack(
    scope= app,
    construct_id = "incremental-replication-workflows-stack",
    workflows_props = WORKFLOW_PROPS,
    env = env
)

ReplicationConfigStack(
    scope= app,
    construct_id = "incremental-replication-config-stack",
    config_props = JOBS_INSTANCES_PROPS,
    env = env
)

app.synth()