# IMPORT
from dataclasses import dataclass, field
from typing import List, Optional
import logging
import os

# USING DATACLASSES FOR BETTER READING AND TO KEEP THE CODE CLEAN

@dataclass(frozen=True)
# I SPLIT DATA IN TO TWO CLASSES, STATIC(Config) A DYNAMIC(SimulationData)
class Config():
    # LIMITS
    LIMIT_NOTICE: float = float(os.getenv("LIMIT_NOTICE", 1.02))
    LIMIT_WARNING: float = float(os.getenv("LIMIT_WARNING", 1.04))
    LIMIT_ERROR: float = float(os.getenv("LIMIT_ERROR", 1.06))
    LIMIT_CRITICAL: float = float(os.getenv("LIMIT_CRITICAL", 1.08))
    LIMIT_EMERGENCY: float = float(os.getenv("LIMIT_EMERGENCY", 1.14))

    # MACHINE DATA
    MACHINE_ID: str = os.getenv("MACHINE_ID", "STROJ_DEFAULT")
    HALL: str = os.getenv("HALL", "HALL_DEFAULT")
    TARGET_PRESSURE: float = float(os.getenv("PRESSURE", 5000.0))

    # POINT SYSTEM
    EMERGENCY: int = 5
    CRITICAL: int = 4
    ERROR: int = 3
    WARNING: int = 2
    NOTICE: int = 1

    EMERGENCY_LEVEL: float = 4.5
    CRITICAL_LEVEL: float = 3.5
    WARNING_LEVEL: float = 2.5
    NOTICE_LEVEL: float = 1.5

    # STATES
    NORMAL: str = "NORMAL"
    PRESSURE_ERROR: str = "PRESSURE ERROR"
    STOP: str = "STOP"

    # LOGGING STYLE
    @staticmethod
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

@dataclass
class SimulationData:
    # SIMULATION METRICS & STATISTICS
    over_pressured: List[int] = field(default_factory=list)
    step_over_pressured_count: float = 0
    checked_pressures: float = 0.0
    degradation: float = 0.0 
    noise: float = 0.001

    # MAIN PRESSURE DATA
    current_pressure: float = 4999.0
    max_pressure: float = 0.0
    min_pressure: float = 0.0
    avg_pressure: float = 0.0

    # DATA HISTORY & ANALYSIS
    latest_pressure_list: List[float] = field(default_factory=list)
    diff: List[float] = field(default_factory=list)
    median: Optional[float] = None

    # ALERT SYSTEM
    alert_lvl_one: bool = False
    alert_lvl_two: bool = False
    alert_lvl_three: bool = False
    alert_lvl_four: bool = False
    starting_allers: bool = False
    msg: str = ""

    # STATE
    state: str = Config.NORMAL
