"""
The main file
"""

import pandas as pd
from pathlib import Path
from settings import Settings
from menstrual_cycle_encoding import CycleEncoding


def get_mode() -> str:
    """Prompt for the run mode."""
    print("Select mode (just introduce the number):")
    print("  [1] encoding")
    return input("Enter mode: ").strip().lower()

def get_encoding_step_minutes(settings: Settings) -> int:
    """
    Prompt for the encoding time interval (minutes), validate it, and
    store it on settings.encoding.step_minutes.
    """
    default = settings.encoding.step_minutes
    raw = input(f"Select encoding time interval in minutes (default {default}): ").strip()

    if raw == "":
        step_minutes = default
    else:
        try:
            step_minutes = int(raw)
            if step_minutes <= 0:
                print(f"Invalid interval, using default ({default}).")
                step_minutes = default
        except ValueError:
            print(f"Invalid interval, using default ({default}).")
            step_minutes = default

    settings.encoding.step_minutes = step_minutes
    print(f"Using encoding step: {step_minutes} min")
    return step_minutes

def main():

    settings = Settings()

    mode = get_mode()

    if mode in ("1", "encoding"):
        get_encoding_step_minutes(settings)
        cycle_encoding(settings)
    else:
        print(f"Unknown mode '{mode}'. Available modes: encoding")


def cycle_encoding(settings: Settings):

    enc = CycleEncoding(settings)
    summary = pd.read_csv(settings.data_folder.cycle_date_folder)
    output_path = settings.data_folder.output_folder

    all_dfs = []
    skipped = []

    for _, row in summary.iterrows():
        pid     = row["participant_ID"]
        cyc     = row["cycle_number"]
        p_start = str(row["period_start"])
        ov_date = str(row["ovulation_date"])
        cyc_len = int(row["cycle_length"])

        if pd.isna(row["period_start"]) or pd.isna(row["ovulation_date"]):
            skipped.append((pid, cyc, "missing period_start or ovulation_date"))
            continue

        try:
            df = enc.encode_cycle(
                patient_id     = pid,
                cycle_num      = cyc,
                period_start   = p_start,
                ovulation_date = ov_date,
                cycle_length   = cyc_len,
                step_minutes   = settings.encoding.step_minutes,
            )
            all_dfs.append(df)
        except ValueError as e:
            skipped.append((pid, cyc, str(e)))
        
        if settings.encoding.save_to_single_file:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path + "sep\\" + f"{pid}_cycle_{cyc}.csv")
        else:
            continue

    print(f"Encoded : {len(all_dfs)} cycles")
    print(f"Skipped : {len(skipped)} cycles")
    for pid, cyc, reason in skipped:
        print(f"  {pid} cycle {cyc}: {reason}")
    
    combined = pd.concat(all_dfs, ignore_index=True)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    output_name = output_path + "all_patients_encoded_data.csv"
    combined.to_csv(output_name, index=False)
    print(f"\nSaved {len(combined)} rows → {output_name}")
    return combined

if __name__ == '__main__':
    main()