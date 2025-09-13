import sys
from time import sleep


def main():
    version = sys.version_info
    if (version < (3, 10)):
        print('[-] Checkpoint only works with Python 3.10+.')
        print(f'Your current Python version : {version.major}.{version.minor}.{version.micro}')
        sys.exit(1)

    from checkpoint.cli import parse_and_run
    from checkpoint.helpers.banner import show_banner
    from checkpoint.helpers.utils import show_version

    show_banner()
    show_version()
    print()
    parse_and_run()