import config
from task import Task


class SimLogger:
    log_enabled = config.LOG
    num_processes = config.NUMBER_PROCESSES
    assert num_processes < 10
    log_thresholds = config.LOG_THRESHOLDS # logs the instructions + extra grans per threshold
    log_thresholds_pure = config.LOG_THRESHOLDS_PURE # logs only extra grants per thresh
    threshold_logger, threshold_logger_pure = [], []
    for i in range(num_processes):
        full_path = log_thresholds.replace('X', str(i))
        full_path_pure = log_thresholds_pure.replace('X', str(i))
        threshold_logger.append(open(full_path, 'w'))
        threshold_logger_pure.append(open(full_path_pure, 'w'))

    @staticmethod
    def log_threshold_per_task(task: Task, thresholds: (int,int,int)):
        assert type(task) is Task
        assert len(thresholds) == 3

        tid, pid = task.task_id, task.process_id
        t1, t2, t_m2 = thresholds[0], thresholds[1], thresholds[2]
        SimLogger.threshold_logger.write(
                f'{tid} {t1} {t2} {t_m2}\n')

    @ staticmethod
    def log_thresh_per_task_pure(task:Task, thresholds:(int,int,int )):
        assert type(task) is Task
        assert len(thresholds) == 3
        tid, pid = task.task_id, task.process_id
        t1, t2, t_m2 = thresholds[0], thresholds[1], thresholds[2]
        SimLogger.threshold_logger_pure.write(
            f'{tid} {t1} {t2} {t_m2}\n')



