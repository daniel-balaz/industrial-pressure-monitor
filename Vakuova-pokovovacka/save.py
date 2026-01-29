# IMPORTS
import random
import time
import os
import sys
import requests
from prometheus_client import start_http_server, Gauge
import numpy as np
from dataclasses import dataclass, field
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import alerts

@dataclass
class Config:
    # THRESHOLD
    LIMIT_NOTICE: float = 1.02
    LIMIT_WARNING: float = 1.04
    LIMIT_ERROR: float = 1.06
    LIMIT_CRITICAL: float = 1.08
    LIMIT_EMERGENCY: float = 1.14

@dataclass
class SimulationData():
    # Ostatní proměnné
    over_pressured: list = field(default_factory=list)
    checked_pressures: float = 0.0
    degradation: float = 0.0
    noise: float = 0.001
    step_over_pressured_count: float = 0

    # PRESSURE
    current_pressure: float = 4999.0#101325.0

    max_pressure: float = 0.0
    min_pressure: float = 0.0
    avg_pressure: float = 0.0
    latest_pressure_list: list = field(default_factory=list)
    diff: list = field(default_factory=list)
    median: float | None = None

    # ALERTS & STATES
    alert_lvl_one: bool = False
    alert_lvl_two: bool = False
    alert_lvl_three: bool = False
    alert_lvl_four: bool = False
    starting_allers: bool = False
    msg: str = ""

    # STATES
    NORMAL: str = "NORMAL"
    PRESSURE_ERROR: str = "PRESSURE ERROR"
    STOP: str = "STOP"
    state: str = "NORMAL"

class Outputs():
    def __init__(self, data: SimulationData):
        self.data = data

    def send_telegram_message(self):
        if self.data.msg != "":
   
            alerts.TelegramAlert.send_alert(MACHINE_ID, HALL, self.data.msg)
        
        self.data.msg = ""
 
    def prometeus(self):
        PRESSURE_METRIC.labels(machine_id=MACHINE_ID, hall=HALL).set(self.data.current_pressure)
        AVG_PRESSURE_METRIC.labels(machine_id=MACHINE_ID, hall=HALL).set(self.data.avg_pressure)
 
    def message(self):
        print(f"Machine: {MACHINE_ID}")
        print(f"Pressure: {self.data.current_pressure}")
        print(f"Avg. Pressure: {self.data.avg_pressure}")
        print(f"Median: {self.data.median}   |   {self.data.diff}")
        print(f"State: {self.data.state}")
        print(f"Points: {self.data.checked_pressures}")
        print(f"List: {self.data.latest_pressure_list}")
        if self.data.msg != "":
            print(f"MSG: {self.data.msg}")
        print("-" * 20)
 
class Machine():
    def __init__(self, data: SimulationData, cfg: Config, TARGET_PRESSURE: int):
        self.data = data
        self.cfg = cfg
        self.TARGET_PRESSURE = TARGET_PRESSURE

    def start(self):
        while self.data.current_pressure > self.TARGET_PRESSURE:
            msg = "Starting..."
            print(msg, round(self.data.current_pressure))
            self.data.current_pressure -= (self.data.current_pressure * 0.2) + random.randint(700, 1000)
            time.sleep(2)
 
    def states(self):
        if self.data.state == self.data.NORMAL and random.random() < 0.005:
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
            self.data.noise = self.data.noise * 1.01
        self.data.current_pressure = round(self.data.current_pressure, 2)

