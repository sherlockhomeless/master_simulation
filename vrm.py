from plan import Plan


class PredictionFailure():
    def __init__(self, process_id: int, transgression: float):
        assert type(transgression) is float
        self.process_id = process_id
        self.transgression = transgression # float that represents plan deviation in %, e.g. a task takes 10% longer => 1.1

    def __repr__(self):
        return f'Process {self.process_id} is more then {self.transgression}% early '


class VRM:
    """
    A stub for the virtual resource system that reschedules plans after prediction failure signals
    """

    def __init__(self, plan: Plan):
        self.plan = plan
        self.reschedule_func = self.reschedule_simple # set for different rescheduling mechanisms

    def reschedule(self, signal: PredictionFailure) -> Plan:
        return self.reschedule_func(signal)

    def reschedule_simple(self, signal: PredictionFailure) -> Plan:
        print(f'Rescheduling plan')

        for task in self.plan:
            if signal.process_id == task.process_id:
                task.length_plan *= signal.transgression

        return self.plan
