#import os
#import pandas as pd
#import matplotlib.pyplot as plt
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import classification_report
#from xgboost import XGBClassifier
import joblib as jb
#from sklearn.metrics import confusion_matrix

"""def simple_load_csv(base_path):
    ""
    Load all CSV files from a directory (including subfolders)
    and merge them into a single DataFrame.
    ""
    
    all_dfs = []

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                
                try:
                    df = pd.read_csv(file_path)
                    #df["source_file"] = file  # optional debug info
                    #df["source_path"] = root  # optional device/folder tracking
                    
                    all_dfs.append(df)

                except Exception as e:
                    print(f"Failed to read {file_path}: {e}")

    if not all_dfs:
        return pd.DataFrame()

    return pd.concat(all_dfs, ignore_index=True)"""
"""def split_csv(df, split_ratio=0.7):
    split_idx = int(len(df) * split_ratio)
    
    train = df.iloc[:split_idx]
    test  = df.iloc[split_idx:]
    
    return train, test"""
"""def load_csv_file(file_path,label):
    print(f"Loading {file_path}...")
    try:
        df = pd.read_csv(file_path).drop_duplicates()
        df["label"] = label
        train, test = split_csv(df)
        return train, test

    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return pd.DataFrame(), pd.DataFrame()"""
"""def load_csv_folder(base_path,label):
    ""
    Load all CSV files from a directory (including subfolders)
    and merge them into a single DataFrame.
    ""
    train_list = []
    test_list = []
    all_dfs = []

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                train, test = load_csv_file(file_path, label)
                train_list.append(train)
                test_list.append(test)

    return train_list, test_list"""
"""def preprocess(devices):
    train_all = []
    test_all = []
    # Load and preprocess data for the device
    for device in devices:
        print(f"Processing {device}...")
        train_n, test_n =load_csv_file(f"./N-BaIot/{device}/benign_traffic.csv", label=0)
        train_g, test_g = load_csv_folder(f"./N-BaIot/{device}/gafgyt_attacks", label=1)
        train_m, test_m = load_csv_folder(f"./N-BaIot/{device}/mirai_attacks", label=1)
        train_device = pd.concat([train_n] + train_g + train_m, ignore_index=True)
        test_device  = pd.concat([test_n] + test_g + test_m, ignore_index=True)
        train_all.append(train_device)
        test_all.append(test_device)
    train_df = pd.concat(train_all, ignore_index=True)
    test_df  = pd.concat(test_all, ignore_index=True)
    return train_df, test_df"""
"""def train_on_devices(devices_data):
    # Train the model
    train , test = devices_data
    x_train = train.drop("label", axis=1)
    y_train = train["label"]
    x_test = test.drop("label", axis=1)
    y_test = test["label"]
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)

    print(classification_report(y_test, y_pred))
    print(confusion_matrix(y_test, y_pred))
    # Evaluate and print results
    jb.dump(model, "rf_model.pkl")
    return model
def test_on_device(model,device_name):
    df_normal = pd.read_csv(f"./N-BaIot/{device_name}/benign_traffic.csv")
    df_gafgyt = simple_load_csv(f"./N-BaIot/{device_name}/gafgyt_attacks/") 
    df_mirai = simple_load_csv(f"./N-BaIot/{device_name}/mirai_attacks/")
    df_attack = pd.concat([df_gafgyt, df_mirai], ignore_index=True)

    df_normal["label"] = 0
    df_attack["label"] = 1

    df_all = pd.concat([df_normal, df_attack], ignore_index=True)
    #df_all = df_all.sample(frac=1, random_state=42).reset_index(drop=True)

    x = df_all.drop("label", axis=1)
    y = df_all["label"]

    y_pred = model.predict(x)

    print(f"Results for {device_name}:")
    print(classification_report(y, y_pred))"""

def load_model(model_path):
    return jb.load(model_path)