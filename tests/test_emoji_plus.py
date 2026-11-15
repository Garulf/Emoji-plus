import asyncio
import json
import sys

import pytest

import emoji_plus

COPY_METHOD = "Flow.Launcher.CopyToClipboard"


def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def titles(results):
    return [result.title for result in results]


def test_icon_file_name_joins_lowercase_codepoints():
    assert emoji_plus.icon_file_name("\U0001F600") == "1f600.png"
    assert emoji_plus.icon_file_name("❤️") == "2764_fe0f.png"


def test_emojis_without_an_icon_are_skipped(sample_emojis):
    assert [emoji.title for emoji in sample_emojis] == ["Grinning Face", "Red Heart"]


def test_empty_query_lists_every_emoji_in_data_order(sample_emojis, settings):
    assert titles(run(emoji_plus.query(""))) == ["Grinning Face", "Red Heart"]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("HEART", ["Red Heart"]),
        ("happy", ["Grinning Face"]),
        (":grin", ["Grinning Face"]),
        ("e", ["Grinning Face", "Red Heart"]),
        ("pizza", []),
    ],
)
def test_query_matches_title_aliases_and_shortcodes(sample_emojis, settings, text, expected):
    assert titles(run(emoji_plus.query(text))) == expected


def test_result_shows_aliases_and_shortcodes(sample_emojis, settings):
    (result,) = run(emoji_plus.query("heart"))
    assert result.subtitle == "love, :heart:"
    assert result.icon.endswith("2764_fe0f.png")
    assert result.context_data == ["❤️", "Red Heart"]


@pytest.mark.parametrize("value", [True, "true", None])
def test_auto_insert_types_the_emoji(sample_emojis, settings, value):
    if value is not None:
        settings["auto_insert"] = value
    (result,) = run(emoji_plus.query("heart"))
    assert result.json_rpc_action["Method"] == "type_char"
    assert result.json_rpc_action["Parameters"] == ["❤️"]


@pytest.mark.parametrize("value", [False, "false"])
def test_without_auto_insert_the_emoji_is_copied(sample_emojis, settings, value):
    settings["auto_insert"] = value
    (result,) = run(emoji_plus.query("heart"))
    assert result.json_rpc_action["Method"] == COPY_METHOD
    assert result.json_rpc_action["Parameters"] == ["❤️", True, False]


def test_type_char_copies_then_starts_sendkeys(host, popen):
    run(emoji_plus.type_char("\U0001F600"))
    assert host == [{"Method": COPY_METHOD, "Parameters": ["\U0001F600", True, False]}]
    ((args, kwargs),) = popen
    assert args[0] == [sys.executable, str(emoji_plus.SENDKEYS_SCRIPT)]
    assert kwargs["creationflags"] == emoji_plus.CREATE_NO_WINDOW


def test_context_menu_offers_copy_and_emojipedia():
    copy, emojipedia = emoji_plus.context_menu(["\U0001F600", "Grinning Face"])
    assert copy.title == "Copy"
    assert copy.json_rpc_action["Method"] == COPY_METHOD
    assert copy.json_rpc_action["Parameters"][0] == "\U0001F600"
    assert emojipedia.title == "Open on Emojipedia.org"
    assert emojipedia.json_rpc_action["Method"] == "Flow.Launcher.OpenUrl"
    assert emojipedia.json_rpc_action["Parameters"][0] == "https://emojipedia.org/grinning-face"


@pytest.mark.parametrize(
    "title, slug",
    [
        ("Flag: United States", "flag-united-states"),
        ("Keycap: *", "keycap-*"),
        ("Woman Technologist (Medium Skin Tone)", "woman-technologist-medium-skin-tone"),
        ("St. Lucia", "st-lucia"),
    ],
)
def test_emojipedia_url(title, slug):
    assert emoji_plus.emojipedia_url(title) == f"https://emojipedia.org/{slug}"


def test_bundled_data_loads_with_icons():
    emojis = emoji_plus.load_emojis(emoji_plus.EMOJI_DATA, emoji_plus.ICON_DIR)
    assert len(emojis) > 3000
    assert emojis[0].title == "Grinning Face"


def test_query_handler_is_registered_over_json_rpc(sample_emojis, settings):
    handler = emoji_plus.plugin._event_handler
    response = run(handler.trigger_event("query", "heart"))
    assert [item["Title"] for item in response["Result"]] == ["Red Heart"]
    json.dumps(response, default=lambda o: o.to_json())
    menu = run(handler.trigger_event("context_menu", ["\U0001F600", "Grinning Face"]))
    assert [item["Title"] for item in menu["Result"]] == ["Copy", "Open on Emojipedia.org"]