class Brain():
    def __init__(self, cfg: Config, data: SimulationData, TARGET_PRESSURE: int):
        self.cfg = cfg
        self.data = data
        self.TARGET_PRESSURE = TARGET_PRESSURE

    def avg_pressure_func(self):
        self.data.latest_pressure_list.append(round(self.data.current_pressure, 2))
        if len(self.data.latest_pressure_list) > 10:
            self.data.latest_pressure_list.pop(0)

        diff = self.data.current_pressure - self.TARGET_PRESSURE
        self.data.diff.append(round(diff, 2))
        self.data.median = np.median(self.data.diff)

        if len(self.data.diff) == 11:
            self.data.diff.pop(0)
            


        if sum(self.data.latest_pressure_list) > 0.0:
            self.data.avg_pressure = sum(self.data.latest_pressure_list) / len(self.data.latest_pressure_list)
        self.data.avg_pressure = round(self.data.avg_pressure, 2)
 
    def check(self):
        # AVG CHECKING
        if self.data.median == None:
            if self.TARGET_PRESSURE * self.cfg.LIMIT_EMERGENCY < self.data.avg_pressure:
                self.data.over_pressured.append(5)

            elif self.TARGET_PRESSURE * self.cfg.LIMIT_ERROR < self.data.avg_pressure:
                self.data.over_pressured.append(3)

            elif self.TARGET_PRESSURE * self.cfg.LIMIT_WARNING < self.data.avg_pressure:
                self.data.over_pressured.append(2)

            elif self.TARGET_PRESSURE * self.cfg.LIMIT_NOTICE < self.data.avg_pressure:
                self.data.over_pressured.append(1)
        
        # MEDIAN CHECKING
        else:
            if self.data.median + self.TARGET_PRESSURE > self.TARGET_PRESSURE * self.cfg.LIMIT_EMERGENCY:
                self.data.over_pressured.append(5)

            elif self.data.median + self.TARGET_PRESSURE > self.TARGET_PRESSURE * self.cfg.LIMIT_CRITICAL:
                self.data.over_pressured.append(4)

            elif self.data.median + self.TARGET_PRESSURE > self.TARGET_PRESSURE * self.cfg.LIMIT_ERROR:
                self.data.over_pressured.append(3)

            elif self.data.median + self.TARGET_PRESSURE > self.TARGET_PRESSURE * self.cfg.LIMIT_WARNING:
                self.data.over_pressured.append(2)

            elif self.data.median + self.TARGET_PRESSURE > self.TARGET_PRESSURE * self.cfg.LIMIT_NOTICE:
                self.data.over_pressured.append(1)

   
        # OVER HEAT RESET
        if self.data.current_pressure < self.data.avg_pressure and self.data.current_pressure < self.TARGET_PRESSURE + (self.TARGET_PRESSURE * 0.01):
            try:
                self.data.over_pressured = []
            except Exception as e:
                print("Nastala chyba: " , e)
        try:
            self.data.checked_pressures = sum(self.data.over_pressured) / len(self.data.over_pressured)
        except:
            self.data.checked_pressures = 0.0
 
        self.data.checked_pressures = round(self.data.checked_pressures, 2)
 
        if len(self.data.over_pressured) >= 6:
            self.data.over_pressured.pop(0)
   
    def brain(self):
        if self.data.checked_pressures >= 4.5:
            self.data.msg = f"!!! VYPÍNÁNÍ !!!\nTlak překrořil maximalní tlak - {self.data.current_pressure} Pa"
            self.data.state = self.data.STOP
 
        elif self.data.checked_pressures >= 3.0 and self.data.alert_lvl_three == False:
            self.data.msg = f"!!! KRITICKÉ !!!\nTlak nekontrolovatelně roste.\nOkamžitě vypněte stroj a proveďte kontrolu."
            self.data.alert_lvl_three = True
 
        elif self.data.checked_pressures >= 2.0 and self.data.alert_lvl_two == False:
            self.data.msg = f"!!! VAROVÁNÍ !!!\nTlak nebezpečně roste.\nProveďte kontrolu nejdříve jak to bude možné."
            self.data.alert_lvl_two = True
       
        elif self.data.current_pressure > self.TARGET_PRESSURE * 1.5 and self.data.median != None and self.data.median < self.TARGET_PRESSURE * 1.1 and self.data.alert_lvl_one == False:
            self.data.msg = f"!!! OZNÁMENÍ !!!\nZkontrolujte senzor."
            self.data.alert_lvl_one = True


 
 
if __name__ == "__main__":
 
    MACHINE_ID = os.getenv("MACHINE_ID", "STROJ_DEFAULT")
    HALL = os.getenv("HALL", "HALL_DEFAULT")
    NORMAL_PRESSURE = os.getenv("PRESSURE", 5000)
 
    try:
        start_http_server(8000, addr='0.0.0.0')
        print(f"Prometheus server bezi na portu 8000 pro {MACHINE_ID}")
    except Exception as e:
        print("Chyba při zapínání serveru: ", e)
        sys.exit(1)
 
    PRESSURE_METRIC = Gauge("aktualni_tlak_stroj", "Aktuální tlak stroje.", ["machine_id", "hall"])
    AVG_PRESSURE_METRIC = Gauge("prumer_tlak_stroj", "Průběrný tlak stroje.", ["machine_id", "hall"])
 
    data = SimulationData()
    cfg = Config()

    machine = Machine(data, cfg, NORMAL_PRESSURE)
    outputs = Outputs(data)
    brain = Brain(cfg, data, NORMAL_PRESSURE)
 
    machine.start()
 
    while True:
        machine.states()
        machine.step()
        brain.avg_pressure_func()
        brain.check()
        brain.brain()
        outputs.message()
        #outputs.send_telegram_message()
        #outputs.prometeus()


        if machine.data.state == "STOP":
            sys.exit()
   
        time.sleep(2)