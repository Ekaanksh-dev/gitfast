import sys
import os


class Colors:
    SUPPORTED = hasattr(sys.stdout, "isatty") and (sys.stdout.isatty() or os.environ.get("FORCE_COLOR"))

    RED    = '\033[91m' if SUPPORTED else ''
    GREEN  = '\033[92m' if SUPPORTED else ''
    YELLOW = '\033[93m' if SUPPORTED else ''
    BLUE   = '\033[94m' if SUPPORTED else ''
    PURPLE = '\033[95m' if SUPPORTED else ''
    CYAN   = '\033[96m' if SUPPORTED else ''
    WHITE  = '\033[97m' if SUPPORTED else ''
    GRAY   = '\033[90m' if SUPPORTED else ''
    BOLD      = '\033[1m'  if SUPPORTED else ''
    UNDERLINE = '\033[4m'  if SUPPORTED else ''
    RESET     = '\033[0m'  if SUPPORTED else ''


class Printer:

    @staticmethod
    def success(msg):
        print(f"{Colors.GREEN}[OK] {msg}{Colors.RESET}")

    @staticmethod
    def error(msg):
        print(f"{Colors.RED}[ERROR] {msg}{Colors.RESET}")

    @staticmethod
    def warning(msg):
        print(f"{Colors.YELLOW}[WARN] {msg}{Colors.RESET}")

    @staticmethod
    def info(msg):
        print(f"{Colors.BLUE}[INFO] {msg}{Colors.RESET}")

    @staticmethod
    def step(msg):
        print(f"{Colors.CYAN}[..] {msg}{Colors.RESET}")

    @staticmethod
    def push(msg):
        print(f"{Colors.PURPLE}[PUSH] {msg}{Colors.RESET}")

    @staticmethod
    def save(msg):
        print(f"{Colors.YELLOW}[SAVE] {msg}{Colors.RESET}")

    @staticmethod
    def scan(msg):
        print(f"{Colors.BLUE}[SCAN] {msg}{Colors.RESET}")

    @staticmethod
    def divider():
        print(f"{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")

    @staticmethod
    def header(msg):
        Printer.divider()
        print(f"{Colors.YELLOW}  {msg}{Colors.RESET}")
        Printer.divider()
