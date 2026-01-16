from .validator import PlanValidator
from .safety import SafetyGatekeeper
from .audit import AuditLogger
from .executor import Executor
from .rollback import RollbackEngine

class TransactionController:
    def __init__(self, mvk_root, audit_log_path):
        self.validator = PlanValidator(mvk_root)
        self.safety = SafetyGatekeeper(mvk_root)
        self.audit = AuditLogger(audit_log_path)
        self.executor = Executor(self.audit)
        self.rollback = RollbackEngine()

    def execute_plan(self, plan):
        print("🔍 Validating plan...")
        self.validator.validate(plan)
        self.safety.check_plan(plan)

        print("🧾 Preparing rollback data...")
        rollback_stack = []

        try:
            for idx, op in enumerate(plan["operations"]):
                self.audit.log(plan["plan_id"], idx, op, "PENDING")

                inverse = self.executor.execute(op)
                rollback_stack.append(inverse)

                self.audit.log(plan["plan_id"], idx, op, "DONE")

            print("✅ Transaction completed successfully.")

        except Exception as e:
            print("💥 FAILURE DETECTED. Rolling back...")
            self.rollback.rollback(rollback_stack)
            raise RuntimeError("Transaction failed and was rolled back.") from e
