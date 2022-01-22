
import os

import pafy
import requests

from helper import is_yt_url, get_vid_id

FILE_SIZE_LIMIT = 50000000


class FileSizeExceeded(Exception):
    """File size limit exceeds the max telegram bot upload limit"""

    def __str__(self) -> str:
        return "File size above 50 MB"


class FileDownloadError(Exception):
    """File was not downloaded or not found in the disk"""

    def __str__(self) -> str:
        return "Unable to download file"


class UnableToDownload(Exception):

    def __str__(self) -> str:
        return "Unable to download file"


class YTADL:
    """YoutubeAudioDl object to carry out download operation"""

    def __init__(self, url: str, url_only=False):
        self.vid_id = get_vid_id(url)
        if self.vid_id == "":
            raise ValueError("Invalid YouTube URL")
        self.url = "https://www.youtube.com/watch?v=" + self.vid_id
        if not is_yt_url(self.url):
            raise ValueError("Invalid YouTube URL")
        self.pafy_obj = None
        self.audio_stream = None
        self.size = None
        self.downloadable = None
        self.file_title = None
        self.file_ext = None
        self.filename = None
        self.audio_file = None
        self.thumbnail = None
        if not url_only:
            self.processor_url()

    def processor_url(self):
        """Starts processing link and gather meta infos"""
        try:
            self.pafy_obj = pafy.new(self.vid_id, size=True)
            self.audio_stream = self.pafy_obj.getbestaudio(preftype='m4a')
            self.size = self.audio_stream.get_filesize()
            self.downloadable = False
            if self.size > FILE_SIZE_LIMIT:
                print("Bot will not be able to send file above 50MB!")
                raise FileSizeExceeded
            self.downloadable = True
            self.file_title = self.pafy_obj.title.replace('/', '_').replace('<', '_').replace('>', '_')
            self.file_ext = self.audio_stream.extension
            self.filename = ''
            self.audio_file = None
            self.thumbnail = requests.get(self.pafy_obj.getbestthumb()).content
        except:
            raise UnableToDownload

    def download(self):
        """Downloads the audio file"""
        self.filename = self.audio_stream.download(quiet=True)
        if self.filename is None:
            self.filename = self.file_title + '.' + self.file_ext
        try:
            self.audio_file = open(self.filename, 'rb')
        except FileNotFoundError:
            print("File download failed!")
            raise FileDownloadError

    def __del__(self):
        try:
            if self.filename:
                os.remove(self.filename)
        except FileNotFoundError:
            pass
