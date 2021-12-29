import json

with open('plugin/emojis.json', 'r') as f:
    EMOJI_DATA = json.load(f)

for emoji in EMOJI_DATA.keys():
    for idx, alias in enumerate(EMOJI_DATA[emoji]['aliases']):
        EMOJI_DATA[emoji]['aliases'][idx] = alias.lower().replace("-", " ")

with open('plugin/emojis.json', 'w') as f:
    json.dump(EMOJI_DATA, f, indent=4)