import os
import sys
import time
import logging
from prometheus_client import start_http_server, Gauge
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data import SimulationData, Config
from components.brain import Brain
from components.machine import Machine
from components.output import Outputs

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == "__main__":

    MACHINE_ID = os.getenv("MACHINE_ID", "STROJ_DEFAULT")
    HALL = os.getenv("HALL", "HALL_DEFAULT")
    TARGET_PRESSURE = int(os.getenv("PRESSURE", 5000))

    try:
        start_http_server(8000, addr='0.0.0.0')
        logging.info(f"Prometheus server bezi na portu 8000 pro {MACHINE_ID}")
    except Exception as e:
        logging.error(f"Chyba při zapínání serveru: {e}")
        sys.exit(1)
 
    PRESSURE_METRIC = Gauge("aktualni_tlak_stroj", "Aktuální tlak stroje.", ["machine_id", "hall"])
    AVG_PRESSURE_METRIC = Gauge("prumer_tlak_stroj", "Průběrný tlak stroje.", ["machine_id", "hall"])
 
    data = SimulationData()
    cfg = Config()

    machine = Machine(data, cfg)
    brain = Brain(cfg, data, TARGET_PRESSURE)
    outputs = Outputs(cfg, data, PRESSURE_METRIC, AVG_PRESSURE_METRIC)
 
    machine.start()

    try:

        while data.state != data.STOP:
            machine.states()
            machine.step()
            brain.avg_pressure_func()
            brain.check()
            brain.brain()
            
            #outputs.message()
            outputs.send_telegram_message()
            outputs.prometeus()

            time.sleep(3)
            
    except Exception as e:
        print("Error: " , e)