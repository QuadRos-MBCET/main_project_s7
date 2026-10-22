"""
Export Group-Stratified Train / Val / Test Splits for the 380-sample SafeAd Catalog.
Guarantees:
1. Zero Data Leakage: Samples sharing brand tokens or campaign source URLs are placed in the same split.
2. Balanced Stratification: Preserves category ratios across SAFE_FOR_ALL, SAFE_14_PLUS, SAFE_18_PLUS, UNSAFE_FOR_ALL.
3. Media Type Preservation: Maintains image vs video distribution across splits.
4. Deterministic: Seeded (seed=42) for 100% reproducibility.
"""

import os
import json
import pandas as pd
import numpy as np

def export_benchmark_splits(
    catalog_path: str,
    output_dir: str,
    train_ratio: float = 0.80,
    val_ratio: float = 0.10,
    seed: int = 42
):
    df = pd.read_csv(catalog_path)
    print(f"[INFO] Loaded {len(df)} samples from {catalog_path}")

    # Create Group Key based on brand token or domain
    def get_group_key(row):
        brand = str(row.get("key_brand_tokens", "")).strip().lower()
        if brand and brand != "nan":
            return f"brand_{brand}"
        url = str(row.get("source_url", "")).strip().lower()
        if "commons.wikimedia" in url:
            # Subdivide by first token of file path
            return f"wiki_{os.path.basename(row['file_path']).split('_')[0]}"
        elif "archive.org" in url:
            return f"archive_{os.path.basename(row['file_path']).split('_')[0]}"
        elif url and url != "nan":
            return f"url_{url}"
        return f"sample_{row['sample_id']}"

    df["group_key"] = df.apply(get_group_key, axis=1)

    rng = np.random.RandomState(seed)
    
    # Stratified Group Split by (safead_label, media_type)
    df["strata"] = df["safead_label"] + "_" + df["media_type"]

    train_indices = []
    val_indices = []
    test_indices = []

    for strata_name, group in df.groupby("strata"):
        unique_groups = group["group_key"].unique()
        rng.shuffle(unique_groups)

        n_groups = len(unique_groups)
        n_train = max(1, int(round(n_groups * train_ratio)))
        n_val = max(1, int(round(n_groups * val_ratio))) if n_groups >= 3 else 0

        train_grps = set(unique_groups[:n_train])
        val_grps = set(unique_groups[n_train:n_train + n_val])
        test_grps = set(unique_groups[n_train + n_val:])

        # If test is empty due to small group count (e.g. video UNSAFE_FOR_ALL with 5 samples)
        if not test_grps and len(train_grps) > 1:
            moved = train_grps.pop()
            test_grps.add(moved)

        for idx, row in group.iterrows():
            grp = row["group_key"]
            if grp in train_grps:
                train_indices.append(idx)
            elif grp in val_grps:
                val_indices.append(idx)
            else:
                test_indices.append(idx)

    train_df = df.loc[train_indices].drop(columns=["group_key", "strata"]).copy()
    val_df = df.loc[val_indices].drop(columns=["group_key", "strata"]).copy()
    test_df = df.loc[test_indices].drop(columns=["group_key", "strata"]).copy()

    # Leakage verification: check group overlap
    train_groups = set(df.loc[train_indices, "group_key"])
    val_groups = set(df.loc[val_indices, "group_key"])
    test_groups = set(df.loc[test_indices, "group_key"])

    leakage_train_val = train_groups.intersection(val_groups)
    leakage_train_test = train_groups.intersection(test_groups)
    leakage_val_test = val_groups.intersection(test_groups)

    assert not leakage_train_val, f"Leakage detected between train and val: {leakage_train_val}"
    assert not leakage_train_test, f"Leakage detected between train and test: {leakage_train_test}"
    assert not leakage_val_test, f"Leakage detected between val and test: {leakage_val_test}"

    os.makedirs(output_dir, exist_ok=True)
    train_df.to_csv(os.path.join(output_dir, "train.csv"), index=False)
    val_df.to_csv(os.path.join(output_dir, "val.csv"), index=False)
    test_df.to_csv(os.path.join(output_dir, "test.csv"), index=False)

    summary = {
        "catalog": catalog_path,
        "total_samples": len(df),
        "split_counts": {
            "train": len(train_df),
            "val": len(val_df),
            "test": len(test_df)
        },
        "train_distribution": train_df["safead_label"].value_counts().to_dict(),
        "val_distribution": val_df["safead_label"].value_counts().to_dict(),
        "test_distribution": test_df["safead_label"].value_counts().to_dict(),
        "leakage_test_passed": True
    }

    summary_path = os.path.join(output_dir, "benchmark_splits_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[SUCCESS] Exported benchmark splits to: {output_dir}")
    print(f"  - Train : {len(train_df)} samples")
    print(f"  - Val   : {len(val_df)} samples")
    print(f"  - Test  : {len(test_df)} samples")
    print(f"  - Leakage Check: PASSED (Zero overlapping groups across splits)")
    return summary

if __name__ == "__main__":
    cat = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub\custom_ads\complete_dataset_catalog.csv"
    out = r"C:\Users\hello\Videos\sourav\datasets\safead-dataset-hub\splits\benchmark_380"
    export_benchmark_splits(cat, out)
