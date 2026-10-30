import unittest

from cofa_orchestrator.planner import ROLE_ORDER, build_plan
from cofa_orchestrator.spec import TaskSpec


def spec() -> TaskSpec:
    return TaskSpec.from_dict(
        {
            "topic": "Generic task",
            "requirements": ["Requirement A", "Requirement B"],
            "outputs": ["Output A"],
        }
    )


class PlannerTests(unittest.TestCase):
    def test_all_required_roles_are_present_in_order(self):
        plan = build_plan(spec())
        self.assertEqual(tuple(role["name"] for role in plan["roles"]), ROLE_ORDER)

    def test_requirements_receive_ids_and_owners(self):
        plan = build_plan(spec())
        self.assertEqual([item["id"] for item in plan["traceability"]], ["REQ-001", "REQ-002"])
        self.assertTrue(all(item["owner"] == "implementer" for item in plan["traceability"]))

    def test_single_allowed_model_applies_to_each_role(self):
        plan = build_plan(spec(), single_model="gpt-6-sol")
        self.assertEqual({role["suggested_model"] for role in plan["roles"]}, {"gpt-6-sol"})

    def test_plan_is_deterministic(self):
        self.assertEqual(build_plan(spec()), build_plan(spec()))


if __name__ == "__main__":
    unittest.main()

