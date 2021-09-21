import logging

# --- ADMIN CONFIG VARIABLES ---
PROJECT_BASE: str = "/home/ml/Dropbox/Master-Arbeit/code/threshold_simulation"
WRITE_PLAN: str = "logs/plan.log"
LOG_THRESHOLDS: str = "logs/thresholds_X.log" # X will be the number of the pid
LOG_THRESHOLDS_PURE: str = "logs/thresholds_pure_X.log"
TESTING: bool = False
JUST_WRITE_PLAN: bool = False  # just writes a new plan to file

# Task-Config
task_sigma: float = 0.1  # sigma for normal distribution for calculating real length of tasks

# --- ProcessRunner Basic Config ---
COST_CONTEXT_SWITCH: int = 0
IPS: int = 1000000000  # was 4000000000
HZ: int = 100  # should be 250
INS_PER_TICK: int = int(IPS/HZ)
RESCHEDULE_TIME: int = IPS * 1

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
TASK_MAX_LEN: int = INS_PER_TICK * 50
PROCESS_MIN_LEN: int = 500  # Minimum amount of tasks in process
PROCESS_MAX_LEN: int = 750  # Maximum amount of tasks in process
BUFFER_MIN: float = 5  # Minimal buffer size in Integer => 2 = 2%
BUFFER_MAX: float = 20  # Maximal buffer size in Integer => 10 = 10%

# Threshold-Config
# t1
T1_MAX_TICKS_OFF: int = 10
T1_MIN_TICKS_OFF: int = 2
T1_MAX_VALUE: int = T1_MAX_TICKS_OFF * INS_PER_TICK  # Task gets interrupted above this limit
NO_PREEMPTION: int = T1_MIN_TICKS_OFF * INS_PER_TICK  # Task does not get interrupted below this limit
T1_SIGMA: float = 1.1

# t2
# t2_task
T2_SIGMA: float = 1.2
assert T2_SIGMA > T1_SIGMA
T2_SPACER_TICKS: int = int(T1_MAX_TICKS_OFF * 1.5)
T2_SPACER = T2_SPACER_TICKS * INS_PER_TICK
T2_MAX: int = (T1_MAX_TICKS_OFF * 5) * INS_PER_TICK

# t2_process
T2_STRESS_RESET: int = 30 * HZ
T2_STRESS_GAIN: int = int(0.25 * INS_PER_TICK)
T2_AVAILABLE_PLAN_BUFFER = 0.7
T2_CAPACITY_BUFFER = 1.1
ASSIGNABLE_BUFFER: float = 0.7
T2_PROCESS_MINIMUM = int(RESCHEDULE_TIME * 1.1)

# t2_node
T2_NODE_LATENESS: float = 1.1
T2_NODE_LOWER_BOUND: float = T2_PROCESS_MINIMUM * NUMBER_PROCESSES

# t2_preemptions
T2_MAX_PREEMPTIONS: float = 5  # Max number a task is allowed to be preempted before Prediction Signal Failure

# tm2
# tm2_task
TM2_SIGMA: float = 1 - (T2_SIGMA - 1)
TM2_TASK_SIGNALING_START: int = T2_SPACER * -1
TM2_TASK_SIGNALING_LIMIT: int = T2_MAX * -1

# tm2_node
TM2_NODE_EARLINESS_CAP: float = 1 - (T2_NODE_LATENESS - 1)
TM2_NODE_EARLINESS_EXTRA: float = 1.05
TM2_NODE_LOWER_BOUND: int = int((T2_NODE_LOWER_BOUND * TM2_NODE_EARLINESS_EXTRA) * -1)

# Rescheduling
PLAN_STRETCH_FACTOR: float = 0.05  # factor to adjust all tasks or processes after a prediction failure signal


# Global-Config
LOG: bool = True  # Is debugging enabled?
LOG_TERM: bool = False
logger = logging.getLogger()

base_folder_logging: str = PROJECT_BASE + "/logs/"
unified_log_path: str = base_folder_logging + "unified_tick.log"
tick_log_path: str = base_folder_logging + "tick.log"
thresh_log_path: str = base_folder_logging + "per_tick_thresh_sum.log"
thresh_log_pure: str = base_folder_logging + "per_tick_thresh_pure.log"


if LOG is True:
    LOG_FORMAT = '[%(module)s][%(funcName)s]-%(levelname)s: %(message)s '
    logging.basicConfig(filename= PROJECT_BASE + "/logs/all.log",
                        level=logging.INFO,
                        format=LOG_FORMAT,
                        filemode='w')

else:
    logging.basicConfig(filename="/dev/null", level=logging.CRITICAL)
logger = logging.getLogger('all')


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
    T1_MAX_VALUE = T1_MAX_TICKS_OFF * INS_PER_TICK  # Task gets interrupted above this limit
    NO_PREEMPTION = T1_MIN_TICKS_OFF * INS_PER_TICK  # Task does not get interrupted below this limit
    T2_SPACER = T1_MAX_TICKS_OFF * INS_PER_TICK


def set_test_config():
    """
    This function sets fixed values for the configuration variables to enable consistent behaviour for the unit tests
    :return:
    """
    global IPS
    global HZ
    global RESCHEDULE_TIME
    global T1_MAX_TICKS_OFF
    global T1_MIN_TICKS_OFF

    HZ = 100
    IPS = 10000
    RESCHEDULE_TIME = IPS * 10
    T1_MAX_TICKS_OFF = 20
    T1_MIN_TICKS_OFF = 2
    update()

