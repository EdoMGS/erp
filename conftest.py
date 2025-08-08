"""
conftest.py – doda korijenski direktorij u sys.path
da bi pytest mogao importirati interne pakete.
"""
import os
import sys

# project root na početak sys.path-a
sys.path.insert(0, os.getcwd())