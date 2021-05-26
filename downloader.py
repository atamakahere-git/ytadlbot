import os

import music_tag
import pafy

from helper import get_sec

CURR_DIR = os.path.dirname(os.path.realpath(__file__))
PATH = CURR_DIR + '/downloaded/'
try:
    os.mkdir('downloaded')
except:
    pass


def set_metadata(file_path_name: str, title: str, artist: str):
    audio = music_tag.load_file(file_path_name)
    audio['title'] = title
    audio['artist'] = artist


def download_from_url(url: str, chat_id: int):
    try:
        audio = pafy.new(url)
    except:
        return None
    audio_stream = audio.getbestaudio(preftype='m4a')
    if audio_stream.get_filesize() > 49999999:
        return {
            'status': False,
            'err': 'File size limit exceeded 50MB'
        }
    audio_title = audio.title
    audio_title = audio_title.replace('/', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace(':', '_').replace('&','_')
    file_name = audio_title + '.m4a'
    file_path_name = PATH + file_name
    audio_stream.download(filepath=file_path_name)
    set_metadata(file_path_name, audio_title, audio.author)
    return {
        'status': True,
        'file': file_path_name,
        'title': audio.title,
        'thumb': audio.getbestthumb(),
        'author': audio.author,
        'duration': get_sec(audio.duration)
    }


if __name__ == '__main__':
    pass
