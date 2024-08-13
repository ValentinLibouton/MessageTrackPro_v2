import sys
from .imemory_buffer import IMemoryBuffer

class MemoryBuffer(IMemoryBuffer):
    def __init__(self, memory_limit_gb):
        self.memory_limit = memory_limit_gb * 1024 * 1024 * 1024 # into octets
        self.current_memory = 0
        self.buffer = []

    def add_data(self, data):
        data_size = sys.getsizeof(data)
        if self.current_memory + data_size > self.memory_limit:
            self.flush_buffer()
        self.buffer.append(data)
        self.current_memory += data_size

    def flush_buffer(self):
        print(f"Flushing buffer with {len(self.buffer)} items. Current memory usage: {self.current_memory} bytes.")
        self.buffer = []
        self.current_memory = 0

    def get_current_memory_usage(self):
        return self.current_memory

    def get_buffer_size(self):
        return len(self.buffer)
