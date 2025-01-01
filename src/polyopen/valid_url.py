from urllib.parse import urlparse


def is_valid_url(url_string):
    url = urlparse(url_string)
    scheme = url.scheme
    return scheme in ["http", "https", "ftp"]
