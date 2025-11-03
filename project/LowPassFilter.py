class LowPassFilter:
    def __init__(self, Tf, dt):
        self.alpha = Tf / (Tf + dt)
        self.filt_measurement = 0
        
    def step(self, measurement):
        self.filt_measurement = self.alpha*self.filt_measurement + (1 - self.alpha)*measurement
        return self.filt_measurement
    
        
    
        

        