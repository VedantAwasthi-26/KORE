import os

class PlanValidator:
    def __init__(self, mvk_root):
        self.mvk_root = os.path.realpath(mvk_root)

    def validate(self, plan):
        if plan.get("aborted"):
            raise ValueError("Plan is aborted.")

        required_keys = ["plan_id", "snapshot_id", "operations"]
        for k in required_keys:
            if k not in plan:
                raise ValueError("Invalid plan format.")

        seen_destinations = set()

        for op in plan["operations"]:
            src = os.path.realpath(op["source"])
            dst = os.path.realpath(op["destination"])

            if src == dst:
                raise ValueError("Source and destination are identical.")

            if dst in seen_destinations:
                raise ValueError("Two operations target same destination.")

            seen_destinations.add(dst)
