"""
The main file
"""

import pandas as pd
from pathlib import Path
from settings import Settings
from menstrual_cycle_encoding import CycleEncoding




def main():

    settings = Settings()

    print("Select mode (just introduce the number):")
    print("  [1] encoding")
    mode = input("Enter mode: ").strip().lower()

    if mode in ("1", "encoding"):
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
        
    print(f"Encoded : {len(all_dfs)} cycles")
    print(f"Skipped : {len(skipped)} cycles")
    for pid, cyc, reason in skipped:
        print(f"  {pid} cycle {cyc}: {reason}")
    
    combined = pd.concat(all_dfs, ignore_index=True)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_path + "all_patients_encoded_data.csv", index=False)
    print(f"\nSaved {len(combined)} rows → {output_path}")
    return combined

if __name__ == '__main__':
    main()