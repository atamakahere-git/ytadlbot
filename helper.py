from urlextract import URLExtract
from urllib import request, error
import requests
import re


def is_yt_url(video_id: str) -> bool:
    checker_url = "https://www.youtube.com/oembed?url="
    video_url = checker_url + video_id
    request = requests.get(video_url)
    return request.status_code == 200


def is_pl_url(url: str):
    if 'list=' in url:
        r = requests.get(url)
        return "Video unavailable" not in r.text
    return False


def get_links_from_text(text: str) -> list:
    urls = URLExtract().find_urls(text)
    yt_urls = []
    for url in urls:
        if is_yt_url(url) or is_pl_url(url):
            yt_urls.append(url)

    return yt_urls


def pretty_url_string(urls: list) -> str:
    pretty_url = ""
    if len(urls) == 0:
        return "No valid url found"
    elif len(urls) > 1:
        pretty_url += f"Received {len(urls)} links\n"
        i = 1
        for url in urls:
            pretty_url += f"{i}. {url}\n"
            i += 1
    pretty_url += "Downloading ..."

    return pretty_url[:4096]


def is_yt_playlist(url: str) -> bool:
    return url.startswith("https://www.youtube.com/playlist?list=")


def get_pl_link_from_url(url: str) -> str:
    if 'list=' in url:
        eq_idx = url.index('=') + 1
        pl_id = url[eq_idx:]
        if '&' in url:
            amp = url.index('&')
            pl_id = url[eq_idx:amp]
        return "https://www.youtube.com/playlist?list=" + pl_id
    else:
        return ""


def get_yt_links_from_pl(url: str) -> list:
    page = None
    urls = []
    try:
        page = request.urlopen(url).read()
        page = str(page)
    except error.URLError as e:
        print(e.reason)
    idx = url.find('list=')
    playlist_id = url[idx+5:]
    if page:
        vid_url_pat = re.compile(r'watch\?v=\S+?list=' + playlist_id)
        vid_url_matches = list(set(re.findall(vid_url_pat, page)))
        if vid_url_matches:
            for vid_url in vid_url_matches:
                urls.append('https://www.youtube.com/'+vid_url[:19])
    return urls


def get_sec(time_str) -> int:
    """Get Seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)
