from urlextract import URLExtract
import requests


def check_video_url(video_id):
    checker_url = "https://www.youtube.com/oembed?url="
    video_url = checker_url + video_id
    request = requests.get(video_url)
    return request.status_code == 200


def get_links_from_text(text: str) -> list:
    urls = URLExtract().find_urls(text)
    yt_urls = []
    for url in urls:
        if check_video_url(url):
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

    return pretty_url
