import json

class SensorDataPacket:
    
    linear_acceleration = (0, 0, 0)   # x, y, z
    angular_acceleration = (0, 0, 0)  # roll, pitch, yaw
    pwm = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    
    def toJSON(self):
            return json.dumps(self, default=lambda o: o.__dict__, 
                sort_keys=True, indent=1)

