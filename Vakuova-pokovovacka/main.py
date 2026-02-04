# LIBRARY IMPORT
import os
import sys
import time
import logging
from prometheus_client import start_http_server, Gauge
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# MODULE IMPORT
from data import SimulationData, Config
from components.brain import Logic
from components.machine import Machine
from components.output import Outputs

# USING LOGGING FORMAT FROM "Config"
Config.setup_logging()

if __name__ == "__main__":

    # INICIALIZATION MAIN DATA ABOUT MACHINE FROM "docker-compose.yml"
    MACHINE_ID = os.getenv("MACHINE_ID", "STROJ_DEFAULT")
    HALL = os.getenv("HALL", "HALL_DEFAULT")
    try:
        TARGET_PRESSURE = int(os.getenv("PRESSURE", 5000))
    except ValueError:
        TARGET_PRESSURE = 5000
        logging.warning(f"Chyba v nastavení tlaku na stroji: [{MACHINE_ID}], používám výchozí hodnotu 5000")

    # STARTING THE PROMETHEUS SERVER
    try:
        start_http_server(8000, addr='0.0.0.0')
        logging.info(f"Prometheus server bezi na portu 8000 pro {MACHINE_ID}")
    except Exception as e:
        logging.error(f"Chyba při zapínání serveru: {e}")
        sys.exit(1)

    # PREPERING "PRESSURE_METRIC" & "AVG_PRESSURE_METRIC" FOR PROMETHEUS
    PRESSURE_METRIC = Gauge("aktualni_tlak_stroj", "Aktuální tlak stroje.", ["machine_id", "hall"])
    AVG_PRESSURE_METRIC = Gauge("prumer_tlak_stroj", "Průběrný tlak stroje.", ["machine_id", "hall"])

    # INICIALIZATING MAIN DATA FROM MODULE "data.py"
    data = SimulationData()
    cfg = Config()

    # INICIALIZACE KOMPONENT STROJE (logika, výstupy, simulace)
    machine = Machine(data, cfg)
    brain = Logic(cfg, data, TARGET_PRESSURE)
    outputs = Outputs(cfg, data, PRESSURE_METRIC, AVG_PRESSURE_METRIC)
 
    # USING "machine.start()" FUNCTION ONLY ONCE AT STARTUP
    machine.start()

    while data.state != cfg.STOP:
        # USING "try" & "except" TO PREVENT PROGRAM FROM STOPPING COUSED BY SHORT-TERM WIFI OUTAGE
        try:
            while data.state != cfg.STOP:
                machine.states()
                machine.step()
                brain.avg_pressure_func()
                brain.check()
                brain.brain()
                outputs.message()
                outputs.send_telegram_message()
                outputs.prometheus()

                time.sleep(3)
                
        except Exception as e:
            # POUŽIL JSEM "logging" PRO LEPŠÍ PŘEHLED VE VÝPISECH
            logging.error(f"Neočekávaná chyba v běhu stroje: {e}")
            logging.info("Zkouším restartovat sekvenci za 10 sekund...")
            time.sleep(10)
        
    logging.info(f"Stroj {MACHINE_ID} byl úspěšně zastaven.")
