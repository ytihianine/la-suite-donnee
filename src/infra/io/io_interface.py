from abc import ABC, abstractmethod
from typing import Any


class IOInterface(ABC):
    """Abstract interface for I/O operations."""

    @abstractmethod
    def read(self, source: str) -> Any:
        """Read data from the given source.

        Args:
            source: Identifier of the resource to read from (e.g. file path, URL, key).

        Returns:
            The data read from the source.
        """

    @abstractmethod
    def write(self, destination: str, data: Any) -> None:
        """Write data to the given destination.

        Args:
            destination: Identifier of the resource to write to.
            data: The data to write.
        """
