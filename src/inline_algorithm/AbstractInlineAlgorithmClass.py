from abc import ABC, abstractmethod

class AbstractInlineAlgorithmClass(ABC):

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def on_server_start(self):
        pass

    @abstractmethod
    def on_server_end(self):
        pass

    @abstractmethod
    def on_scan_start(self):
        pass

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def on_scan_end(self):
        pass

    @abstractmethod
    def on_scan_abort(self):
        pass