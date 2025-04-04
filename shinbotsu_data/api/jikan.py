import time
from enum import Enum

from shinbotsu_data.api.extractor import BaseApiExctractor

from typing import Optional, Any
import requests


class JikanEndpoints(str, Enum):
    ANIME = "anime"
    MANGA = "manga"
    TAG_ANIME = "genres/anime"
    TAG_MANGA = "genres/manga"
    PRODUCERS = "producers"
    MAGAZINES = "magazines"
    PEOPLE = "people"


class JikanApiExtractor(BaseApiExctractor):
    def __init__(self) -> None:
        super().__init__(
            base_url="https://api.jikan.moe/v4", headers={"Accept": "application/json"}
        )

    def fetch_data(
        self, endpoint: str, params: Optional[dict[str, str | int]], retry: int = 3
    ) -> Any:
        url = f"{self.base_url}/{endpoint}"
        time.sleep(1)
        for attempt in range(retry):
            try:
                self.logger.debug(
                    f"Attempting to fetch ressource on {endpoint} with params {params}"
                )
                response = requests.get(
                    url, headers=self.headers, params=params, timeout=1
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout as e:
                self.logger.error(f"Request to {url} timed out: {e}.")
                self.logger.warning(f"Retrying {attempt + 1}/{retry}")
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 404:
                    self.logger.error(f"Resource was not found for {url}: {e}")
                    return None
                elif status_code == 429:
                    self.logger.warning(f"Rate limit reached: {e}")
                elif status_code == 500:
                    self.logger.error(f"Internal server error: {e}")
                elif status_code == 503:
                    self.logger.error(f"Service unavailble: {e}")
                self.logger.warning(f"Retrying {attempt + 1}/{retry}")
            except (
                requests.exceptions.RequestException,
                requests.exceptions.JSONDecodeError,
            ) as e:
                self.logger.error(f"Other error occured: {e}")
                return None
            time.sleep(2**attempt)
        self.logger.error(f"Failed to fetch data from {url} after {retry} attempts")
        return None
