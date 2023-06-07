from config.common_config import VPC_PROPS

""" Dict representing the structure to define subnet groups' properties. Every key value pair in the root
represents a single subnet group configuration. The key is the id that will be used from within the stack and the
value is a dict with the set of properties for that particular subnet group. 

Supported properties are:
    - 'id': str. Representing the id of the DMS subnet group when created. This id is the one that will be used when
    referencing the security group from within any job execution
    - 'description': str. Representing a description of the subnet group.
    - 'db_name': list. Representing a list of vpc subnet ids that will be covered by subnet group.
"""
SUBNET_GROUPS_PROPS = {
    'subnet_group_01': {
        'id': 'replication_subnet_group_01',
        'description': 'Replication subnet group for all replication jobs', 
        
        'subnet_ids': VPC_PROPS['private_subnets']
    }
}