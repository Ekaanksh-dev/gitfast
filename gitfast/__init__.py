__version__ = "1.0.0"
__author__  = "Ekaanksh Patil"
__email__   = "pekanksh@email.com"
__license__ = "MIT"
__description__ = "42 git shortcuts + auto merge conflict resolver"

from gitfast.utils.colors import Colors

def banner():
    print(f"""
{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
{Colors.YELLOW}  ⚡ gitfast v{__version__}{Colors.RESET}
{Colors.GRAY}  42 git shortcuts. Zero friction.{Colors.RESET}
{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}
""")
