import config


class PredictionFailureSignal:
    def __init__(self, process_id: int, transgression: float):
        assert type(transgression) is float
        self.process_id = process_id
        self.transgression = transgression # float that represents plan deviation in %, e.g. a task takes 10% longer => 1.1

    def __repr__(self):
        return f'Process {self.process_id} is more then {self.transgression}% early '


class JobScheduler:
    """
    A stub for the virtual resource system that reschedules plans after prediction failure signals
    """

    def __init__(self, plan):
        self.plan = plan
        self.reschedule_func = self.reschedule_simple  # set for different rescheduling mechanisms
        self.received_signals = []

    def reschedule(self, signal: PredictionFailureSignal):
        #for p in plan.Process:

        return self.reschedule_func(signal)

    @staticmethod
    def reschedule_simple(tasks, shrink=False) -> []:
        old = list([x.length_plan for x in tasks])
        stretch = config.PLAN_STRETCH_FACTOR if not shrink else -config.PLAN_STRETCH_FACTOR
        for t in tasks:
            plan_delta = int(t.length_plan_unchanged * stretch)
            t.length_plan += plan_delta
        return tasks

    def signal_t2(self, time_stamp, signaling_task, tasks):
        """
        Signals T2
        :param time_stamp: current time at which t2 was signaled
        :param signaling_task: Task which caused signal
        :param tasks: All upcoming tasks in the plan
        :return:
        """
        self.received_signals.append((time_stamp, signaling_task, "t2"))
        cur_task_pid = signaling_task.process_id
        all_tasks_to_stretch = list(filter(lambda task: task.process_id == cur_task_pid and task.task_finished is False,
                                           tasks))
        JobScheduler.reschedule_simple(all_tasks_to_stretch)

        config.logger.info(f'@{time_stamp}{signaling_task} caused a prediction failure signal')
        print(f'T2 signal received at {time_stamp} by {signaling_task}')

    def signal_t_m2(self, time_stamp, signaling_task, tasks):
        """
        Signals T-2
        :param time_stamp: current time at which t-2 was signaled
        :param signaling_task: Task which caused signal
        :return:
        """
        length_original = signaling_task.length_plan
        self.received_signals.append((time_stamp, signaling_task, "t_m2"))
        cur_task_pid = signaling_task.process_id
        all_tasks_to_stretch = list(filter(lambda task: task.process_id == cur_task_pid, tasks))
        JobScheduler.reschedule_simple(all_tasks_to_stretch, shrink=True)
        config.logger.info(f'@{time_stamp}{signaling_task} caused a prediction failure signal')
        assert length_original != tasks[0].length_plan
        return tasks

    def get_last_signal(self):
        try:
            return self.received_signals[-1]
        except IndexError:
            return None
