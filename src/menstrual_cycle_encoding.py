"""
This code 
"""

# import libraries
import pandas as pd
import numpy as np
import math
import argparse
from datetime import datetime, timedelta
from settings import Settings

# constante setting
MIN_CYCLE = 10
MAX_CYCLE = 60

def _parse_date(s: str, name: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse {name}='{s}'. Use YYYY-MM-DD format.")


# function for encoding
class CycleEncoding:
    def __init__(self, settings:Settings):
        
        super().__init__()
        self.settings = settings

    def encode_cycle(self,
                     patient_id: str, cycle_num: int, 
                     period_start: str, ovulation_date: str, 
                     cycle_length: int, step_minutes: int = 1440) -> pd.DataFrame:

        ps = _parse_date(period_start, "period_start")
        ov = _parse_date(ovulation_date, "ovulation_date")
        cl = int(cycle_length)

        if not (MIN_CYCLE <= cl <= MAX_CYCLE):
            raise ValueError(f"cycle_lenght must be betwen {MIN_CYCLE} and {MAX_CYCLE} dyas, got {cl}.")
        if ov <= ps:
            raise ValueError("ovulation_date must be strictly after period_start.")
        
        next_menses = ps + timedelta(cl)

        if ov >= next_menses:
            raise ValueError(f"ovulation_date must fall within the cycle before next mense on {next_menses.date()}.")
        
        follicular_duration = (ov - ps).total_seconds()          # menses → ovulation
        luteal_duration     = (next_menses - ov).total_seconds() # ovulation → menses

        step = timedelta(minutes=step_minutes)

        records = []
        t = ps

        while t < next_menses:
            if t <= ov:
                # follicular phase: menses (θ=π) → ovulation (θ=2π)
                frac  = (t - ps).total_seconds() / follicular_duration  # 0 → 1
                theta = math.pi + frac * math.pi                         # π → 2π
                if t == ov:
                    phase = "ovulation"
                else:
                    phase = "follicular"
            else:
                # luteal phase: ovulation (θ=0) → menses (θ=π)
                frac  = (t - ov).total_seconds() / luteal_duration       # 0 → 1
                theta = frac * math.pi                                    # 0 → π
                phase = "luteal"
            
            sin_val = math.sin(theta)
            cos_val = math.cos(theta)
            theta_pi = theta / math.pi

            menses_onset = 1 if t == ps else 0
            ovulation    = 1 if t == ov else 0

            records.append({
                "ID": patient_id,
                "cycle_number": cycle_num,
                "timestamp": t,
                "phase": phase,
                "theta_pi": theta_pi,
                "cos_theta": cos_val,
                "sin_theta": sin_val,
                "menses_onset": menses_onset,
                "ovulation": ovulation,
            })

            t += step
        
        df = pd.DataFrame(records)
        return df