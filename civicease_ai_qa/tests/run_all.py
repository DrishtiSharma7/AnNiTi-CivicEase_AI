"""Runs every test with no pytest needed:  python tests/run_all.py   (pytest -q also works)"""
import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root.parent))
suite = unittest.defaultTestLoader.discover(str(root), pattern="test_*.py")
res = unittest.TextTestRunner(verbosity=1).run(suite)
sys.exit(0 if res.wasSuccessful() else 1)
