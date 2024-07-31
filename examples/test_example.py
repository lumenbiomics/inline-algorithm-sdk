from src.inline_algorithm.PramanaInlineAlgorithmClass import PramanaInlineAlgorithmClass

class TestChildClass(PramanaInlineAlgorithmClass):
    def __init__(self, port, host, docker_mode=True):
        super().__init__(port, host, docker_mode)
    
    def process(self, message):
        return [[1, 2, 1, 'test_output']]

if __name__== '__main__':
    obj = TestChildClass(8000, 'localhost', docker_mode=False)
    obj.run()