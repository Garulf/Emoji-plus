import json
import os
import subprocess
import sys
from pathlib import Path

RUN_PY = Path(__file__).resolve().parents[1] / "src" / "run.py"


def rpc(tmp_path, *requests):
    env = {k: v for k, v in os.environ.items() if k not in {"APPDATA", "LOCALAPPDATA", "FLOW_PROGRAM_DIRECTORY"}}
    lines = [json.dumps({"jsonrpc": "2.0", "id": i, **r}) for i, r in enumerate(requests, 1)]
    lines.append(json.dumps({"jsonrpc": "2.0", "id": 0, "method": "close", "params": []}))
    proc = subprocess.run(
        [sys.executable, str(RUN_PY)],
        input="\n".join(lines) + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=tmp_path,
        env=env,
        timeout=60,
    )
    return {reply["id"]: reply for reply in map(json.loads, proc.stdout.splitlines())}


def test_starts_outside_a_flow_launcher_folder_and_answers_a_query(tmp_path):
    replies = rpc(tmp_path, {"method": "query", "params": [{"search": "rocket"}, {"auto_insert": False}]})
    assert replies[1]["error"] is None
    assert [r["Title"] for r in replies[1]["result"]["result"]] == ["Rocket"]


def test_empty_query_returns_every_emoji_as_valid_json(tmp_path):
    replies = rpc(tmp_path, {"method": "query", "params": [{"search": ""}, {}]})
    assert len(replies[1]["result"]["result"]) > 3000
