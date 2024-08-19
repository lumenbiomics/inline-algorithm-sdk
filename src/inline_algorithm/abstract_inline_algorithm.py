'''
This is an abstract base class from which other custom implementations can be derived.
'''

from abc import ABC, abstractmethod

class AbstractInlineAlgorithm(ABC):
    '''
    Abstract Base Class containing methods to use for building the inline
    algorithm container
    '''
    @abstractmethod
    def run(self):
        '''
        To start the API server
        '''
        pass

    @abstractmethod
    def on_server_start(self):
        '''
        To run when the API server starts up
        '''
        pass

    @abstractmethod
    def on_server_end(self):
        '''
        To run when the API server shuts down
        '''
        pass

    @abstractmethod
    def on_scan_start(self, message):
        '''
        Method to run when a scan starts
        '''
        pass

    @abstractmethod
    def process(self, message):
        '''
        Method to run when an AOI or tile is presented
        '''
        pass

    @abstractmethod
    def on_scan_end(self, message):
        '''
        Method to run when a scan ends
        '''
        pass

    @abstractmethod
    def on_scan_abort(self, message):
        '''
        Method to run when a scan aborts
        '''
        pass
