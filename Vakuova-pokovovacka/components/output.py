# IMPORT
import logging

from data import SimulationData, Config
from common import alerts

Config.setup_logging()

class Outputs:
    def __init__(self, cfg: Config, data: SimulationData, p_metric, avg_metric):
        self.data = data
        self.cfg = cfg
        self.machine_id = cfg.MACHINE_ID
        self.hall = cfg.HALL
        self.p_metric = p_metric
        self.avg_metric = avg_metric

    def send_telegram_message(self):
        # SENDING ALERT VIA TELEGRAM 
        if self.data.msg != "":
            alerts.TelegramAlert.send_alert(self.machine_id, self.hall, self.data.msg)
        self.data.msg = ""
 
    def prometheus(self):
        # UPDATING PROMETHEUS METRICS
        self.p_metric.labels(machine_id=self.machine_id, hall=self.hall).set(self.data.current_pressure)
        self.avg_metric.labels(machine_id=self.machine_id, hall=self.hall).set(self.data.avg_pressure)
    
    # FOR DEBUGGING ONLY - THESE LOGS WON'T BE VISIBLE IF logging level IS SET TO "INFO"
    def message(self):
        logging.debug(f"Machine: {self.machine_id}")
        logging.debug(f"Pressure: {self.data.current_pressure}")
        logging.debug(f"Avg. Pressure: {self.data.avg_pressure}")
        logging.debug(f"Median: {self.data.median}")
        logging.debug(f"State: {self.data.state}")
        logging.debug(f"Points: {self.data.checked_pressures}")