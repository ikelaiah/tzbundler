"""
Entry point to run unified tzbundler tests.
"""
import sys
from tests.test_tzbundler import run_all_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)