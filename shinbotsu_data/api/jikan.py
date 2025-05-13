import logging
import time


from typing import Optional, Any
import requests


class JikanApiExtractor:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def fetch_data(
        self,
        endpoint: str,
        params: Optional[dict[str, str | int | list[Any]]] = None,
        retry: int = 3,
    ) -> Any:
        for attempt in range(retry):
            if attempt > 0:
                self.logger.warning(f"Retrying (attempt {attempt + 1}/{retry})")
            time.sleep(2**attempt)
            try:
                response = requests.get(
                    endpoint,
                    headers={"Accept": "application/json"},
                    params=params,
                    timeout=3,
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout as e:
                self.logger.error(f"Request to {endpoint} with {params} timed out: {e}")
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 404:
                    self.logger.error(
                        f"Resource was not found for {endpoint} with {params}: {e}"
                    )
                    return {}
                elif status_code == 429:
                    self.logger.warning(f"Rate limit reached: {e}")
                    if attempt < retry - 1:
                        time.sleep(60)
                elif status_code == 500:
                    self.logger.error(f"Internal server error: {e}")
                    if attempt < retry - 1:
                        time.sleep((attempt + 1) * 600)
                elif status_code == 503:
                    if attempt < retry - 1:
                        time.sleep((attempt + 1) * 600)
                    self.logger.error(f"Service unavailable: {e}")
            except (
                requests.exceptions.RequestException,
                requests.exceptions.JSONDecodeError,
            ) as e:
                self.logger.error(f"Other error occurred: {e}")
                return {}
        self.logger.error(
            f"Failed to fetch data from {endpoint} with {params} after {retry} attempts"
        )
        return {}
