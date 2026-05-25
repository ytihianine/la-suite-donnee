from pathlib import Path
from typing import Any

from src.infra.io.io_interface import IOInterface


class LocalFilesystemAdapter(IOInterface):
    """Local filesystem implementation of the IOInterface.

    Reads and writes files on the local disk.
    """

    def read(self, source: str) -> bytes:
        """Read a file from the local filesystem.

        Args:
            source: Path to the file to read.

        Returns:
            The raw bytes of the file.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        return Path(source).read_bytes()

    def write(self, destination: str, data: Any) -> None:
        """Write data to a file on the local filesystem.

        Creates parent directories if they do not exist.

        Args:
            destination: Path to the file to write.
            data: The data to write. Must be bytes or a string (encoded to UTF-8).
        """
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, str):
            path.write_text(data, encoding="utf-8")
        else:
            path.write_bytes(data)
