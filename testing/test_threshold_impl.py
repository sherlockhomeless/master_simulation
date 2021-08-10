import unittest
from plan import Plan
from process_runner import ProcessRunner

class TestThreshold(unittest.TestCase):
    def setUp(self) -> None:
        self.p: Plan = Plan.read_plan_from_file("testing/plan.log")
        self.pr: ProcessRunner = ProcessRunner(p)

    def test_t1(self):
        pass
    def test_t2(self):
        pass
    def test_tm2(self):
        pass


