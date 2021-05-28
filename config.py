import logging


# Global-Config
LOG: bool = True  # Is debugging enabled?
LOG_TERM: bool = False
logger = logging.getLogger()

base_folder_logging: str = "/home/ml/Dropbox/Master-Arbeit/code/threshold_simulation/logs/"
unified_log_path: str = base_folder_logging + "unified_tick.log"
tick_log_path: str = base_folder_logging + "tick.log"
thresh_log_path: str = base_folder_logging + "per_tick_thresh_sum.log"
thresh_log_pure: str = base_folder_logging + "per_tick_thresh_pure.log"


if LOG is True:
    LOG_FORMAT = '[%(module)s][%(funcName)s]-%(levelname)s: %(message)s '
    logging.basicConfig(filename="/home/ml/Dropbox/Master-Arbeit/code/threshold_simulation/logs/all.log",
                        level=logging.INFO,
                        format=LOG_FORMAT,
                        filemode='w')

else:
    logging.basicConfig(filename="/dev/null", level=logging.CRITICAL)
logger = logging.getLogger('all')


# Admin-Config
PROJECT_BASE: str = "/home/ml/Dropbox/Master-Arbeit/code/threshold_simulation"
WRITE_PLAN: str = "logs/plan.log"
LOG_THRESHOLDS: str = "logs/thresholds_X.log" # X will be the number of the pid
LOG_THRESHOLDS_PURE: str = "logs/thresholds_pure_X.log"
TESTING: bool = False
JUST_WRITE_PLAN: bool = False

# Task-Config
task_sigma: float = 0.15  # sigma for normal distribution for calculating real lenght of tasks

# --- ProcessRunner Basic Config ---
COST_CONTEXT_SWITCH: int = 0
IPS: int = 4000000000  # was 4000000000
HZ: int = 250  # should be 250
INS_PER_TICK: int = int(IPS/HZ)
RESCHEDULE_TIME: int = IPS * 10

# --- Process Runner Behaviour Config ---
# Discussed in Thesis; Determines if unallocated time slots are allowed to be assigned to preempted tasks
INSERT_PREEMPTED_IN_FREE: bool = False

# Plan-Config
MAX_BUFF_USAGE: float = 0.5
TASK_SIGMA: float = 10
DEADLINE: float = 1.1  # total time * DEADLINE = Time to be finished
FREE_TIME: float = 0.1  # Percentage of the plan that is not assigned
NUMBER_PROCESSES: int = 3
TASK_MIN_LEN: int = INS_PER_TICK
TASK_MAX_LEN: int = INS_PER_TICK * 100
PROCESS_MIN_LEN: int = 90  # Minimum amount of tasks in process
PROCESS_MAX_LEN: int = 100  # Maximum amount of tasks in process
BUFFER_MIN: float = 2  # Minimal buffer size in Integer => 2 = 2%
BUFFER_MAX: float = 10  # Maximal buffer size in Integer => 10 = 10%

# Threshold-Config
# t1
MAX_TICKS_OFF: int = 20
MIN_TICKS_OFF: int = 2
T1_MAX_VALUE: int = MAX_TICKS_OFF * INS_PER_TICK  # Task gets interrupted above this limit
NO_PREEMPTION: int = MIN_TICKS_OFF * INS_PER_TICK  # Task does not get interrupted below this limit
T1_SIGMA: float = 1.3

# t2
RELAX: int = 1
STRESS_PER_SIGNAL: int = 30 * HZ  # seconds until
ASSIGNABLE_BUFFER: float = 1
T2_MAX_TASK_LATENESS: float = 1.5
T2_SPACER: float = MAX_TICKS_OFF * INS_PER_TICK
T2_MAX_PREEMPTIONS: float = 5  # Max number a task is allowed to be preempted before Prediction Signal Failure
T2_NODE_LATENESS: float = 1.1
T2_MINIMUM_USABLE_BUFFER: float = 0.05  # Minimum of the available buffer that is usable
T2_PROCESS_MINIMUM = RESCHEDULE_TIME * 1.5

# Rescheduling
PLAN_STRETCH_FACTOR: float = 0.05  # factor to adjust all tasks or processes after a prediction failure signal


def update():
    """
    Updates Config Variables that are based on other values for testing
    :return:
    """
    global INS_PER_TICK
    global RESCHEDULE_TIME
    global TASK_MIN_LEN
    global TASK_MAX_LEN
    global T1_MAX_VALUE
    global NO_PREEMPTION
    global T2_SPACER
    INS_PER_TICK = int(IPS / HZ)
    RESCHEDULE_TIME = IPS / 20
    TASK_MIN_LEN = INS_PER_TICK
    TASK_MAX_LEN = INS_PER_TICK * 100
    T1_MAX_VALUE = MAX_TICKS_OFF * INS_PER_TICK  # Task gets interrupted above this limit
    NO_PREEMPTION = MIN_TICKS_OFF * INS_PER_TICK  # Task does not get interrupted below this limit
    T2_SPACER = MAX_TICKS_OFF * INS_PER_TICK

