from data import SimulationData, Config
from common import alerts

class Outputs:
    def __init__(self, cfg: Config, data: SimulationData, p_metric, avg_metric):
        self.data = data
        self.cfg = cfg
        self.machine_id = cfg.MACHINE_ID
        self.hall = cfg.HALL
        self.p_metric = p_metric
        self.avg_metric = avg_metric

    def send_telegram_message(self):
        if self.data.msg != "":
            alerts.TelegramAlert.send_alert(self.machine_id, self.hall, self.data.msg)
        self.data.msg = ""
 
    def prometeus(self):
        self.p_metric.labels(machine_id=self.machine_id, hall=self.hall).set(self.data.current_pressure)
        self.avg_metric.labels(machine_id=self.machine_id, hall=self.hall).set(self.data.avg_pressure)
 
    def message(self):
        print(f"Machine: {self.machine_id}")
        print(f"Pressure: {self.data.current_pressure}")
        print(f"Avg. Pressure: {self.data.avg_pressure}")
        print(f"Median: {self.data.median}   |   {self.data.diff}")
        print(f"State: {self.data.state}")
        print(f"Points: {self.data.checked_pressures}")
        print("-" * 20)