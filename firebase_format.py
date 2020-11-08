class firebase_format:
  
  def __init__(self):
    self.cur_temp = 0.0
    self.fine_dust = 0.0
    self.humidity = 0.0
    self.lactation = 0.0
    self.sound = 0.0
    self.temperature = 0.0 
    self.weight = 0.0

  def update_data(self, cur_temp, fine_dust, humidity, 
                  sound, temperature, weight):
    self.cur_temp = float(cur_temp)
    self.fine_dust = float(fine_dust)
    self.humidity = float(humidity)
    self.sound = float(sound)
    self.temperature = float(temperature) 
    self.weight = float(weight)
  
  def return_data(self):
    return {
      'cur_temp': self.cur_temp,
      'fine_dust': self.fine_dust,
      'humidity': self.humidity,
      'sound': self.sound,
      'temperature': self.temperature,
      'weight': self.weight
    }
    