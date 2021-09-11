"""Collection of helpers."""

import os


def info(title):
    """Print info about the current process."""
    print(title)
    print("module name:", __name__)
    print("parent process:", os.getppid())
    print("process id:", os.getpid())
