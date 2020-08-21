#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()

try:
    cpu.load(sys.argv[1])
    cpu.run()
except IndexError:
    print("You need a file name to continue")