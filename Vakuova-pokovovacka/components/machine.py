import random
import time
import logging
import os
from data import Config, SimulationData

class Machine:
    def __init__(self, data: SimulationData, cfg: Config):
        self.data = data
        self.cfg = cfg
        self.TARGET_PRESSURE = cfg.TARGET_PRESSURE

    def start(self):
        while self.data.current_pressure > self.TARGET_PRESSURE:
            logging.info(f"Starting... Current pressure: {round(self.data.current_pressure)} Pa")
            self.data.current_pressure -= (self.data.current_pressure * 0.2) + random.randint(700, 1000)
            time.sleep(3)
 
    def states(self):
        if self.data.state == self.data.NORMAL and random.random() < float(os.getenv("CHANCE_OF_ERROR", 0.001)):
            self.data.state = self.data.PRESSURE_ERROR
        if self.data.degradation == 0.0 and random.random() < 0.01:
            self.data.degradation = random.uniform(5, 10)
 
    def step(self):
        random_num = random.uniform(5, 20)
        diff = random.uniform(0.05, 0.1)
        if self.data.state == self.data.NORMAL:
            if self.data.current_pressure < self.TARGET_PRESSURE:
                self.data.current_pressure = self.data.degradation + (self.data.current_pressure + (((self.TARGET_PRESSURE - self.data.current_pressure) * diff) + random_num))
            elif self.data.current_pressure >= self.TARGET_PRESSURE:
                self.data.current_pressure = self.data.degradation + (self.data.current_pressure - (((self.data.current_pressure - self.TARGET_PRESSURE) * diff) + random_num))

        elif self.data.state == self.data.PRESSURE_ERROR:
            diff_error = random.uniform(10.0, 60.0)
            if self.data.current_pressure < self.TARGET_PRESSURE:
                self.data.current_pressure = diff_error + (self.data.degradation + self.data.current_pressure + (((self.TARGET_PRESSURE - self.data.current_pressure) * diff) + random_num))
                self.data.current_pressure += self.data.current_pressure * self.data.noise
            elif self.data.current_pressure >= self.TARGET_PRESSURE:
                self.data.current_pressure = diff_error + (self.data.degradation + self.data.current_pressure - (((self.data.current_pressure - self.TARGET_PRESSURE) * diff) + random_num))
                self.data.current_pressure += self.data.current_pressure * self.data.noise
            self.data.noise = min(self.data.noise * 1.01, 100.0)
        self.data.current_pressure = round(self.data.current_pressure, 2)