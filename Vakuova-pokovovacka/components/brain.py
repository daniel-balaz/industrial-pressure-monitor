# IMPORT
import numpy as np
import logging

from data import SimulationData, Config

Config.setup_logging()

class Logic:
    def __init__(self, cfg: Config, data: SimulationData, TARGET_PRESSURE: int):
        self.cfg = cfg
        self.data = data
        self.TARGET_PRESSURE = TARGET_PRESSURE

    def avg_pressure_func(self):
        # KEEPING "latest_pressure_list" LENGTH UNDER 10 FOR EASY CHANGE
        self.data.latest_pressure_list.append(round(self.data.current_pressure, 2))
        if len(self.data.latest_pressure_list) > 10:
            self.data.latest_pressure_list.pop(0)

    # USING MEDIAN TO SEE THE REAL MIDDLE
        diff = self.data.current_pressure - self.TARGET_PRESSURE

        self.data.diff.append(round(diff, 2))

        if len(self.data.diff) > 10:
            self.data.diff.pop(0)
            
        self.data.median = float(np.median(self.data.diff))

    # PREVENTION OF DIVISION BY ZERO
        if len(self.data.latest_pressure_list) > 0:
            self.data.avg_pressure = sum(self.data.latest_pressure_list) / len(self.data.latest_pressure_list)
        self.data.avg_pressure = round(self.data.avg_pressure, 2)
 
    def check(self):
        # USING "avg_pressure" IF MEDIAN WON'T BE USABLE
        if self.data.median is not None:
            check = self.data.median + self.cfg.TARGET_PRESSURE
        else:
            check = self.data.avg_pressure
        
        # ADDING WEIGHT TO "over_pressured" BASED ON THE SEVERITY OF THE PRESSURE CONDITION
        if check > self.TARGET_PRESSURE * self.cfg.LIMIT_EMERGENCY:
            self.data.over_pressured.append(self.cfg.EMERGENCY)
        elif check > self.TARGET_PRESSURE * self.cfg.LIMIT_CRITICAL:
            self.data.over_pressured.append(self.cfg.CRITICAL)
        elif check > self.TARGET_PRESSURE * self.cfg.LIMIT_ERROR:
            self.data.over_pressured.append(self.cfg.ERROR)
        elif check > self.TARGET_PRESSURE * self.cfg.LIMIT_WARNING:
            self.data.over_pressured.append(self.cfg.WARNING)
        elif check > self.TARGET_PRESSURE * self.cfg.LIMIT_NOTICE:
            self.data.over_pressured.append(self.cfg.NOTICE)

        # RESETTING "over_pressured" IF "avg_pressure" GET INTO NORMAL STATE
        if self.data.avg_pressure < self.TARGET_PRESSURE + (self.TARGET_PRESSURE * 0.02):
            self.data.over_pressured = []

        # KEEPING THE LENGTH OF "over_pressured" UNDER 6
        if len(self.data.over_pressured) >= 6:
            self.data.over_pressured.pop(0)

        # I CREATED A POINT SYSTEM FOR BETTER WORK WITH STATE OF PRESSURE AND TO REDUCE NOISE
        if self.data.over_pressured:
            self.data.checked_pressures = sum(self.data.over_pressured) / len(self.data.over_pressured)
        else:
            self.data.checked_pressures = 0.0
 
        self.data.checked_pressures = round(self.data.checked_pressures, 1)


    def brain(self):
        # SENDING ALERTS BASED ON POINT SYSTEM
        if self.data.checked_pressures >= self.cfg.EMERGENCY_LEVEL:
            self.data.msg = f"!!! VYPÍNÁNÍ !!!\nTlak překročil maximální limit. | {self.data.current_pressure} Pa |"
            self.data.state = self.cfg.STOP
            logging.critical(f"VYPÍNÁNÍ - {self.data.current_pressure} Pa")

        elif self.data.checked_pressures >= self.cfg.CRITICAL_LEVEL and not self.data.alert_lvl_three:
            self.data.msg = f"!!! KRITICKÉ !!!\nTlak nekontrolovatelně roste.\nOkamžitě vypněte stroj a proveďte kontrolu."
            self.data.alert_lvl_three = True
            logging.warning(f"KRITICKÝ STAV - {self.data.current_pressure} Pa")

        elif self.data.checked_pressures >= self.cfg.WARNING_LEVEL and not self.data.alert_lvl_two:
            self.data.msg = f"!!! VAROVÁNÍ !!!\nTlak nebezpečně roste.\nDoporučená kontrola."
            self.data.alert_lvl_two = True
            logging.warning(f"VAROVÁNÍ - {self.data.current_pressure} Pa")

        elif self.data.current_pressure >= self.cfg.NOTICE_LEVEL and not self.data.alert_lvl_one:
            self.data.msg = f"!!! OZNÁMENÍ !!!\nTlak opustil NORMALNÍ stav."
            self.data.alert_lvl_one = True
            logging.warning("OZNÁMENÍ")
        
        if self.data.current_pressure > self.data.avg_pressure * 1.5:
            logging.warning(f"Abnormální skok tlaku: {self.data.current_pressure} Pa")
        