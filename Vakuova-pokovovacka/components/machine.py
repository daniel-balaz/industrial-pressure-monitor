import random
import time
import logging
import os
from data import Config, SimulationData

Config.setup_logging()

class Machine:
    def __init__(self, data: SimulationData, cfg: Config):
        self.data = data
        self.cfg = cfg
        self.TARGET_PRESSURE = cfg.TARGET_PRESSURE

    def start(self):
        # ONLY WHEN "current_pressure" IS ABOVE "TARGET_PRESSURE"
        while self.data.current_pressure > self.TARGET_PRESSURE:
            logging.info(f"Starting... Current pressure: {round(self.data.current_pressure)} Pa")
            self.data.current_pressure -= (self.data.current_pressure * 0.2) + random.randint(700, 1000) # ADDING SOME NOISE BY USING RANDOM SO EVERY START WILL BE DIFFERENT
            time.sleep(3)
 
    def states(self):
        # USING RANDOM CHANCE TO GENERATE ERROR OR DEGRADATION
        if self.data.state == self.cfg.NORMAL and random.random() < float(os.getenv("CHANCE_OF_ERROR", 0.001)):
            self.data.state = self.cfg.PRESSURE_ERROR
        if self.data.degradation == 0.0 and random.random() < 0.005:
            self.data.degradation = random.uniform(5, 10)
 
    def step(self):
        random_num = random.uniform(5, 20)
        diff = random.uniform(0.05, 0.1)
        # MAIN PRESSURE CALCULATION
        if self.data.state == self.cfg.NORMAL:
            # IF "current_pressure" IS BELOW OR ABOVE "TARGET_PRESSURE", THIS PART WILL TRY TO GET IT AS CLOSE AS POSSIBLE TO "TARGET_PRESSURE"
            if self.data.current_pressure < self.TARGET_PRESSURE:
                self.data.current_pressure = self.data.degradation + (self.data.current_pressure + (((self.TARGET_PRESSURE - self.data.current_pressure) * diff) + random_num))

            elif self.data.current_pressure >= self.TARGET_PRESSURE:
                self.data.current_pressure = self.data.degradation + (self.data.current_pressure - (((self.data.current_pressure - self.TARGET_PRESSURE) * diff) + random_num))

        elif self.data.state == self.cfg.PRESSURE_ERROR:
            diff_error = random.uniform(10.0, 60.0)
            # IF "state" IS "PRESSURE_ERROR", THIS PART WILL ALSO TRY TO GET CLOSE TO THE "TARGET_PRESSURE" BUT BECAUSE OF "diff_error" AND "noise" IT WILL BECOME IMPOSSIBLE AFTER FEW ROUNDS IN THIS STATE
            if self.data.current_pressure < self.TARGET_PRESSURE:
                self.data.current_pressure = diff_error + (self.data.degradation + self.data.current_pressure + (((self.TARGET_PRESSURE - self.data.current_pressure) * diff) + random_num))
                self.data.current_pressure += self.data.current_pressure * self.data.noise
            elif self.data.current_pressure >= self.TARGET_PRESSURE:
                self.data.current_pressure = diff_error + (self.data.degradation + self.data.current_pressure - (((self.data.current_pressure - self.TARGET_PRESSURE) * diff) + random_num))
                self.data.current_pressure += self.data.current_pressure * self.data.noise
            self.data.noise = min(self.data.noise * 1.01, 100.0) # THIS WILL MAKE SURE THAT TME MACHINE WITH "PRESSURE_ERROR" WILL FAIL TO GET TO THE "TARGET_PRESSURE"
        self.data.current_pressure = round(self.data.current_pressure, 2)