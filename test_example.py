from PramanaInlineAlgorithmClass import PramanaInlineAlgorithmClass

class TestChildClass(PramanaInlineAlgorithmClass):
    def __init__(self, port, host, docker_mode=False):
        super().__init__(port, host, docker_mode)
    
    def process(self, path):
        return [[1, 2, 1, 'test_output']]

if __name__== '__main__':
    obj = TestChildClass(8000, 'localhost')
    obj.run()