"""
Exports vCons to AWS S3
"""

import json
from typing import Optional
from vcon import Vcon
from src.logger import get_logger

try:
    import boto3
except ImportError:
    boto3 = None

logger = get_logger(__name__)


class S3Exporter:
    """Exports vCons to AWS S3 bucket"""

    def __init__(
        self,
        bucket: str,
        region: str = "us-east-1",
        prefix: str = "elevenlabs/",
        encryption: str = "none",
    ):
        """
        Initialize S3 exporter

        Args:
            bucket: S3 bucket name
            region: AWS region
            prefix: S3 key prefix
            encryption: Encryption type ('none', 'AES256', 'aws:kms')
        """
        self.bucket = bucket
        self.region = region
        self.prefix = prefix
        self.encryption = encryption

        try:
            if boto3 is None:
                raise ImportError("boto3 package not installed")
            self.s3_client = boto3.client("s3", region_name=region)
            logger.info(f"S3Exporter initialized for bucket: {bucket}")

        except ImportError:
            logger.error("boto3 package not installed")
            raise
        except Exception as e:
            logger.error(f"Error initializing S3 client: {str(e)}")
            raise

    def export(
        self,
        vcon: Vcon,
        key: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Export vCon to S3

        Args:
            vcon: vCon object to export
            key: Optional custom S3 key (without prefix)
            metadata: Optional S3 object metadata

        Returns:
            S3 object key
        """
        try:
            if key is None:
                key = f"{vcon.uuid}.vcon.json"

            full_key = f"{self.prefix.rstrip('/')}/{key}"

            vcon_json = vcon.to_json()
            body = json.dumps(vcon_json).encode("utf-8")

            extra_args = self._build_put_object_args(vcon, metadata)

            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=full_key,
                Body=body,
                ContentType="application/json",
                **extra_args,
            )

            logger.info(f"Successfully exported vCon to s3://{self.bucket}/{full_key}")
            return full_key

        except Exception as e:
            logger.error(f"Error exporting vCon to S3: {str(e)}")
            raise

    def export_batch(self, vcons: list, key_pattern: str = None) -> list:
        """
        Export multiple vCons to S3

        Args:
            vcons: List of vCon objects to export
            key_pattern: Optional pattern for S3 keys

        Returns:
            List of S3 object keys
        """
        keys = []

        for i, vcon in enumerate(vcons):
            try:
                if key_pattern:
                    key = key_pattern.format(
                        index=i,
                        uuid=vcon.uuid,
                    )
                else:
                    key = None

                s3_key = self.export(vcon, key)
                keys.append(s3_key)

            except Exception as e:
                logger.error(f"Error exporting vCon {i} to S3: {str(e)}")

        logger.info(f"Successfully exported {len(keys)} vCons to S3")
        return keys

    def _build_put_object_args(
        self, vcon: Vcon, metadata: Optional[dict] = None
    ) -> dict:
        """Build extra arguments for put_object call"""
        args = {}

        if self.encryption == "AES256":
            args["ServerSideEncryption"] = "AES256"
        elif self.encryption == "aws:kms":
            args["ServerSideEncryption"] = "aws:kms"

        if metadata:
            args["Metadata"] = metadata
        else:
            args["Metadata"] = {
                "vcon-uuid": vcon.uuid,
                "source": "elevenlabs-adapter",
            }

        args["Tagging"] = "source=elevenlabs&type=vcon"

        return args

    def verify_bucket_access(self) -> bool:
        """
        Verify that the S3 bucket is accessible

        Returns:
            True if bucket is accessible, False otherwise
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
            logger.info(f"Successfully verified access to S3 bucket: {self.bucket}")
            return True

        except Exception as e:
            logger.error(f"Error verifying S3 bucket access: {str(e)}")
            return False
