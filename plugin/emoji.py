import json
from pathlib import Path

from flox import Flox

from emojis.db.db import EMOJI_DB as db

ICON_FOLDER = Path(Path.cwd()) / "icons"



class Emoji(Flox):

    def translate_to_icon(self, emoji, _):
        code = []
        for idx, char in enumerate(emoji):
            char_code = '{:X}'.format(ord(emoji[idx])).lower()
            # if char_code != 'fe0f':
            code.append(char_code)
        if len(code) > 1:
            # if '200d' in code:
            #     for item in code:
            #         if item == 'fe0f':
            #             code.remove(item)
            file_name = "-".join(code) + ".png"
        else:
            file_name = code[0] + ".png"

        file_name = file_name.replace("fe0f", "")
        file_path = Path(ICON_FOLDER, file_name)
        if not file_path.exists():
            self.logger.info(_)
            self.logger.info(file_name)
        return str(file_path)


    def query(self, query):
        for emoji in db:
            if query.replace("_", " ") in emoji.aliases[0].replace("_", " "):
                icon = self.translate_to_icon(u'\U0001F947', emoji.aliases[0].title().replace("_", " "))
                self.add_item(
                    title=emoji.aliases[0].title().replace("_", " "),
                    subtitle=Path(icon).name,
                    icon=icon,
                )


    def context_menu(self, data):
        pass

if __name__ == "__main__":
    Emoji()

