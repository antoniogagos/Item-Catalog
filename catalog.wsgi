#!/usr/bin/python
import sys
import logging
import os
logging.basicConfig(stream=sys.stderr)
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)

from project import app as application
application.secret_key = 'Mzs8a3xPMY-BlK-3kEYFslJT'
