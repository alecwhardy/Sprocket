class Dog:
    
    def __init__(self, legs):
        """[summary]

        Args:
            legs (List of Legs): Follow order Front Left, Front Right, Rear Left, Rear Right
        """
        self.legs = legs

    def flatten_shoulders(self, speed):
        for leg in self.legs:
            leg.set_shoulder_position(0, speed)
