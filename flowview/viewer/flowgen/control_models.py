from ..staticfg import Block


class DecisionBlock(Block):
    """
    A block for non loop control timeline statements
    """

    def __init__(self, id):
        super().__init__(id)
        self.shape = "diamond"
        self.color = "lightblue4"

    def __str__(self):
        return "Decision " + super().__str__()


class LoopBlock(Block):
    """
    A block for loop statements
    """

    def __init__(self, id):
        super().__init__(id)
        self.shape = "oval"
        self.color = "lightblue4"

    def __str__(self):
        return "Loop " + super().__str__()
