class AdvancedPrint:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def yellow(msg: str, end="\n") -> None:
        print(f"{AdvancedPrint.YELLOW}{msg}{AdvancedPrint.ENDC}", end=end)

    @staticmethod
    def red(msg: str, end="\n") -> None:
        print(f"{AdvancedPrint.RED}{msg}{AdvancedPrint.ENDC}", end=end)

    @staticmethod
    def green(msg: str, end="\n") -> None:
        print(f"{AdvancedPrint.GREEN}{msg}{AdvancedPrint.ENDC}", end=end)

    @staticmethod
    def blue(msg: str, end="\n") -> None:
        print(f"{AdvancedPrint.BLUE}{msg}{AdvancedPrint.ENDC}", end=end)

    @staticmethod
    def pink(msg: str, end="\n") -> None:
        print(f"{AdvancedPrint.HEADER}{msg}{AdvancedPrint.ENDC}", end=end)

    @staticmethod
    def underline(msg: str, end="\n") -> None:
        print(f"{AdvancedPrint.UNDERLINE}{msg}{AdvancedPrint.ENDC}", end=end)

    @staticmethod
    def bold(msg: str, end="\n") -> None:
        print(f"{AdvancedPrint.BOLD}{msg}{AdvancedPrint.ENDC}", end=end)
