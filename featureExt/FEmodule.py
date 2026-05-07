import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from FeatureExtractor import FE
import pandas as pd
import numpy as np


def extract_features(file):
    all_rows = []
    extractor = FE(file)
    while True:
        features = extractor.get_next_vector()
        if len(features) == 0:
            break
        all_rows.append(features)
    df = pd.DataFrame(all_rows, columns=extractor.nstat.getNetStatHeaders())
    return df


def align_to_model(df):
    lambdas = ['L5', 'L3', 'L1', 'L0.1', 'L0.01']
    model_headers = []

    # MI_dir (15) and H (15): weight, mean, variance
    for g in ['MI_dir', 'H']:
        for l in lambdas:
            model_headers += [f"{g}_{l}_weight", f"{g}_{l}_mean", f"{g}_{l}_variance"]

    # HH (35): weight, mean, std, magnitude, radius, covariance, pcc
    for l in lambdas:
        model_headers += [f"HH_{l}_weight", f"HH_{l}_mean", f"HH_{l}_std",
                          f"HH_{l}_magnitude", f"HH_{l}_radius",
                          f"HH_{l}_covariance", f"HH_{l}_pcc"]

    # HH_jit (15): weight, mean, variance
    for l in lambdas:
        model_headers += [f"HH_jit_{l}_weight", f"HH_jit_{l}_mean", f"HH_jit_{l}_variance"]

    # HpHp (35): weight, mean, std, magnitude, radius, covariance, pcc
    for l in lambdas:
        model_headers += [f"HpHp_{l}_weight", f"HpHp_{l}_mean", f"HpHp_{l}_std",
                          f"HpHp_{l}_magnitude", f"HpHp_{l}_radius",
                          f"HpHp_{l}_covariance", f"HpHp_{l}_pcc"]

    # Step 1: Swap Radius <-> Magnitude for HH and HpHp groups
    # Extractor gives [std, radius, magnitude], model expects [std, magnitude, radius]
    cols = list(df.columns)
    for i in [33, 40, 47, 54, 61, 83, 90, 97, 104, 111]:
        cols[i], cols[i+1] = cols[i+1], cols[i]
    df = df[cols]

    # Step 2: Variance → Std Dev for HH and HpHp std columns
    hh_hphp_std_indices = [32, 39, 46, 53, 60, 82, 89, 96, 103, 110]
    for idx in hh_hphp_std_indices:
        df.iloc[:, idx] = np.sqrt(df.iloc[:, idx].abs())

    # Step 3: Rename to model headers
    df.columns = model_headers

    return df