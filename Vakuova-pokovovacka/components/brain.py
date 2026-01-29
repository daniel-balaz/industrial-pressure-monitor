import numpy as np
from data import SimulationData, Config

class Brain:
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
        if len(self.data.diff) == 11:
            self.data.diff.pop(0)
            
        self.data.median = float(np.median(self.data.diff))

        if sum(self.data.latest_pressure_list) > 0.0:
            self.data.avg_pressure = sum(self.data.latest_pressure_list) / len(self.data.latest_pressure_list)
        self.data.avg_pressure = round(self.data.avg_pressure, 2)
 
    def check(self):
        if self.data.median == None:
            if self.TARGET_PRESSURE * self.cfg.LIMIT_EMERGENCY < self.data.avg_pressure:
                self.data.over_pressured.append(5)
            elif self.TARGET_PRESSURE * self.cfg.LIMIT_ERROR < self.data.avg_pressure:
                self.data.over_pressured.append(3)
            elif self.TARGET_PRESSURE * self.cfg.LIMIT_WARNING < self.data.avg_pressure:
                self.data.over_pressured.append(2)
            elif self.TARGET_PRESSURE * self.cfg.LIMIT_NOTICE < self.data.avg_pressure:
                self.data.over_pressured.append(1)
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

        if self.data.current_pressure < self.data.avg_pressure and self.data.current_pressure < self.TARGET_PRESSURE + (self.TARGET_PRESSURE * 0.01):
            self.data.over_pressured = []

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
        elif self.data.checked_pressures >= 3.0 and not self.data.alert_lvl_three:
            self.data.msg = f"!!! KRITICKÉ !!!\nTlak nekontrolovatelně roste.\nOkamžitě vypněte stroj a proveďte kontrolu."
            self.data.alert_lvl_three = True
        elif self.data.checked_pressures >= 2.0 and not self.data.alert_lvl_two:
            self.data.msg = f"!!! VAROVÁNÍ !!!\nTlak nebezpečně roste.\nProveďte kontrolu nejdříve jak to bude možné."
            self.data.alert_lvl_two = True
        elif self.data.current_pressure > self.TARGET_PRESSURE * 1.5 and self.data.median is not None and self.data.median < self.TARGET_PRESSURE * 1.1 and not self.data.alert_lvl_one:
            self.data.msg = f"!!! OZNÁMENÍ !!!\nZkontrolujte senzor."
            self.data.alert_lvl_one = True