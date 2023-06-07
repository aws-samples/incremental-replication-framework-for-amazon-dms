from aws_cdk import (
    aws_dms as dms,
    aws_secretsmanager as secrets_manager,
    aws_iam as iam,
)

from constructs import Construct

class DmsEndpointConstruct(Construct):
    """ Class to represent a DMS Endpoint"""

    def __init__(self, scope: Construct, construct_id: str, endpoint_props: dict, **kwargs) -> None:
        """ Class Constructor. Will create a DMS endpoint based on properties specified as parameter
        
        Parameters
        ----------
        endpoint_props : dict
            dict with required properties for endpoint creation. This includes general and engine specific.
            For more details check config/endpoints_config.py documentation and examples.
        """
        
        super().__init__(scope, construct_id, **kwargs)

        dms_props = endpoint_props['endpoint']
        
        endpoint = dms.CfnEndpoint(
            scope= self, 
            id= dms_props["id"],
            
            endpoint_identifier = dms_props["id"],
            endpoint_type = dms_props["type"],
            engine_name = dms_props["engine"]
        )

        if 'db_name' in dms_props: endpoint.database_name = dms_props['db_name']
        
        if 'specific' in endpoint_props:
            specific_props = endpoint_props['specific']
            
            secret_name = specific_props.pop('secrets_manager_secret_arn_name')
            secret = secrets_manager.Secret.from_secret_name_v2(
                scope= self,
                id= f'{dms_props["id"]}-secret',
                secret_name= secret_name
            )
            specific_props['secrets_manager_secret_id'] = secret.secret_arn
            
            secret_role_name = specific_props.pop('secrets_manager_access_role_name')
            secret_role = iam.Role.from_role_name(
                scope= self,
                id= f'{dms_props["id"]}-secret-role',
                role_name= secret_role_name
            )
            specific_props['secrets_manager_access_role_arn'] = secret_role.role_arn
            
            if 'postgres' in dms_props["engine"]:
                endpoint.postgre_sql_settings=dms.CfnEndpoint.PostgreSqlSettingsProperty(**specific_props)
            
            elif ('aurora' in dms_props["engine"]) or ('mysql' in dms_props["engine"]): 
                endpoint.my_sql_settings=dms.CfnEndpoint.MySqlSettingsProperty(**specific_props)
