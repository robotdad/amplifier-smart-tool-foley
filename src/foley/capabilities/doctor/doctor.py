from importlib.metadata import version
import re
import subprocess
from typing import Any

from foley.audio import engine_path
from foley.schemas import FoleyError


def doctor(providers: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"foley": version("foley"), "render_ready": False, "paid_generation": False}
    try:
        executable = engine_path()
        probe = subprocess.run([executable, "--version"], capture_output=True, timeout=10, text=True)
        match = re.search(r"Csound version ([0-9.]+)", probe.stderr + probe.stdout)
        result.update(
            csound=executable,
            engine_version=match[1] if match else "unknown",
            render_ready=probe.returncode == 0 and match is not None,
        )
    except (FoleyError, OSError, subprocess.TimeoutExpired, IndexError) as exc:
        result["engine_problem"] = str(exc)
    if providers:
        from foley.intelligence.agent import discover

        result["intelligence"] = discover()
    return result
