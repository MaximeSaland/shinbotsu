from typing import Optional
from abc import ABC, abstractmethod

import logging


class BaseApiExctractor(ABC):
    def __init__(self, base_url: str, headers: Optional[dict[str, str]]) -> None:
        self.base_url = base_url
        self.headers = headers
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def fetch_data(
        self, endpoint: str, params: Optional[dict[str, str | int]], retry: int
    ) -> None:
        """Fetch data from an API given a specific endpoint

        Args:
            endpoint (str): api endpoint
            params (Optional[dict[str, str  |  int]]): request parameters
        """
        pass
