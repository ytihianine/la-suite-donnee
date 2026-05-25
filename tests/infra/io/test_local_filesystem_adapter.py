from pathlib import Path

import pytest

from src.infra.io.io_interface import IOInterface
from src.infra.io.local_filesystem_adapter import LocalFilesystemAdapter


class TestLocalFilesystemAdapter:
    """Tests for the LocalFilesystemAdapter."""

    def test_implements_io_interface(self) -> None:
        """Test that LocalFilesystemAdapter is a subclass of IOInterface."""
        assert issubclass(LocalFilesystemAdapter, IOInterface)

    def test_write_and_read_bytes(self, tmp_path: Path) -> None:
        """Test writing and reading bytes round-trips correctly."""
        adapter = LocalFilesystemAdapter()
        file_path = str(tmp_path / "data.bin")

        adapter.write(file_path, b"binary content")
        result = adapter.read(file_path)

        assert result == b"binary content"

    def test_write_string_encodes_utf8(self, tmp_path: Path) -> None:
        """Test that writing a string stores it as UTF-8."""
        adapter = LocalFilesystemAdapter()
        file_path = str(tmp_path / "text.txt")

        adapter.write(file_path, "héllo wörld")
        result = adapter.read(file_path)

        assert result == "héllo wörld".encode("utf-8")

    def test_write_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test that write creates missing parent directories."""
        adapter = LocalFilesystemAdapter()
        file_path = str(tmp_path / "a" / "b" / "c" / "file.txt")

        adapter.write(file_path, b"nested")

        assert adapter.read(file_path) == b"nested"

    def test_read_missing_file_raises(self, tmp_path: Path) -> None:
        """Test that reading a non-existent file raises FileNotFoundError."""
        adapter = LocalFilesystemAdapter()

        with pytest.raises(FileNotFoundError):
            adapter.read(str(tmp_path / "missing.txt"))
