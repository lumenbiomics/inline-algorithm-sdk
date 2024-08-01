from abc import ABC, abstractmethod

class AbstractInlineAlgorithm(ABC):

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
    def on_scan_start(self, message):
        pass

    @abstractmethod
    def process(self, message):
        pass

    @abstractmethod
    def on_scan_end(self, message):
        pass

    @abstractmethod
    def on_scan_abort(self, message):
        pass