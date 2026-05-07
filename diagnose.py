import joblib
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from featureExt.FEmodule import extract_features, align_to_model

# Charge le modèle
model = joblib.load('binaryClassParams.pkl')

# Test avec ton pcap normal (on sait que c est du trafic normal)
df_raw = extract_features(r'C:\Users\user\sniff 2.0.pcap')
df = align_to_model(df_raw)
preds = model.predict(df)

print('=== TEST SUR TRAFIC NORMAL ===')
print(f'Total paquets     : {len(preds)}')
print(f'Prédit Normal (0) : {(preds == 0).sum()}')
print(f'Prédit Attaque (1): {(preds == 1).sum()}')
print(f'Taux FP           : {(preds == 1).sum() / len(preds) * 100:.1f}%')

# Probabilités de confiance
proba = model.predict_proba(df)
print(f'\nConfiance moyenne (normal)  : {proba[:,0].mean():.3f}')
print(f'Confiance moyenne (attaque) : {proba[:,1].mean():.3f}')
print(f'Paquets confiance attaque > 0.8 : {(proba[:,1] > 0.8).sum()}')
print(f'Paquets confiance attaque > 0.5 : {(proba[:,1] > 0.5).sum()}')