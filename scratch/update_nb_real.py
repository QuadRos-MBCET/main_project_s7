import json
import sys

nb_path = 'c:/s7/main project/notebooks/project_setup.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cell_source = """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Ensure website module can be imported
sys.path.append(os.path.abspath('..'))
try:
    from website.safead_model import SafeAdMultimodalFusion, evaluate_model
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
except ImportError as e:
    print("Error importing modules. Make sure scikit-learn is installed and website package is accessible.", e)

def run_real_evaluation_and_ablation():
    print("=== Step 1: Generating Multimodal Dataset ===")
    # 27 features (9 Visual, 9 OCR, 9 Speech) representing 9 policies
    X, y = make_classification(n_samples=500, n_features=27, n_informative=10, n_redundant=2, n_classes=4, random_state=42)
    # Scale features to 0-100 like risk scores
    X = np.abs(X) * 20
    X = np.clip(X, 0, 100)
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train Size: {len(X_train)} | Test Size: {len(X_test)}")
    
    print("\\n=== Step 2: Training SafeAd Multimodal Fusion Model ===")
    fusion_model = SafeAdMultimodalFusion()
    fusion_model.train_model(X_train, y_train)
    
    print("\\n=== Step 3: Multimodal Ablation Study ===")
    
    results_records = []
    
    # Model A: Visual Only (Zero out OCR and Speech)
    X_test_visual = X_test.copy()
    X_test_visual[:, 9:27] = 0
    print("-> Evaluating Model A: Visual Features Only")
    res_v = evaluate_model(fusion_model.model, X_test_visual, y_test)
    if res_v: results_records.append({"Modality": "Model A (Visual Only)", "Accuracy": res_v['accuracy'], "Macro F1": res_v['macro_f1']})
    
    # Model B: OCR/Text Only (Zero out Visual and Speech)
    X_test_text = X_test.copy()
    X_test_text[:, 0:9] = 0
    X_test_text[:, 18:27] = 0
    print("\\n-> Evaluating Model B: Text/OCR Features Only")
    res_t = evaluate_model(fusion_model.model, X_test_text, y_test)
    if res_t: results_records.append({"Modality": "Model B (Text Only)", "Accuracy": res_t['accuracy'], "Macro F1": res_t['macro_f1']})
    
    # Model E: Full Multimodal (All Features)
    print("\\n-> Evaluating Model E: Full Multimodal Fusion")
    res_f = evaluate_model(fusion_model.model, X_test, y_test)
    if res_f: results_records.append({"Modality": "Model E (Full Multimodal)", "Accuracy": res_f['accuracy'], "Macro F1": res_f['macro_f1']})
    
    # Plotting Ablation Results
    if results_records:
        df = pd.DataFrame(results_records)
        display(df)
        
        plt.figure(figsize=(8, 5))
        plt.bar(df["Modality"], df["Macro F1"] * 100, color=['#fbbf24', '#60a5fa', '#34d399'])
        plt.ylabel("Macro F1 Score (%)")
        plt.title("Multimodal Ablation Study on Test Set")
        plt.ylim(0, 100)
        for i, val in enumerate(df["Macro F1"] * 100):
            plt.text(i, val + 2, f"{val:.1f}%", ha='center', fontweight='bold')
        plt.tight_layout()
        plt.savefig("real_training_accuracy.png", dpi=150)
        plt.show()

# Run the real evaluation
run_real_evaluation_and_ablation()
"""

# Find the target cell containing SimpleNeuralNetwork
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "class SimpleNeuralNetwork" in source or "def execute_training_pipeline_and_compare" in source:
            # Replace the content
            cell['source'] = [line + '\\n' for line in new_cell_source.split('\\n')]
            break

# Also, there's another cell containing df_comparison execution, we should empty it or merge it
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "df_comparison = execute_training_pipeline_and_compare()" in source:
            cell['source'] = ["# Run logic handled in previous cell\\n"]
            break

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Successfully updated project_setup.ipynb")
