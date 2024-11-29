import matrix

class KalmanFilter:
    def __init__(self, dt=1, x0=68, x0_acc=0.5):
        '''
        x0 -- initial position (temperature) [F]
        v0 -- initial velocity [F/sec]
        a0 -- initial acceleration [F/sec^2]
        x0_acc -- initial position accuracy (1-standard deviation) [F]
        v0_acc -- initial velocity accuracy (1-standard deviation) [F/sec]
        a0_acc -- initial acceleration accuracy (1-standard deviation) [F/sec^2]
        '''
        
        # State
        self.x = [x0, 0, 0]
        
        # State covariance
        self.P = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]
    
        # Process model (state transition matrix)
        self.F = [
            [1, dt, 0.5 * dt ** 2],
            [0, 1, dt],
            [0, 0, 1]
        ]
        
        # Process noise covariance
        self.Q = [
            [x0_acc, 0, 0],
            [0, x0_acc**2, 0],
            [0, 0, x0_acc**3]
        ]
        
        # Measurement matrix
        self.H = [
            [1, 0, 0]
        ]
        
        # Measurement noise covariance matrix
        self.R = [
            [x0_acc ** 2]
        ]
        
        # Identity matrix
        self.I = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]
    
    def predict(self):
        '''
        Predict the next state
        '''
        
        # State prediction x = Fx
        self.x = matrix.multiply(self.F, self.x)
        
        # Covariance prediction P = FPF^T + Q
        F_T = matrix.transpose(self.F)
        FP = matrix.multiply(self.F, self.P)
        FPF_T = matrix.multiply(FP, F_T)
        self.P = matrix.add(FPF_T, self.Q)
        

    def update(self, z):
        '''
        Update the state with a measurement
        '''
        
        # Predict the next state before updating
        self.predict()
        
        # Measurement residual y = z - Hx
        y = matrix.subtract([z], matrix.multiply(self.H, self.x))
        
        # Measurement residual covariance S = HPH^T + R
        H_T = matrix.transpose(self.H)
        HP = matrix.multiply(self.H, self.P)
        HPH_T = matrix.multiply(HP, H_T)
        S = matrix.add(HPH_T, self.R)
        
        # Kalman gain K = PH^TS^-1
        # S_inv = matrix.invert(S)
        S_inv = [1 / S[0]]
        H_T = matrix.transpose(self.H)
        PH_T = matrix.multiply(self.P, H_T)
        K = matrix.multiply(PH_T, S_inv)
        
        # Update state x = x + Ky
        self.x = matrix.add(self.x, matrix.multiply(K, y))
        
        # Update covariance P = (I - KH)P
        KH = matrix.multiply(K, self.H)
        I_KH = matrix.subtract(self.I, KH)
        self.P = matrix.multiply(I_KH, self.P)


if __name__ == "__main__":
    kf = KalmanFilter()
    
    measurements = [68.1, 70.5, 74, 78.5, 82.8, 86.1, 90]
    
    for z in measurements:
        kf.update(z)
        
        print(f'x: {kf.x[0]:.2f} v: {kf.x[1]:.2f} a: {kf.x[2]:.2f}')
