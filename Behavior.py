from Walk import Walk
import time

class Behavior:
    """ Class that autonomously issues commands.  AI will have control over this.
    """

    def __init__(self, dog):
        self.dog = dog
        self.walk = Walk(dog)

    def behave(self):
        # Main behave function.  This is called every loop cycle.
        pass

    