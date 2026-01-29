from dataclasses import dataclass, field
from typing import List, Optional
import os

@dataclass
class Config():
    LIMIT_NOTICE: float = float(os.getenv("LIMIT_NOTICE", 1.02))
    LIMIT_WARNING: float = float(os.getenv("LIMIT_WARNING", 1.04))
    LIMIT_ERROR: float = float(os.getenv("LIMIT_ERROR", 1.06))
    LIMIT_CRITICAL: float = float(os.getenv("LIMIT_CRITICAL", 1.08))
    LIMIT_EMERGENCY: float = float(os.getenv("LIMIT_EMERGENCY", 1.14))

    MACHINE_ID: str = os.getenv("MACHINE_ID", "STROJ_DEFAULT")
    HALL: str = os.getenv("HALL", "HALL_DEFAULT")
    TARGET_PRESSURE: float = float(os.getenv("PRESSURE", 5000.0))

@dataclass
class SimulationData:
    over_pressured: List[int] = field(default_factory=list)
    checked_pressures: float = 0.0
    degradation: float = 0.0 
    noise: float = 0.001
    step_over_pressured_count: float = 0

    current_pressure: float = 4999.0
    max_pressure: float = 0.0
    min_pressure: float = 0.0
    avg_pressure: float = 0.0
    latest_pressure_list: List[float] = field(default_factory=list)
    diff: List[float] = field(default_factory=list)
    median: Optional[float] = None

    alert_lvl_one: bool = False
    alert_lvl_two: bool = False
    alert_lvl_three: bool = False
    alert_lvl_four: bool = False
    starting_allers: bool = False
    msg: str = ""

    NORMAL: str = "NORMAL"
    PRESSURE_ERROR: str = "PRESSURE ERROR"
    STOP: str = "STOP"
    state: str = "NORMAL"