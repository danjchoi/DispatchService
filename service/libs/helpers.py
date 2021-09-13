"""Collection of helpers."""

import os
import random
import string


def info(title):
    """Print info about the current process."""
    return f"{title}, parent process: {os.getppid()}, process id: {os.getpid()}"


def rand_alphanumeric(length=8):
    """Return a random alphanumeric string of length l."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
