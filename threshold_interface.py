from threshold_impl import *
from typing import Callable


class Threshold:
    def __init__(self, compute_t1: Callable = None, check_t1: Callable = None, compute_t2_task: Callable = None,
                 check_t2_task: Callable = None, compute_t2_process: Callable = None, check_t2_process: Callable = None,
                 compute_t2_node: Callable = None, check_t2_node: Callable = None, compute_t2_preemptions: Callable = None,
                 check_t2_preemptions: Callable = None, compute_tm2_task: Callable = None, check_tm2_task: Callable = None,
                 compute_tm2_node: Callable = None, check_tm2_node: Callable = None):
        """
        This class is intended to act as an interface that allows to easily swap different implementations of threshold
        calculation and threshold checking. Python has afai no way of more concretely defining a function signature. For
        this reason the type of all parameter is just callable. The signature might also change for different implementations.
        Every calc*-function should return a number-value that represents the threshold value. Every check*-function
        returns a true if the threshold was transgressed and false if it wasn't
        If a Threshold should be disabled "lambda *a: False" can be inserted into the check*-function
        """

        self.compute_t1 = compute_t1
        self.check_t1 = check_t1
        self.compute_t2_task = compute_t2_task
        self.check_t2_task = check_t2_task
        self.compute_t2_process = compute_t2_process
        self.check_t2_process = check_t2_process
        self.compute_t2_node = compute_t2_node
        self.check_t2_node = check_t2_node
        self.compute_t2_preemptions = compute_t2_preemptions
        self.check_t2_preemptions = check_t2_preemptions
        self.compute_tm2_task = compute_tm2_task
        self.check_tm2_task = check_tm2_task
        self.compute_tm2_node = compute_tm2_node
        self.check_tm2_node = check_tm2_node


thresholder: Threshold = Threshold(compute_t1=calc_t1, check_t1=compare_t1, compute_t2_task=calc_t2_task,
                                   check_t2_task=check_t2_task, compute_t2_process=calc_t2_process,
                                   check_t2_process=check_t2_process, compute_t2_node=calc_t2_node, check_t2_node=check_t2_node,
                                   compute_t2_preemptions=lambda task: task.was_preempted,
                                   check_t2_preemptions=check_t2_preemptions, compute_tm2_task=
                                   calc_tm2_task, check_tm2_task=check_tm2_task, compute_tm2_node=calc_tm2_node,
                                   check_tm2_node=check_tm2_node)
