# Global-Config
LOG = False  # Is debugging enabled?

# Admin-Config
WRITE_PLAN = "logs/plan.log"
LOG_THRESHOLDS = "logs/thresholds_X.log" # X will be the number of the pid
LOG_THRESHOLDS_PURE = "logs/thresholds_pure_X.log"
TESTING = False

# Task-Config
task_sigma = 0.25  # sigma for normal distribution for calculating real lenght of tasks

# ProcessRunner-Config
COST_CONTEXT_SWITCH = None
IPS = 1000 # was 4000000000
HZ = 10 # should be 250
INS_PER_TICK = int(IPS/HZ)

RESCHEDULE_TIME = IPS / 20
LOAD = 1  # systemload

# Plan-Config
JUST_GENERATE_PLAN = False
MAX_BUFF_USAGE = 0.5
DEADLINE = 1.1  # total time * DEADLINE = Time to be finished
FREE_TIME = 10 #  Percentage of the plan that is not assigned
NUMBER_PROCESSES = 3
TASK_MIN_LEN = INS_PER_TICK
TASK_MAX_LEN = INS_PER_TICK * 1000
PROCESS_MIN_LEN = 10
PROCESS_MAX_LEN = 10
BUFFER_MIN = 2
BUFFER_MAX = 10

# Threshold-Config
# t1
MAX_TICKS_OFF = 20
MIN_TICKS_OFF = 2
PREEMPTION_LIMIT = MAX_TICKS_OFF * INS_PER_TICK
NO_PREEMPTION = MIN_TICKS_OFF * INS_PER_TICK
SIGMA_T1 = 1.3
# t2
RELAX = 1
STRESS = 1
CAP_LATENESS = 1.5
assert SIGMA_T1 < CAP_LATENESS
CONSUMABLE_BUFFER = 0.5
SPACER_CONSTANT = 2
