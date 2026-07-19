import sys
from wiz.cli import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting cleanly.")
        sys.exit(0)
