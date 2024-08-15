'''
Example file illustrating use of the InlineAlgoQueueProcessor base class
'''
from inline_algorithm.inline_algo_queue_processor import InlineAlgoQueueProcessor

class TestChild(InlineAlgoQueueProcessor):
    '''
    Example child class of InlineAlgoQueueProcessor
    '''
    def process(self, message):
        '''
        Method for processing incoming message from the scanner.
        '''
        print(f'Incoming message: {message}')
        return [[1, 2, 1, 'test_output']]

if __name__== '__main__':
    obj = TestChild(8000, 'localhost', docker_mode=False)
    obj.run()
