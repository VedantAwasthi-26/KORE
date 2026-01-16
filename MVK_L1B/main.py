import json
from transaction import TransactionController

MVK_ROOT = r"C:\Users\Vedant\Desktop\MVK_ROOT_TEST"
AUDIT_LOG = "audit_log.jsonl"

if __name__ == "__main__":
    with open("plan.json", "r") as f:
        plan = json.load(f)

    controller = TransactionController(
        mvk_root=MVK_ROOT,
        audit_log_path=AUDIT_LOG
    )

    controller.execute_plan(plan)
