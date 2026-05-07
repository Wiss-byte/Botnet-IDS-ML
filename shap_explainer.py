import shap
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')  # pas de fenêtre popup
import matplotlib.pyplot as plt
import os

# ==== LOAD MODEL ====
model = joblib.load("binaryClassParams.pkl")

# ==== INIT EXPLAINER ====
explainer = shap.TreeExplainer(model)

def explain_prediction(df_aligned, save_path="shap_plot.png"):
    """
    df_aligned : DataFrame aligné (115 features) d'UNE seule ligne
    Retourne : dict des top features + sauvegarde un plot
    """
    # Calcul SHAP values
    shap_values = explainer.shap_values(df_aligned)

    # Pour classification binaire, prendre les valeurs pour classe 1 (attaque)
    if isinstance(shap_values, list):
        sv = shap_values[1]  # classe attaque
    else:
        sv = shap_values

    # Top 10 features les plus importantes
    feature_names = df_aligned.columns.tolist()
    mean_shap = np.abs(sv).mean(axis=0)
    top_indices = np.argsort(mean_shap)[::-1][:10]

    top_features = {
        feature_names[i]: round(float(mean_shap[i]), 4)
        for i in top_indices
    }

    # Générer le plot
    plt.figure(figsize=(10, 6))
    plt.barh(
        [feature_names[i] for i in top_indices][::-1],
        [mean_shap[i] for i in top_indices][::-1],
        color='#f85149'
    )
    plt.xlabel('SHAP Value (impact sur la détection)')
    plt.title('🔍 Top 10 Features — Explication de la détection')
    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight',
                facecolor='#161b22', edgecolor='none')
    plt.close()

    return top_features


if __name__ == "__main__":
    # Test rapide avec le pcap normal
    import sys
    sys.path.insert(0, '.')
    from featureExt.FEmodule import extract_features, align_to_model

    print("Extracting features for SHAP test...")
    df_raw = extract_features(r"C:\Users\user\sniff 2.0.pcap")
    df = align_to_model(df_raw)

    print("Computing SHAP values...")
    top = explain_prediction(df, save_path="shap_plot.png")

    print("\n=== TOP 10 FEATURES ===")
    for feat, val in top.items():
        print(f"  {feat}: {val}")

    print("\nPlot saved to shap_plot.png ✅")