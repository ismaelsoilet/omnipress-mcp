"""OmniPress Blender 3D Template: Brazil Flag (Legacy Alias).

Forwarding wrapper for the universal waving_flag.py template.
Maintained for backward compatibility with existing CLI invocations and scripts.
"""

from pathlib import Path

_target = Path(__file__).parent / "waving_flag.py"
if _target.is_file():
    with open(_target, "rb") as _f:
        exec(compile(_f.read(), str(_target), "exec"))
