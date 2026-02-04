import logging

# Nastavení: kam to jde a jak moc podrobně
logging.basicConfig(
    level=logging.INFO, # Vypíše vše od INFO výše (přeskočí DEBUG)
    format='%(asctime)s - %(levelname)s - %(message)s' # Formát: Čas - Úroveň - Zpráva
)

# Použití v kódu
while True:
    logging.info("Tady startuje tvoje simulace tlaku")
logging.warning("Pozor, tlak se blíží k limitu!")