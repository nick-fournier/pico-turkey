import utime

class MAX6675:
    MEASUREMENT_PERIOD_MS = 220

    def __init__(self, sck, cs, so):
        """
        Creates a new object for controlling MAX6675
        :param sck: SCK (clock) pin, must be configured as Pin.OUT
        :param cs: CS (select) pin, must be configured as Pin.OUT
        :param so: SO (data) pin, must be configured as Pin.IN
        """
        # Thermocouple
        self._sck = sck
        self._sck.low()

        self._cs = cs
        self._cs.high()

        self._so = so
        self._so.low()

        self._last_measurement_start = 0
        self._last_read_temp = 0
        self._error = 0

    def _cycle_sck(self):
        """
        Helper method to cycle the SCK (clock) signal.
        """
        self._sck.high()
        utime.sleep_us(1)
        self._sck.low()
        utime.sleep_us(1)

    def refresh(self):
        """
        Start a new measurement.
        """
        self._cs.low()
        utime.sleep_us(10)
        self._cs.high()
        self._last_measurement_start = utime.ticks_ms()

    def ready(self):
        """
        Signals if the measurement is finished.
        :return: True if the measurement is ready for reading.
        """
        return utime.ticks_ms() - self._last_measurement_start > MAX6675.MEASUREMENT_PERIOD_MS

    def error(self):
        """
        Returns the error bit of the last reading. If this bit is set (=1), there's a problem with the
        thermocouple - it can be damaged or loosely connected.
        :return: Error bit value
        """
        return self._error

    def read(self):
        """
        Reads the last measurement and starts a new one. If a new measurement is not ready yet, it returns the last value.
        Note: The last measurement can be quite old (e.g., since the last call to `read`).
        To refresh the measurement, call `refresh` and wait for `ready` to become True before reading.
        :return: Measured temperature
        """
        # Check if a new reading is available
        if self.ready():
            # Bring CS pin low to start the protocol for reading the result of
            # the conversion process. Forcing the pin down outputs
            # the first (dummy) sign bit 15.
            self._cs.low()
            utime.sleep_us(10)

            # Read temperature bits 14-3 from MAX6675.
            value = 0
            for i in range(12):
                # SCK should resemble the clock signal, and the new SO value
                # is presented at the falling edge.
                self._cycle_sck()
                value += self._so.value() << (11 - i)

            # Read the TC Input pin to check if the input is open.
            self._cycle_sck()
            self._error = self._so.value()

            # Read the last two bits to complete the protocol.
            for i in range(2):
                self._cycle_sck()

            # Finish the protocol and start a new measurement.
            self._cs.high()
            self._last_measurement_start = utime.ticks_ms()

            self._last_read_temp = value * 0.25

        return self._last_read_temp