
class ExponentialMovingAverage:
    def __init__(self, alpha):
        """
        Initialize the EMA calculator.

        :param alpha: Smoothing factor (0 < alpha ≤ 1).
        
        Higher alpha discounts older observations faster.
        
        """
        if not (0 < alpha <= 1):
            raise ValueError("Alpha must be in the range (0, 1].")
        self.alpha = alpha
        self.ema = None

    def update(self, value):
        """
        Update the EMA with a new value.

        :param value: New data point.
        :return: Updated EMA.
        """
        if self.ema is None:
            # Initialize EMA with the first value
            self.ema = value
        else:
            # Update EMA
            self.ema = self.alpha * value + (1 - self.alpha) * self.ema
        return self.ema
