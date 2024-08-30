from abc import ABC, abstractmethod
from typing import Iterator, List
from config.system_config import SystemConfig

class ImboxExtractor(ABC):
    @abstractmethod
    def _email_generator(self) -> Iterator[bytes]:
        pass

    @abstractmethod
    def extract_emails(self, show_progress: bool = True, num_workers: int = SystemConfig.MAX_WORKERS) -> List[str]:
        pass