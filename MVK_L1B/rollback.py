import shutil
import os

class RollbackEngine:
    def rollback(self, stack):
        for op in reversed(stack):
            src = op["source"]
            dst = op["destination"]

            if os.path.exists(src):
                shutil.move(src, dst)
