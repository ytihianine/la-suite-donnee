from unittest.mock import MagicMock, patch
from urllib.error import URLError

from src.infra.http.ping import ping


class TestPing:
    """Tests for the ping function."""

    @patch("src.infra.http.ping.urllib.request.urlopen")
    def test_ping_success(self, mock_urlopen: MagicMock) -> None:
        """Test that ping returns True when the website responds."""
        mock_urlopen.return_value = MagicMock()
        assert ping("https://example.com") is True
        mock_urlopen.assert_called_once_with("https://example.com", timeout=5)

    @patch("src.infra.http.ping.urllib.request.urlopen")
    def test_ping_url_error(self, mock_urlopen: MagicMock) -> None:
        """Test that ping returns False when a URLError occurs."""
        mock_urlopen.side_effect = URLError("Connection refused")
        assert ping("https://unreachable.example.com") is False

    def test_ping_invalid_url(self) -> None:
        """Test that ping returns False for an invalid URL."""
        assert ping("not-a-valid-url") is False

    @patch("src.infra.http.ping.urllib.request.urlopen")
    def test_ping_timeout(self, mock_urlopen: MagicMock) -> None:
        """Test that ping returns False on a timeout (OSError)."""
        mock_urlopen.side_effect = OSError("Timeout")
        assert ping("https://example.com") is False
