from pathlib import Path
from time import time, sleep
import os
import sys
import json

from tqdm import tqdm
from emojipedia import Emojipedia, Emoji
import requests


ALIASES_FILENAME = 'emojis.json'
ALIASES_PATH = Path(Path.cwd(), ALIASES_FILENAME) 

def write_file(data: dict) -> None:
    """Writes a dictionary to a file."""
    with open(ALIASES_PATH, "r+") as file:
        file_data = json.load(file)
        file_data.update(data)
        file.seek(0)
        json.dump(file_data, file, indent=4)

def main():
    all_emoji = Emojipedia.all()
    progress = tqdm(all_emoji)
    progress.set_description('Total Progress')
    with open(ALIASES_PATH, 'w') as f:
        json.dump({}, f, indent=4)
    for emoji in progress:
        progress.write(emoji.title)
        shortcodes = []
        if emoji.shortcodes:
            shortcodes = emoji.shortcodes.replace('(Github, Slack)', '').replace('(Emojipedia)', '').replace('\n\n', '\n').split('\n')
            shortcodes[:] = [x for x in shortcodes if x]
        data = {
            emoji.character: {
                'title': emoji.title,
                'description': emoji.description,
                'aliases': emoji.aliases,
                'codepoints': emoji.codepoints,
                'shortcodes': shortcodes
            }
        }
        write_file(data)
        

if __name__ == '__main__':
    start = time()
    main()
    end = time() - start
    print(f'Finished in {end:.2f} seconds.')