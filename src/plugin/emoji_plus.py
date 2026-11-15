from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, List, Tuple

from pyflowlauncher import FlowLauncherV2, Plugin, Result
from pyflowlauncher.command import Command

PLUGIN_DIR = Path(__file__).resolve().parent
EMOJI_DATA = PLUGIN_DIR / "assets" / "emojis.json"
ICON_DIR = PLUGIN_DIR / "assets" / "icons"
SENDKEYS_SCRIPT = PLUGIN_DIR / "sendkeys.py"
CREATE_NO_WINDOW = 0x08000000

plugin = Plugin(launcher=FlowLauncherV2())


@dataclass(frozen=True)
class Emoji:
    char: str
    title: str
    aliases: Tuple[str, ...]
    shortcodes: Tuple[str, ...]
    icon: str

    @property
    def subtitle(self) -> str:
        return ", ".join(self.aliases + self.shortcodes)

    def matches(self, query: str) -> bool:
        needle = query.lower()
        return any(needle in text.lower() for text in (*self.aliases, *self.shortcodes, self.title))


def icon_file_name(char: str) -> str:
    return "_".join(f"{ord(c):x}" for c in char) + ".png"


def load_emojis(data_path: Path, icon_dir: Path) -> List[Emoji]:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    emojis = []
    for char, entry in data.items():
        icon = icon_dir / icon_file_name(char)
        if icon.exists():
            emojis.append(
                Emoji(
                    char=char,
                    title=entry["title"],
                    aliases=tuple(entry["aliases"]),
                    shortcodes=tuple(entry["shortcodes"]),
                    icon=str(icon),
                )
            )
    return emojis


@lru_cache(maxsize=1)
def all_emojis() -> List[Emoji]:
    return load_emojis(EMOJI_DATA, ICON_DIR)


def as_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return default


def auto_insert() -> bool:
    return as_bool(plugin.settings.get("auto_insert"), default=True)


def emojipedia_url(title: str) -> str:
    slug = title.lower()
    for old, new in ((":", ""), ("_", "-"), (" ", "-"), (".", ""), ("(", ""), (")", "")):
        slug = slug.replace(old, new)
    return f"https://emojipedia.org/{slug}"


def copy_command(char: str) -> Command:
    return plugin.launcher.api.copy_to_clipboard(char, direct_copy=True, show_default_notification=False)


@plugin.on_method
async def type_char(char: str) -> None:
    await plugin.launcher.api.invoke(copy_command(char))
    subprocess.Popen(
        [sys.executable, str(SENDKEYS_SCRIPT)],
        creationflags=CREATE_NO_WINDOW,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def emoji_result(emoji: Emoji, insert: bool) -> Result:
    result = Result(
        title=emoji.title,
        subtitle=emoji.subtitle,
        icon=emoji.icon,
        context_data=[emoji.char, emoji.title],
    )
    if insert:
        return result.add_action(type_char, parameters=[emoji.char])
    return result.add_action(copy_command(emoji.char))


@plugin.on_method
async def query(query: str) -> List[Result]:
    insert = auto_insert()
    return [emoji_result(emoji, insert) for emoji in all_emojis() if emoji.matches(query)]


@plugin.on_method
def context_menu(data: list) -> List[Result]:
    char, title = data[0], data[1]
    icons = plugin.launcher.icons
    return [
        Result(title="Copy", subtitle="Copy emoji to clipboard", icon=icons.copy).add_action(copy_command(char)),
        Result(
            title="Open on Emojipedia.org",
            subtitle="Opens Emojipedia.org for this emoji",
            icon=icons.browser,
        ).add_action(plugin.launcher.api.open_url(emojipedia_url(title))),
    ]
