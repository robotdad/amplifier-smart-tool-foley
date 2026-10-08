"""Public Agent adapter. A child process isolates configuration and SDK logs."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
from typing import Any

from foley.intelligence.schemas import AgentRequest, AgentResult
from foley.schemas import FoleyError

PROVIDERS = ("openai", "anthropic", "gemini", "openai-chatgpt", "github-copilot")
ALIASES = {"chatgpt": "openai-chatgpt", "github": "github-copilot"}


def canonical_provider(provider: str) -> str:
    provider = ALIASES.get(provider, provider)
    if provider not in PROVIDERS:
        raise FoleyError(f"Unsupported provider. Choose {', '.join(PROVIDERS)}.")
    return provider


def invoke_worker(payload: dict[str, Any], timeout: int = 300) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="foley-agent-") as directory:
        root = Path(directory)
        config = root / "config.json"
        config.write_text('{"context_intelligence":{"destinations":{}},"extra_request_params":{}}')
        env = {k: v for k, v in os.environ.items() if not k.startswith("AMPLIFIER_AGENT_")}
        env["AMPLIFIER_AGENT_CONFIG"] = str(config)
        env["AMPLIFIER_AGENT_SESSIONS_DIRECTORY"] = str(root / "sessions")
        # Only the public config is selected. HOME is preserved for subscription
        # credentials; ambient Agent config, tools and capture endpoints are not.
        with subprocess.Popen(
            [sys.executable, "-m", "foley.intelligence.worker"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env=env,
            cwd=root,
            start_new_session=os.name == "posix",
        ) as process:
            try:
                stdout, _ = process.communicate(json.dumps(payload), timeout=timeout + 15)
            except subprocess.TimeoutExpired as exc:
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.communicate()
                raise FoleyError(
                    "Agent timed out. No sound was published; check provider access or use a longer timeout."
                ) from exc
        if process.returncode:
            raise FoleyError(
                "Agent runtime failed. Run foley doctor --providers and verify the installed Agent dependencies."
            )
        try:
            return json.loads(stdout)
        except ValueError as exc:
            raise FoleyError(
                "Agent returned an invalid adapter response. Reinstall the package and run doctor."
            ) from exc


class AgentIntelligence:
    implementation = "amplifier-agent public 0.22"

    def preflight(self) -> None:
        from importlib.metadata import PackageNotFoundError, version

        try:
            version("amplifier-agent")
        except PackageNotFoundError as exc:
            raise FoleyError("Install Foley's declared amplifier-agent dependency before using create/revise.") from exc

    def run(self, request: AgentRequest) -> AgentResult:
        self.preflight()
        canonical_provider(request.provider)
        return AgentResult.model_validate(
            invoke_worker({"action": "design", "request": request.model_dump(mode="json")}, request.timeout_seconds)
        )


def discover(provider: str | None = None) -> dict[str, Any]:
    if provider:
        provider = canonical_provider(provider)
    return invoke_worker({"action": "models" if provider else "providers", "provider": provider}, 60)
