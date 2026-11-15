from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "data" / "SettingsTemplate.yaml"


def test_auto_insert_setting_is_kept():
    text = TEMPLATE.read_text(encoding="utf-8")
    assert "type: checkbox" in text
    assert "name: auto_insert" in text
    assert 'defaultValue: "true"' in text


def test_auto_insert_description_is_shown_once():
    text = TEMPLATE.read_text(encoding="utf-8")
    assert text.count("into the last activated window") == 1
