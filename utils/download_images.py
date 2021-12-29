from pathlib import Path
import shutil
from time import time

from tqdm import tqdm
from emojipedia import Emojipedia, Emoji
import requests



ICON_FOLDER = 'icons_test'
FOLDER_PATH = Path(Path.cwd(), ICON_FOLDER)
IMAGE_SIZES = {
    '72x72': 72,
    '120x120': 120
}


def download_img(emoji: Emoji, prefered_platform: str, image_size=IMAGE_SIZES['72x72']) -> None:
    """Downloads an emoji image from Emojipedia.org."""
    for _platform in emoji.platforms:
        if _platform.name.lower() == prefered_platform.lower():
            url = _platform.image_url
            # Emojipedia package only retrieves 120x120 images.
            if image_size == IMAGE_SIZES['72x72']:
                url = _platform.image_url.replace('/thumbs/120/', f'/thumbs/{IMAGE_SIZES["72x72"]}/')
            _download(url)
            break

def _download(url: str) -> str:
    """Downloads a file from a URL."""
    file_name = format_filename(url)
    path = FOLDER_PATH.joinpath(file_name)
    if path.exists():
        return
    try:
        response = requests.get(url, stream=True)
        if not Path(FOLDER_PATH).exists():
            Path(FOLDER_PATH).mkdir()
        with open(path, 'wb') as f:
            for data in response.iter_content(chunk_size=1024):
                if data:
                    f.write(data)
    except requests.exceptions.RequestException as e:
        pass
    

def format_filename(url: str) -> str:
    """Formats a URL to a filename."""
    idx = -1
    url_split = url.split('/')[-1].split('_')
    # Some file URL's have multiple underscores. We detect that here and split accordingly.
    if len(url_split) > 2:
        idx = -2
    file_name = url.split('/')[-1].split('_')[idx].replace("-", "_")
    if not file_name.endswith('.png'):
        file_name += '.png'
    return file_name

def main():

    all_emoji = Emojipedia.all()
    progress = tqdm(all_emoji)
    progress.set_description('Total Progress')
    for emoji in progress:
        progress.set_description(emoji.title) 
        download_img(emoji, 'twitter', IMAGE_SIZES['120x120'])

if __name__ == "__main__":
    script_start = time()
    main()
    script_start = time() - script_start
    print(f'Script finished in {script_start:.2f} seconds.')