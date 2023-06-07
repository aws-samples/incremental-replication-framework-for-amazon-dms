from config.common_config import COMMON_PROPS

# --------------------- EXAMPLES -------------------------
POSTGRES_TO_MYSQL_ENDPOINTS_CONFIG = {
    'source_endpoint_01': {
        'endpoint': {
            'id': 'aurora-postgres-source-01-full',
            'type': 'source',
            'engine': 'aurora-postgresql',
            'db_name': 'postgresdb'
        },
        'specific': {
            'secrets_manager_secret_arn_name': '', # Include secret arn name
            'secrets_manager_access_role_name': COMMON_PROPS['dms_secrets_common_role_name']
        }
    },
    'source_endpoint_02':  {
        'endpoint': {
            'id': 'aurora-postgres-source-01-incremental',
            'type': 'source',
            'engine': 'aurora-postgresql',
            'db_name': 'postgresdb'
        },
        'specific': {
            'slot_name': 'postgres_to_mysql_job_01',
            'secrets_manager_secret_arn_name': '', # Include secret arn name
            'secrets_manager_access_role_name': COMMON_PROPS['dms_secrets_common_role_name']
        }
    },
    'target_endpoint_01': {
        'endpoint': {
            'id': 'aurora-mysql-target-01',
            'type': 'target',
            'engine': 'aurora',
        },
        'specific': {
            'secrets_manager_secret_arn_name': '',  # Include secret arn name
            'secrets_manager_access_role_name': COMMON_PROPS['dms_secrets_common_role_name']
        }
    }
}

MYSQL_TO_POSTGRES_ENDPOINTS_CONFIG = {
    'source_endpoint_01': {
        'endpoint': {
            'id': 'aurora-mysql-source-01',
            'type': 'source',
            'engine': 'aurora'
        },
        'specific': {
            'secrets_manager_secret_arn_name': '', # Include secret arn name
            'secrets_manager_access_role_name': COMMON_PROPS['dms_secrets_common_role_name']
        }
    },
    'target_endpoint_01': {
        'endpoint': {
            'id': 'aurora-postgres-target-01',
            'type': 'target',
            'engine': 'aurora-postgresql',
            'db_name': 'postgresdb'
        },
        'specific': {
            'secrets_manager_secret_arn_name': '', # Include secret arn name
            'secrets_manager_access_role_name': COMMON_PROPS['dms_secrets_common_role_name']
        }
    }
}

# --------------------- MAIN VARIABLE -------------------------
""" Dict representing the structure to define endpoints' properties. Every key value pair in the root
represents a single endpoint configuration. The key is the id that will be used from within the stack and the
value is a dict with the set of properties for that particular endpoint. 

Properties are grouped in to categories:
- 'endpoint' category is where common properties, independent of the db engine, are placed. This includes:
    - 'id': str. Representing the id of the DMS endpoint when created. This id is the one that will be used when
    referencing the endpoint from within any job execution
    - 'type': str. Representing whether the endpoint will connect to a 'source' or 'target' database.
    - 'engine': str. Representing the database engine type. Accepted values as of now include 'aurora' and 'aurora-postgres' only
    - 'db_name': str. Representing the name of the database you are going to connect to. Note that for postgres this represents the
    database name but in mysql it represents the schema name.

- 'specific' category is where engine specific properties are placed. As of by now only postgres and mysql are supported.
Specifically the following properties:
    - For postgres databases:
        - 'secrets_manager_access_role_name': str. As all connection to databases will be done through secrets manager. This property
        represents the name of the role that DMS will use to access that secret.
        - 'secrets_manager_secret_arn_name': str. As all connection to databases will be done through secrets manager. This property
        represents the name of the secret where connection details can be found. Note that this is the arn name, which means that
        it is not the console name, but the last element of the arn which has random characters included on top of the console name,
        when deployed.
        - 'slot_name': str. The name of the replication slot to be used by cdc tasks. Note that this means that it is good idea to deploy
        two endpoints when using postgres as a source; the reason being, one will be used on full replication task where a new slot will
        be created in the process, and the second will be used for cdc task after duplicating the slot created by the full task and referencing
        the slot name in the endpoint configuration. As you may see, the slot name that the framework uses is the checkpoint name of the job.

    - For mysql databases:
        - 'secrets_manager_access_role_name': str. As all connection to databases will be done through secrets manager. This property
        represents the name of the role that DMS will use to access that secret.
        - 'secrets_manager_secret_arn_name': str. As all connection to databases will be done through secrets manager. This property
        represents the name of the secret where connection details can be found. Note that this is the arn name, which means that
        it is not the console name, but the last element of the arn which has random characters included on top of the console name,
        when deployed.

Other properties from CDK could be used here as well, but haven't been tested yet. One example is when forcing the use of pg_logical plugin for
postgres sources. CDK docs: https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_dms/CfnEndpoint.html
"""
ENDPOINTS_CONFIG = POSTGRES_TO_MYSQL_ENDPOINTS_CONFIG