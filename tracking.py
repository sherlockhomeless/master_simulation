

class Tracker:
    """
    Objects of this class keep track of the state of
    """
    def __init__(self, number_processes):
        self.overall_lateness = 0 # time the whole node is late or early, aka accumulated lateness
        self.process_lateness = [[] for x in range(number_processes)] # the individual lateness of a process
        self.stress = 0
