"""Default execution entry point if running the package via python -m."""
from dpp import runner
import sys


def main():
    """Run dpp from script entry point."""
    return runner.main()


if __name__ == '__main__':
    sys.exit(main())