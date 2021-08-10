

class InstructionTracker:
    def __init__(self):
        self.instructions_task = 0
        self.instructions_slot = 0

    def run_instructions(self, ins: int):
        self.instructions_task += ins
        self.instructions_slot += ins

    def run_instructions_slot(self, ins: int):
        self.instructions_slot += ins

    def run_instructions_task(self, ins: int):
        self.instructions_task += ins

    def __repr__(self):
        return f'( t: {self.instructions_task}, s: {self.instructions_slot})'
