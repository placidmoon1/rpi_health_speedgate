from smbus2 import SMBus
from mlx90614 import MLX90614
from time import sleep
bus = SMBus(1)
sensor = MLX90614(bus, address=0x5A)
while True:
    print ("Ambient Temperature :", sensor.get_ambient())
    print ("Object Temperature :", sensor.get_object_1())
    sleep(1)
bus.close() 