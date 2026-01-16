import os

FORBIDDEN = [
    r"C:\Windows",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\System32"
]

class SafetyGatekeeper:
    def __init__(self, mvk_root):
        self.mvk_root = os.path.realpath(mvk_root)

    def is_inside_root(self, path):
        return os.path.commonpath([path, self.mvk_root]) == self.mvk_root

    def check_plan(self, plan):
        for op in plan["operations"]:
            src = os.path.realpath(op["source"])
            dst = os.path.realpath(op["destination"])

            for bad in FORBIDDEN:
                if src.startswith(bad) or dst.startswith(bad):
                    raise RuntimeError("Forbidden system path detected.")

            if not self.is_inside_root(src) or not self.is_inside_root(dst):
                raise RuntimeError("Path escapes MVK root.")
