"""
security/encrypt_banks.py — Converts CSV question banks into encrypted .qbank files.
"""
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from security.crypto import encrypt_file, load_qbank

QB_DIR = ROOT / "question_bank"

def process():
    for csv_file in ["arabic.csv", "english.csv", "dump_Questions_backup.csv"]:
        csv_path = QB_DIR / csv_file
        if csv_path.exists():
            qbank_path = QB_DIR / csv_file.replace(".csv", ".qbank")
            encrypt_file(csv_path, qbank_path)
            
            # Verify decryption immediately
            rows = load_qbank(qbank_path)
            print(f"Verified decryption for {qbank_path.name}: {len(rows)} rows loaded cleanly in memory.")

if __name__ == "__main__":
    process()
