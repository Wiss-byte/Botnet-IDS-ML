from .feature_extractor import FE
import pandas as pd
import numpy as np

def extract_features(file):
    all_rows = []
    extractor = FE(file)
    while True:
        features = extractor.get_next_vector() # Returns shape (115,)
        
        if len(features) == 0:
            break # No more packets
            
        # 2. Add the single vector to your list
        all_rows.append(features)
    df = pd.DataFrame(all_rows, columns=extractor.nstat.getNetStatHeaders())
    return df

def align_to_model(df):
    # 1. Define the 115 headers your model expects
    lambdas = ['L5', 'L3', 'L1', 'L0.1', 'L0.01']
    model_headers = []
    
    # MI_dir (15) & H (15) & HH_jit (15) use 'variance'
    # HH (35) & HpHp (35) use 'std', 'magnitude', 'radius'
    
    # This matches the EXACT order in your model's list:
    for g in ['MI_dir', 'H']:
        for l in lambdas:
            model_headers += [f"{g}_{l}_weight", f"{g}_{l}_mean", f"{g}_{l}_variance"]
            
    for l in lambdas:
        model_headers += [f"HH_{l}_weight", f"HH_{l}_mean", f"HH_{l}_std", 
                          f"HH_{l}_magnitude", f"HH_{l}_radius", f"HH_{l}_covariance", f"HH_{l}_pcc"]
            
    for l in lambdas:
        model_headers += [f"HH_jit_{l}_weight", f"HH_jit_{l}_mean", f"HH_jit_{l}_variance"]
        
    for l in lambdas:
        model_headers += [f"HpHp_{l}_weight", f"HpHp_{l}_mean", f"HpHp_{l}_std", 
                          f"HpHp_{l}_magnitude", f"HpHp_{l}_radius", f"HpHp_{l}_covariance", f"HpHp_{l}_pcc"]

    # 2. Reorder the Radius and Magnitude columns
    # The extractor gives [..., std, radius, magnitude, ...]
    # We must swap them to [..., std, magnitude, radius, ...]
    
    # Indices for HH Radius/Magnitude: 33/34, 40/41, 47/48, 54/55, 61/62
    # Indices for HpHp Radius/Magnitude: 83/84, 90/91, 97/98, 104/105, 111/112
    cols = list(df.columns)
    for i in [33, 40, 47, 54, 61, 83, 90, 97, 104, 111]:
        cols[i], cols[i+1] = cols[i+1], cols[i]
    df = df[cols]

    # 3. Math Fix: Convert Variance to Std Dev for HH and HpHp only
    # The extractor's 3rd feature in these groups is currently variance.
    # We need the square root for the model's 'std' requirement.
    #hh_hphp_std_cols = [32, 39, 46, 53, 60, 82, 89, 96, 103, 110]
    #for idx in hh_hphp_std_cols:
        #df.iloc[:, idx] = np.sqrt(df.iloc[:, idx])

    # 4. Final Rename
    df.columns = model_headers
    return df