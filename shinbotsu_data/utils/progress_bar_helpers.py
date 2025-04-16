import shutil
import sys
import time
from datetime import timedelta


class ProgressBar:
    def __init__(self, total: int, size: int = 20, prefix: str = ""):
        self.total = total
        self.size = size
        self.prefix = prefix
        self.empty_char = "▱"
        self.full_char = "▰"
        self.bar = self.empty_char * self.size
        self.start_time = time.time()

    def update_progress(self, step: int) -> None:
        percent = "{0:.1f}".format(100 * (step / float(self.total)))
        filled_length = int(self.size * step // self.total)
        self.bar = self.full_char * filled_length + self.empty_char * (
            self.size - filled_length
        )
        if step == 0:
            eta = "calculating..."
        else:
            elapsed_time = time.time() - self.start_time
            time_per_step = elapsed_time / step
            eta_seconds = time_per_step * (self.total - step)
            eta = str(timedelta(seconds=int(eta_seconds)))
        line = f"{self.prefix}|{self.bar}| {percent}% complete - ETA: {eta}".ljust(
            shutil.get_terminal_size().columns
        )
        sys.stdout.write("\r" + line)
        sys.stdout.flush()
        if step == self.total:
            print()
