# IMPORT
import os
import sys
import time
import logging
from prometheus_client import start_http_server, Gauge
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# IMPORT MODULU
from data import SimulationData, Config
from components.brain import Brain
from components.machine import Machine
from components.output import Outputs

# NASTAVENÍ LOGGING FORMÁTU
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == "__main__":

    # ZÁPIS OZNAČENÍ JEDNOTLIVÉHO STROJE ZE SOUBORU "docker-compose.yml" DO PROMĚNNÝCH 
    MACHINE_ID = os.getenv("MACHINE_ID", "STROJ_DEFAULT")
    HALL = os.getenv("HALL", "HALL_DEFAULT")
    try:
        TARGET_PRESSURE = int(os.getenv("PRESSURE", 5000))
    except ValueError:
        TARGET_PRESSURE = 5000
        logging.warning(f"Chyba v nastavení tlaku na stroji: [{MACHINE_ID}], používám výchozí hodnotu 5000")

    # SPOUŠTĚNÍ PROMETHEUS SERVERU
    try:
        start_http_server(8000, addr='0.0.0.0')
        logging.info(f"Prometheus server bezi na portu 8000 pro {MACHINE_ID}")
    except Exception as e:
        logging.error(f"Chyba při zapínání serveru: {e}")
        sys.exit(1)

    # ZÁPIS DAT DO PROMĚNNÝCH VE FORMÁTU PRO PROMETHEUS
    PRESSURE_METRIC = Gauge("aktualni_tlak_stroj", "Aktuální tlak stroje.", ["machine_id", "hall"])
    AVG_PRESSURE_METRIC = Gauge("prumer_tlak_stroj", "Průběrný tlak stroje.", ["machine_id", "hall"])

    # ULOŽENÍ HLAVNÍCH DAT Z MODULU "data.py" DO PROMĚNNYCH
    data = SimulationData()
    cfg = Config()

    # INICIALIZACE KOMPONENT STROJE (logika, výstupy, simulace)
    machine = Machine(data, cfg)
    brain = Brain(cfg, data, TARGET_PRESSURE)
    outputs = Outputs(cfg, data, PRESSURE_METRIC, AVG_PRESSURE_METRIC)
 
    # JEDNORÁZOVÉ ZAPNUTÍ STARTOVACÍ FUNKCE NA ZAČÁTKU
    machine.start()

    # ZABALENÍ HLAVNÍ ČÁSTI DO FUNKCE WHILE
    while data.state != data.STOP:
        # POŽITÍM FUNKCE "try" & "except" SE ZBAVÍME NEPLÁNOVANÉHO PLNÉHO ZASTAVENI Z DŮVODŮ JAKO KRÁTKODOBÝ VÝPADEK SENZORU
        try:
            # 
            while data.state != data.STOP:
                machine.states()
                machine.step()
                brain.avg_pressure_func()
                brain.check()
                brain.brain()
                
                #outputs.message()
                outputs.send_telegram_message()
                outputs.prometheus()

                time.sleep(3)
                
        except Exception as e:
            # POMOCÍ "logging" PROGRAM VYPÍŠE CHYBU
            logging.error(f"Neočekávaná chyba v běhu stroje: {e}")
            logging.info("Zkouším restartovat sekvenci za 10 sekund...")
            time.sleep(10)
        
    logging.info(f"Stroj {MACHINE_ID} byl úspěšně zastaven.")
