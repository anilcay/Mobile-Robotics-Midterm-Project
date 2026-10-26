"""Make the package importable when pytest runs from the source tree (no colcon)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
