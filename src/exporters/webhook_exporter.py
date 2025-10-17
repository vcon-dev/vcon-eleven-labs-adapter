"""
Exports vCons via HTTP webhooks
"""

import json
import time
from typing import Optional, List
from vcon import Vcon
import requests
from src.logger import get_logger

logger = get_logger(__name__)


class WebhookExporter:
    """Exports vCons via HTTP POST to webhook endpoints"""

    def __init__(
        self,
        url: str,
        api_key: Optional[str] = None,
        auth_type: str = "none",
        retry_attempts: int = 3,
        timeout: int = 30,
    ):
        """
        Initialize webhook exporter

        Args:
            url: Webhook URL to POST vCons to
            api_key: Optional API key for authentication
            auth_type: Authentication type ('none', 'bearer', 'api-key')
            retry_attempts: Number of retry attempts
            timeout: Request timeout in seconds
        """
        self.url = url
        self.api_key = api_key
        self.auth_type = auth_type
        self.retry_attempts = retry_attempts
        self.timeout = timeout

        logger.info(f"WebhookExporter initialized for URL: {url}")

    def export(
        self,
        vcon: Vcon,
        custom_headers: Optional[dict] = None,
    ) -> bool:
        """
        Export vCon via webhook POST

        Args:
            vcon: vCon object to export
            custom_headers: Optional custom HTTP headers

        Returns:
            True if successful, False otherwise
        """
        try:
            vcon_json = vcon.to_json()
            payload = json.dumps(vcon_json)

            headers = self._build_headers(custom_headers)

            for attempt in range(self.retry_attempts):
                try:
                    response = requests.post(
                        self.url,
                        data=payload,
                        headers=headers,
                        timeout=self.timeout,
                    )

                    if 200 <= response.status_code < 300:
                        logger.info(
                            f"Successfully posted vCon {vcon.uuid} to webhook (status: {response.status_code})"
                        )
                        return True
                    else:
                        logger.warning(
                            f"Webhook returned status {response.status_code}: {response.text}"
                        )

                        if attempt == self.retry_attempts - 1:
                            return False

                        wait_time = 2 ** attempt
                        logger.info(f"Retrying in {wait_time}s...")
                        time.sleep(wait_time)

                except requests.Timeout:
                    logger.warning(f"Webhook request timeout (attempt {attempt + 1}/{self.retry_attempts})")

                    if attempt == self.retry_attempts - 1:
                        return False

                    wait_time = 2 ** attempt
                    time.sleep(wait_time)

                except requests.RequestException as e:
                    logger.warning(f"Webhook request error: {str(e)}")

                    if attempt == self.retry_attempts - 1:
                        return False

                    wait_time = 2 ** attempt
                    time.sleep(wait_time)

            return False

        except Exception as e:
            logger.error(f"Error exporting vCon via webhook: {str(e)}")
            return False

    def export_batch(
        self,
        vcons: List[Vcon],
        batch_size: int = 1,
    ) -> dict:
        """
        Export multiple vCons via webhook

        Args:
            vcons: List of vCon objects to export
            batch_size: Whether to batch multiple vCons per request

        Returns:
            Dictionary with success/failure counts
        """
        results = {
            "successful": 0,
            "failed": 0,
            "total": len(vcons),
        }

        if batch_size == 1:
            for vcon in vcons:
                if self.export(vcon):
                    results["successful"] += 1
                else:
                    results["failed"] += 1

        else:
            for i in range(0, len(vcons), batch_size):
                batch = vcons[i : i + batch_size]

                if self._export_batch_request(batch):
                    results["successful"] += len(batch)
                else:
                    results["failed"] += len(batch)

        logger.info(
            f"Batch export complete: {results['successful']} successful, {results['failed']} failed"
        )
        return results

    def _export_batch_request(self, vcons: List[Vcon]) -> bool:
        """Export a batch of vCons in a single request"""
        try:
            batch_data = [vcon.to_json() for vcon in vcons]
            payload = json.dumps({"vcons": batch_data})

            headers = self._build_headers()
            headers["X-Batch-Size"] = str(len(vcons))

            response = requests.post(
                self.url,
                data=payload,
                headers=headers,
                timeout=self.timeout,
            )

            if 200 <= response.status_code < 300:
                logger.info(
                    f"Successfully posted batch of {len(vcons)} vCons to webhook"
                )
                return True
            else:
                logger.warning(
                    f"Webhook batch request returned status {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Error posting batch to webhook: {str(e)}")
            return False

    def _build_headers(self, custom_headers: Optional[dict] = None) -> dict:
        """Build HTTP headers for webhook request"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "vcon-elevenlabs-adapter/0.1.0",
        }

        if self.auth_type == "bearer" and self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.auth_type == "api-key" and self.api_key:
            headers["X-API-Key"] = self.api_key

        if custom_headers:
            headers.update(custom_headers)

        return headers

    def verify_webhook(self) -> bool:
        """
        Verify that the webhook endpoint is accessible

        Returns:
            True if webhook is accessible, False otherwise
        """
        try:
            test_payload = {"test": True}
            headers = self._build_headers()

            response = requests.post(
                self.url,
                data=json.dumps(test_payload),
                headers=headers,
                timeout=self.timeout,
            )

            if 200 <= response.status_code < 300:
                logger.info("Webhook verification successful")
                return True
            else:
                logger.warning(f"Webhook returned unexpected status: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Webhook verification failed: {str(e)}")
            return False
