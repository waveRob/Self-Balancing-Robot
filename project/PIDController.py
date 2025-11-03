

class PIDController:
    def __init__(self, k_p, k_d, k_i, e_int_max, dt):
        
        self.dt = dt
        self.k_p = k_p
        self.k_d = k_d
        self.k_i = k_i
        self.e_int_max = e_int_max
        
        self.e_int = 0
        self.e_pre = 0
        
    def step(self, error):
    
        e = error
        self.e_int += e * self.dt
        self.e_int = min(self.e_int_max, self.e_int)
        self.e_int = max(-self.e_int_max, self.e_int)
        e_diff = (e - self.e_pre) / self.dt
        self.e_pre = e
        
        u_p = self.k_p * e
        u_d = self.k_d * e_diff
        u_i = self.k_i * self.e_int
        u = u_p + u_d + u_i
        
        return u
        
        