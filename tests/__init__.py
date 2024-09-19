import os
import sys

if os.environ.get('BRITIVE_UNIT_TESTING'):
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
