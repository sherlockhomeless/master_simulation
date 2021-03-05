import logging


# Global-Config
LOG = True  # Is debugging enabled?
LOG_TERM = False
logger = logging.getLogger()

base_folder_logging = "/home/ml/Dropbox/Master-Arbeit/code/threshold_simulation/logs/"
tick_log_path = base_folder_logging + "tick.log"
thresh_log_path = base_folder_logging + "per_tick_thresh_sum.log"
thresh_log_pure = base_folder_logging + "per_tick_thresh_pure.log"


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
WRITE_PLAN = "logs/plan.log"
LOG_THRESHOLDS = "logs/thresholds_X.log" # X will be the number of the pid
LOG_THRESHOLDS_PURE = "logs/thresholds_pure_X.log"
TESTING = False

# Task-Config
task_sigma = 0.25  # sigma for normal distribution for calculating real lenght of tasks

# --- ProcessRunner Basic Config ---
COST_CONTEXT_SWITCH = 0
IPS = 1000  # was 4000000000
HZ = 10  # should be 250
INS_PER_TICK = int(IPS/HZ)
RESCHEDULE_TIME = IPS / 20
LOAD = 1  # systemload

# --- Process Runner Behaviour Config ---
# Discussed in Thesis; Determines if unallocated time slots are allowed to be assigned to preempted tasks
INSERT_PREEMPTED_IN_FREE = False

# Plan-Config
JUST_GENERATE_PLAN = False
MAX_BUFF_USAGE = 0.5
DEADLINE = 1.1  # total time * DEADLINE = Time to be finished
FREE_TIME = 10 #  Percentage of the plan that is not assigned
NUMBER_PROCESSES = 3
TASK_MIN_LEN = INS_PER_TICK
TASK_MAX_LEN = INS_PER_TICK * 100
PROCESS_MIN_LEN = 90 # Minimum amount of tasks in process
PROCESS_MAX_LEN = 100 # Maximum amount of tasks in process
BUFFER_MIN = 2 # Minimal buffer size in Integer => 2 = 2%
BUFFER_MAX = 10 # Maximal buffer size in Integer => 10 = 10%

# Threshold-Config
# t1
MAX_TICKS_OFF = 20
MIN_TICKS_OFF = 2
PREEMPTION_LIMIT = MAX_TICKS_OFF * INS_PER_TICK  # Task gets interrupted above this limit
NO_PREEMPTION = MIN_TICKS_OFF * INS_PER_TICK  # Task does not get interrupted below this limit
SIGMA_T1 = 1.3

# t2
RELAX = 1
STRESS = 1
CAP_LATENESS = 1.5
assert SIGMA_T1 < CAP_LATENESS
ASSIGNABLE_BUFFER = 0.5
T2_SPACER = MAX_TICKS_OFF * INS_PER_TICK
T2_MAX_PREEMPTIONS = 5  # Max number a task is allowed to be preempted before Prediction Signal Failure


def update():
    """
    Updates Config Variables that are based on other values for testing
    :return:
    """
    global INS_PER_TICK
    global RESCHEDULE_TIME
    global TASK_MIN_LEN
    global TASK_MAX_LEN
    global PREEMPTION_LIMIT
    global NO_PREEMPTION
    global T2_SPACER
    INS_PER_TICK = int(IPS / HZ)
    RESCHEDULE_TIME = IPS / 20
    TASK_MIN_LEN = INS_PER_TICK
    TASK_MAX_LEN = INS_PER_TICK * 100
    PREEMPTION_LIMIT = MAX_TICKS_OFF * INS_PER_TICK  # Task gets interrupted above this limit
    NO_PREEMPTION = MIN_TICKS_OFF * INS_PER_TICK  # Task does not get interrupted below this limit
    T2_SPACER = MAX_TICKS_OFF * INS_PER_TICK

