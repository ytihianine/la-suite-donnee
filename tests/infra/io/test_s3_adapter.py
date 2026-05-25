from typing import Any
from unittest.mock import MagicMock

from src.infra.io.io_interface import IOInterface
from src.infra.io.s3_adapter import S3Adapter


class TestS3Adapter:
    """Tests for the S3Adapter."""

    def _make_adapter(self, client: Any = None) -> S3Adapter:
        """Create an S3Adapter with a mock client."""
        mock_client = client or MagicMock()
        return S3Adapter(bucket_name="test-bucket", client=mock_client)

    def test_implements_io_interface(self) -> None:
        """Test that S3Adapter is a subclass of IOInterface."""
        assert issubclass(S3Adapter, IOInterface)

    def test_read_calls_get_object(self) -> None:
        """Test that read delegates to get_object with the correct parameters."""
        mock_client = MagicMock()
        body = MagicMock()
        body.read.return_value = b"file content"
        mock_client.get_object.return_value = {"Body": body}
        adapter = self._make_adapter(mock_client)

        result = adapter.read("path/to/file.txt")

        mock_client.get_object.assert_called_once_with(
            Bucket="test-bucket", Key="path/to/file.txt"
        )
        assert result == b"file content"

    def test_write_bytes_calls_put_object(self) -> None:
        """Test that write with bytes delegates to put_object."""
        mock_client = MagicMock()
        adapter = self._make_adapter(mock_client)

        adapter.write("path/to/output.bin", b"raw bytes")

        mock_client.put_object.assert_called_once_with(
            Bucket="test-bucket", Key="path/to/output.bin", Body=b"raw bytes"
        )

    def test_write_string_encodes_to_utf8(self) -> None:
        """Test that write with a string encodes it to UTF-8 before uploading."""
        mock_client = MagicMock()
        adapter = self._make_adapter(mock_client)

        adapter.write("path/to/output.txt", "hello world")

        mock_client.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="path/to/output.txt",
            Body=b"hello world",
        )
