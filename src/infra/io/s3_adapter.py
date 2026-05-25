from typing import Any

import boto3

from src.infra.io.io_interface import IOInterface


class S3Adapter(IOInterface):
    """S3 implementation of the IOInterface.

    Reads and writes objects in an Amazon S3 bucket.
    """

    def __init__(self, bucket_name: str, client: Any = None) -> None:
        """Initialize the S3 adapter.

        Args:
            bucket_name: Name of the S3 bucket to operate on.
            client: Optional pre-configured boto3 S3 client. If not provided,
                a default client is created.
        """
        self._bucket_name = bucket_name
        self._client: Any = client or boto3.client("s3")

    def read(self, source: str) -> bytes:
        """Read an object from S3.

        Args:
            source: The S3 object key to read.

        Returns:
            The raw bytes of the object.

        Raises:
            botocore.exceptions.ClientError: If the object does not exist
                or access is denied.
        """
        response = self._client.get_object(Bucket=self._bucket_name, Key=source)
        return response["Body"].read()  # type: ignore[no-any-return]

    def write(self, destination: str, data: Any) -> None:
        """Write data to an S3 object.

        Args:
            destination: The S3 object key to write to.
            data: The data to upload. Must be bytes or a string (encoded to UTF-8).
        """
        body = data.encode("utf-8") if isinstance(data, str) else data
        self._client.put_object(Bucket=self._bucket_name, Key=destination, Body=body)
