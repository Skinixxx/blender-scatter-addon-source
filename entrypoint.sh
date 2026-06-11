#!/bin/sh
set -e
BLENDER="${BLENDER_PATH}/blender"
BLENDER_PYTHON="${BLENDER_PATH}/4.2/python/bin/python3.11"
export PYTHONPATH="/app:$PYTHONPATH"

# Install test dependencies into Blender's bundled Python
"$BLENDER_PYTHON" -m pip install --quiet pytest pytest-cov 2>/dev/null

"$BLENDER" --background --python-expr "
import sys
sys.path.insert(0, '/app')
from blender_scatter_addon import register
register()
import pytest
sys.exit(pytest.main(['tests/', '-v']))
"
