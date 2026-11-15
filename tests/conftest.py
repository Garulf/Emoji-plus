import json

import pytest

import emoji_plus

SAMPLE_DATA = {
    "\U0001F600": {"title": "Grinning Face", "aliases": ["happy face"], "codepoints": ["U+1F600"], "shortcodes": [":grinning:"]},
    "❤️": {"title": "Red Heart", "aliases": ["love"], "codepoints": ["U+2764", "U+FE0F"], "shortcodes": [":heart:"]},
    "\U0001F984": {"title": "Unicorn", "aliases": [], "codepoints": ["U+1F984"], "shortcodes": [":unicorn:"]},
}


@pytest.fixture
def sample_emojis(tmp_path, monkeypatch):
    data_path = tmp_path / "emojis.json"
    data_path.write_text(json.dumps(SAMPLE_DATA), encoding="utf-8")
    icon_dir = tmp_path / "icons"
    icon_dir.mkdir()
    for name in ("1f600.png", "2764_fe0f.png"):
        (icon_dir / name).write_bytes(b"")
    emojis = emoji_plus.load_emojis(data_path, icon_dir)
    monkeypatch.setattr(emoji_plus, "all_emojis", lambda: emojis)
    return emojis


@pytest.fixture
def settings():
    launcher = emoji_plus.plugin.launcher
    launcher._settings = {}
    yield launcher._settings
    launcher._settings = {}


@pytest.fixture
def host(monkeypatch):
    invoked = []

    async def invoke(command):
        invoked.append(command)

    monkeypatch.setattr(emoji_plus.plugin.launcher.api, "_invoke_fn", invoke)
    return invoked


@pytest.fixture
def popen(monkeypatch):
    calls = []
    monkeypatch.setattr(emoji_plus.subprocess, "Popen", lambda *args, **kwargs: calls.append((args, kwargs)))
    return calls
