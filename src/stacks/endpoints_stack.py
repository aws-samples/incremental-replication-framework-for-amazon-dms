from aws_cdk import (
    Stack
)

from constructs import Construct
from src.constructs.dms_endpoint import DmsEndpointConstruct

class ReplicationEndpointsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, endpoints_props: list, **kwargs) -> None:
        
        super().__init__(scope, construct_id, **kwargs)

        for endpoint_construct_id, endpoint_props in endpoints_props.items():

            DmsEndpointConstruct(
                scope = self, 
                construct_id = endpoint_construct_id,
                endpoint_props = endpoint_props
            )
