from urlextract import URLExtract
import requests
import re


def is_yt_url(video_id: str) -> bool:
    checker_url = "https://www.youtube.com/oembed?url="
    video_url = checker_url + video_id
    request = requests.get(video_url)
    return request.status_code == 200


def get_links_from_text(text: str) -> list:
    urls = URLExtract().find_urls(text)
    yt_urls = []
    for url in urls:
        if is_yt_url(url):
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
    idx = url.find('list=')
    pl_id = url[idx + 5:]
    pl_url = "https://www.youtube.com/playlist?list=" + pl_id
    if is_yt_url(pl_url):
        return pl_url
    return ""


def get_yt_links_from_pl(url: str) -> list:
    urls = []
    page_text = requests.get(url).text
    parser = re.compile(r"watch\?v=\S+?list=")
    playlist = set(re.findall(parser, page_text))
    playlist = map(
        (lambda x: "https://www.youtube.com/" + x.replace("\\u0026list=", "")), playlist
    )
    return [*playlist]


def get_sec(time_str) -> int:
    """Get Seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)
