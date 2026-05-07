import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from featureExt.FEmodule import extract_features, align_to_model
import xgboostModule as xgbm

# ── Ton fichier pcap ──────────────────────────────────────────────
PCAP_FILE = r"C:\Users\user\sniff 2.0.pcap"
# ─────────────────────────────────────────────────────────────────

print("[1] Extracting features...")
df_raw = extract_features(PCAP_FILE)
print(f"    Raw shape: {df_raw.shape}")

print("[2] Aligning to model...")
df_aligned = align_to_model(df_raw)
print(f"    Aligned shape: {df_aligned.shape}")
print(f"    Columns (first 5): {list(df_aligned.columns[:5])}")

print("[3] Loading model...")
model = xgbm.load_model("binaryClassParams.pkl")

print("[4] Predicting...")
preds = model.predict(df_aligned)

print(f"\n✅ Results:")
print(f"   Total packets  : {len(preds)}")
print(f"   Normal (0)     : {(preds == 0).sum()}")
print(f"   Attack (1)     : {(preds == 1).sum()}")