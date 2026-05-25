import urllib.request
from urllib.error import URLError


def ping(url: str) -> bool:
    """Ping a website and return True if it responds, False otherwise.

    Args:
        url: The full URL to ping (e.g. "https://example.com").

    Returns:
        True if the website responds successfully, False otherwise.
    """
    try:
        urllib.request.urlopen(url, timeout=5)
    except (URLError, ValueError, OSError):
        return False
    return True
