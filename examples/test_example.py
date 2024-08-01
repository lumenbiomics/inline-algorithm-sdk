from inline_algorithm.inline_algo_queue_processor import InlineAlgoQueueProcessor

class TestChild(InlineAlgoQueueProcessor):
    def __init__(self, port, host, docker_mode=True):
        super().__init__(port, host, docker_mode)
    
    def process(self, message):
        return [[1, 2, 1, 'test_output']]

if __name__== '__main__':
    obj = TestChild(8000, 'localhost', docker_mode=False)
    obj.run()