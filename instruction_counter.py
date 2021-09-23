

class InstructionTracker:
    def __init__(self, instructions_planned=0, instructions_retired_slot=0,
                 instructions_retired_task=0, instructions_real=0):
        self.plan = instructions_planned
        self.real = instructions_real
        self.instructions_retired_slot = instructions_retired_slot
        self.instructions_retired_task = instructions_retired_task

    def retire_instructions_task(self, instructions: int):
        self.instructions_retired_task += instructions

    def retire_instructions_slot(self, instructions: int):
        self.instructions_retired_slot += instructions

    def has_finished(self) -> bool:
        return self.instructions_retired_task >= self.real

    def has_finished_early(self) -> bool:
        return self.has_finished() and self.instructions_retired_task < self.plan

    def is_late(self) -> bool:
        return self.instructions_retired_task > self.plan

    def get_lateness(self):
        if self.has_finished() or self.is_late():
            return self.instructions_retired_task - self.plan
        else:
            return 0

    def __repr__(self):
        return f'( plan: {self.plan}, real: {self.real},' \
               f' retired: {self.instructions_retired_task})'
