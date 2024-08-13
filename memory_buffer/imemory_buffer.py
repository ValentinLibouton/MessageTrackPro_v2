from abc import ABC, abstractmethod

class IMemoryBuffer(ABC):
    @abstractmethod
    def add_data(self, data):
        pass

    @abstractmethod
    def flush_buffer(self):
        pass

    @abstractmethod
    def get_current_memory_usage(self):
        pass

    @abstractmethod
    def get_buffer_size(self):
        pass
