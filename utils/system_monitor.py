import psutil


class SystemMonitor:

    @staticmethod
    def get_ram_usage():
        """Returns the percentage of RAM usage."""
        memory_info = psutil.virtual_memory()
        return memory_info.percent

    @staticmethod
    def get_cpu_usage():
        """Returns the percentage of CPU usage."""
        return psutil.cpu_percent(interval=1)

if __name__ == '__main__':
    ram_usage = SystemMonitor.get_ram_usage()
    cpu_usage = SystemMonitor.get_cpu_usage()
    print(f'RAM usage: {ram_usage}% - CPU usage: {cpu_usage}%')

