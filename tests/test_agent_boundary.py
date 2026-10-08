from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from typing import Any

import pytest

from foley import lib
from foley.intelligence.agent import AgentIntelligence, invoke_worker
from foley.intelligence.schemas import AgentRequest
from foley.scene import Scene


def request():
    return AgentRequest(
        provider="openai",
        model="gpt-6-astra",
        prompt="Make a metal impact",
        output_schema=Scene.model_json_schema(),
        timeout_seconds=60,
    )


def test_worker_configuration_isolation(monkeypatch):
    monkeypatch.setenv("AMPLIFIER_AGENT_CONFIG", "/host/private/config.json")
    monkeypatch.setenv("AMPLIFIER_AGENT_MODEL", "do-not-inherit")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-for-logs")

    class FakeProcess:
        returncode = 0

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def communicate(self, text, timeout):
            return '{"providers":[]}', None

    def fake_popen(command, **kwargs):
        assert command[-2:] == ["-m", "foley.intelligence.worker"]
        env = kwargs["env"]
        assert "AMPLIFIER_AGENT_MODEL" not in env
        assert env["OPENAI_API_KEY"] == "test-key-not-for-logs"
        assert env["AMPLIFIER_AGENT_CONFIG"] != "/host/private/config.json"
        assert json.loads(Path(env["AMPLIFIER_AGENT_CONFIG"]).read_text()) == {
            "context_intelligence": {"destinations": {}},
            "extra_request_params": {},
        }
        return FakeProcess()

    monkeypatch.setattr("foley.intelligence.agent.subprocess.Popen", fake_popen)
    assert invoke_worker({"action": "providers"}) == {"providers": []}


@dataclass
class LocalProvider:
    address: str
    requests: list[dict]
    behavior: dict[str, str]


@pytest.fixture
def local_provider():
    requests = []
    behavior = {"mode": "normal"}
    scene = lib.recipe("metal-impact", duration=2).model_dump()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            pass

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append(body)
            turn = len(requests)
            mode = behavior["mode"]
            if mode == "failure-after-submit" and turn > 1:
                data = b'{"error":{"message":"secret-never-print","type":"invalid_request_error","code":"test"}}'
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            submit_turn = (turn <= 2 if mode == "invalid-then-valid" else turn == 1) and mode != "no-submission"
            if submit_turn:
                submitted = json.loads(json.dumps(scene))
                if mode == "invalid-then-valid" and turn == 1:
                    submitted["layers"][0]["attack"] = 2
                item: dict[str, Any] = {
                    "type": "function_call",
                    "id": f"fc_{turn}",
                    "call_id": f"call_{turn}",
                    "name": "submit_scene",
                    "arguments": json.dumps(submitted),
                    "status": "completed",
                }
            else:
                item = {
                    "type": "message",
                    "id": "msg_1",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": "Scene submitted.", "annotations": []}],
                }
            response = {
                "id": f"resp_{turn}",
                "object": "response",
                "created_at": 1,
                "status": "completed",
                "error": None,
                "incomplete_details": None,
                "model": body["model"],
                "output": [item],
                "usage": {"input_tokens": 10, "output_tokens": 10, "total_tokens": 20},
                "parallel_tool_calls": False,
                "tool_choice": "auto",
                "tools": body.get("tools", []),
            }
            if not body.get("stream"):
                data = json.dumps(response).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            events: list[dict[str, Any]] = [
                {"type": "response.created", "response": {**response, "status": "in_progress", "output": []}},
                {
                    "type": "response.output_item.added",
                    "output_index": 0,
                    "item": {**item, "arguments": ""} if submit_turn else {**item, "content": []},
                },
            ]
            if submit_turn:
                events += [
                    {
                        "type": "response.function_call_arguments.delta",
                        "item_id": f"fc_{turn}",
                        "output_index": 0,
                        "delta": item["arguments"],
                    },
                    {
                        "type": "response.function_call_arguments.done",
                        "item_id": f"fc_{turn}",
                        "output_index": 0,
                        "arguments": item["arguments"],
                    },
                ]
            else:
                events += [
                    {
                        "type": "response.content_part.added",
                        "item_id": "msg_1",
                        "output_index": 0,
                        "content_index": 0,
                        "part": {"type": "output_text", "text": "", "annotations": []},
                    },
                    {
                        "type": "response.output_text.delta",
                        "item_id": "msg_1",
                        "output_index": 0,
                        "content_index": 0,
                        "delta": "Scene submitted.",
                    },
                    {
                        "type": "response.output_text.done",
                        "item_id": "msg_1",
                        "output_index": 0,
                        "content_index": 0,
                        "text": "Scene submitted.",
                    },
                ]
            events += [
                {"type": "response.output_item.done", "output_index": 0, "item": item},
                {"type": "response.completed", "response": response},
            ]
            data = "".join(
                f"event: {event['type']}\ndata: {json.dumps({**event, 'sequence_number': i})}\n\n"
                for i, event in enumerate(events)
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield LocalProvider(f"http://127.0.0.1:{server.server_port}/v1", requests, behavior)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_public_agent_against_local_endpoint(local_provider, monkeypatch):
    """Real public SDK/engine, synthetic HTTP provider, no paid network request."""
    monkeypatch.setenv("OPENAI_BASE_URL", local_provider.address)
    monkeypatch.setenv("OPENAI_API_KEY", "local-test-only")
    result = AgentIntelligence().run(request())
    assert result.error is None, result
    assert result.output is not None
    assert result.output["title"] == "Metal Impact"
    assert result.provenance["provider"] == "openai"
    assert result.provenance["model"] == "gpt-6-astra"
    assert result.provenance["observed_selections"]
    assert result.provenance["observed_selections"][0]["model"] == "gpt-6-astra"
    assert result.provenance["terminal_state"] == "success"
    assert len(local_provider.requests) == 2
    for body in local_provider.requests:
        assert body["model"] == "gpt-6-astra"
        assert body.get("store") is False
        assert [tool["name"] for tool in body["tools"]] == ["submit_scene"]
        parameters = body["tools"][0]["parameters"]
        serialized_schema = json.dumps(parameters)
        for name in ("duration", "attack", "release", "sustain"):
            description = Scene.model_json_schema()["$defs"]["Layer"]["properties"][name]["description"]
            assert description in serialized_schema
        serialized_request = json.dumps(body)
        assert "sustain=0 makes release silent" in serialized_request
        assert "not a hold" in serialized_request
        assert "preserve unrelated components" in serialized_request


@pytest.mark.parametrize("mode", ["no-submission", "invalid-then-valid", "failure-after-submit"])
def test_public_agent_recovery(local_provider, monkeypatch, mode):
    monkeypatch.setenv("OPENAI_BASE_URL", local_provider.address)
    monkeypatch.setenv("OPENAI_API_KEY", "local-test-only")
    local_provider.behavior["mode"] = mode
    result = AgentIntelligence().run(request())
    if mode == "no-submission":
        assert result.output is None
        assert result.error is not None
        assert "NO_SUBMISSION" in result.error
    else:
        assert result.output is not None, result
        assert result.error is None
        Scene.model_validate(result.output)
    if mode == "invalid-then-valid":
        assert len(local_provider.requests) == 3
    if mode == "failure-after-submit":
        assert result.provenance["terminal_state"] == "failure"
    assert "secret-never-print" not in result.model_dump_json()
