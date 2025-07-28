"""
Entry point to run the tzbundler (make_tz_bundle.py) tool.
"""
import sys
from tzbundler.make_tz_bundle import main

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
