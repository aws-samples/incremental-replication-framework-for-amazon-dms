from aws_cdk import (
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as event_targets,
    aws_stepfunctions as stepfunctions
)

from constructs import Construct

class JobFlowConstruct(Construct):
    """ Class to represent the Job Flow (job workflow sequence) that will be triggered when job is executed
    Note that resources will choreograph (coordinate) the execution of each independent workflow (state machine) following a sequence.
    Resources include eventbridge rules and targets.
    """

    def __init__(self, scope: Construct, construct_id: str, jobs_flow_props: dict, **kwargs) -> None:
        """ Class Constructor. Will create a Job Flow (job workflow sequence) based on properties specified as parameter
        Events include: 1/ cron event rule / target in case a workflow should start on a schedule. 
        2/ finish event rule that will trigger whenever tge workflows finishes successfully
        3/ target on previous workflow finish rule so that new workflow is executed when successfully finished. 
        This target will apply only if there is a previous workflow within the sequence and if the workflow is not cron based.
        
        Parameters
        ----------
        jobs_flow_props : dict
            dict with required properties for Job Flow (job workflow sequence) creation.
            For more details check config/job_instances_config.py documentation and examples.
        """

        super().__init__(scope, construct_id, **kwargs)
        
        eventbridge_common_role_name = jobs_flow_props['eventbridge_replication_common_role_name']
        eventbridge_common_role = iam.Role.from_role_name(
            scope= self,
            id= 'eventbridge-common-role',
            role_name= eventbridge_common_role_name
        )

        replication_event_bus_name = jobs_flow_props['replication_event_bus_name']
        replication_event_bus = events.EventBus.from_event_bus_name(
            scope= self,
            id= 'replication-event-bus',
            event_bus_name= replication_event_bus_name
        )

        job_step_rules = []
        job_name = jobs_flow_props['job_name']
        instance_name = jobs_flow_props['instance_name']
        job_steps_details = jobs_flow_props['job_steps_details']
        
        for index, step_props in enumerate(job_steps_details):
            step_state_machine = self.__get_state_machine(index, step_props)
            
            step_cron = step_props['cron'] if 'cron' in step_props else None
            if step_cron:
                step_cron_rule = self.__create_step_cron_rule(index, job_name, instance_name, step_props, step_state_machine, eventbridge_common_role)
                job_step_rules.append(step_cron_rule)
            else:
                step_first = False if index > 0 else True
                if not step_first:
                    previous_step_finish_rule = job_step_rules.pop(-1)
                    self.__create_step_finish_target(step_state_machine, previous_step_finish_rule, eventbridge_common_role)
                    job_step_rules.append(previous_step_finish_rule)

            step_finish_rule = self.__create_step_finish_rule(index, job_name, step_props, replication_event_bus)
            job_step_rules.append(step_finish_rule)
 
    def __get_state_machine(self, index, step_props):
        """Helper class private method to retrieve state machine (workflow) to be referenced on targets """
        
        state_machine_name = step_props['state_machine_name']
        state_machine = stepfunctions.StateMachine.from_state_machine_name(
            scope=self,
            id= f'state_machine_{index:02d}',
            state_machine_name=state_machine_name
        )

        return state_machine
    
    def __create_step_cron_rule(self, index, job_name, instance_name, step_props, state_machine, eventbridge_common_role):
        """Helper class private method to create a cron rule in EventBridge and assign the specified state machine as target """

        step_enabled = step_props['enabled'] if 'enabled' in step_props else True
        step_cron = step_props['cron']
        step_cron_rule = events.Rule(
            scope= self,
            id= f'job_step_{index:02d}_cron_rule',
            rule_name= f'{job_name}-step-{index:02d}-cron-rule',
            enabled=step_enabled,
            schedule=events.Schedule.cron(**step_cron)
        )
        
        step_cron_rule_target = event_targets.SfnStateMachine(
            machine=state_machine,
            role=eventbridge_common_role,
            input=events.RuleTargetInput.from_object(
                {
                    'InstanceName': instance_name,
                    'JobName': job_name
                }
            )
        )

        step_cron_rule.add_target(step_cron_rule_target)

        return step_cron_rule
    
    def __create_step_finish_rule(self, index, job_name, step_props, replication_event_bus):
        """Helper class private method to create a finish (custom) rule in EventBridge """

        step_enabled = step_props['enabled'] if 'enabled' in step_props else True
        step_finish_rule = events.Rule(
            scope= self,
            id= f'job_step_{index:02d}_finish_rule',
            rule_name= f'{job_name}-step-{index:02d}-finish-rule',
            event_bus=replication_event_bus,
            enabled=step_enabled,
            event_pattern=events.EventPattern(
                source=['custom.replication'],
                detail={
                    'WorkflowName': [step_props['state_machine_name']],
                    'WorkflowStatus': ['SUCCEEDED'],
                    'WorkflowOutput': {
                        'JobName': [job_name]
                    }
                }
            )
        )

        return step_finish_rule
    
    def __create_step_finish_target(self, state_machine, step_finish_rule, eventbridge_common_role):
        """Helper class private method to create a target pointing to the specified state machine in the specified EventBridge rule """

        step_finish_target = event_targets.SfnStateMachine(
            machine=state_machine,
            role=eventbridge_common_role,
            input=events.RuleTargetInput.from_event_path('$.detail.WorkflowOutput')
        )

        step_finish_rule.add_target(step_finish_target)

        return step_finish_rule
        
        
