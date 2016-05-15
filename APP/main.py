#!/usr/bin/env python3

import sys
from core import SatView


def main():
    try:
        app = SatView()
        app.run()
    except Exception as e:
        print("fatal error: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
