HEADER = "\033[95m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"


def yellow(msg: str) -> None:
    return f"{YELLOW}{msg}{ENDC}"


def red(msg: str) -> None:
    return f"{RED}{msg}{ENDC}"


def green(msg: str) -> None:
    return f"{GREEN}{msg}{ENDC}"


def blue(msg: str) -> None:
    return f"{BLUE}{msg}{ENDC}"


def pink(msg: str) -> None:
    return f"{HEADER}{msg}{ENDC}"


def underline(msg: str) -> None:
    return f"{UNDERLINE}{msg}{ENDC}"


def bold(msg: str) -> None:
    return f"{BOLD}{msg}{ENDC}"
