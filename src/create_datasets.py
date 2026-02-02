import pandas as pd
import os
from pathlib import Path

# Define paths
raw_data_path = 'src/outputs/datasets/raw/epey_popular_phones_full.csv'
processed_data_dir = 'src/outputs/datasets/processed'

# Create processed directory if it doesn't exist
Path(processed_data_dir).mkdir(parents=True, exist_ok=True)

# Read the raw dataset
print("Reading raw dataset...")
df = pd.read_csv(raw_data_path)

print(f"Total records in raw data: {len(df)}")
print(f"Total columns: {len(df.columns)}")

# Column mapping - Turkish to English
# urun_adi = product name
# fiyat_tl = product price
# puan = product point (rating)

# 1. CREATE FIRST DATASET: Basic product information
print("\n" + "="*50)
print("Creating Dataset 1: Basic Product Information")
print("="*50)

# Select required columns
dataset1 = df[['urun_adi', 'fiyat_tl', 'puan']].copy()

# Rename columns to English
dataset1.columns = ['product_name', 'product_price', 'product_point']

# Remove rows with missing values in any of the three columns
dataset1 = dataset1.dropna(subset=['product_name', 'product_price', 'product_point'])
dataset1 = dataset1.reset_index(drop=True)

# Save dataset 1
dataset1_path = os.path.join(processed_data_dir, 'products_basic_info.csv')
dataset1.to_csv(dataset1_path, index=False)
print(f"\n✓ Dataset 1 saved to: {dataset1_path}")
print(f"  Records: {len(dataset1)}")
print(f"  Columns: {list(dataset1.columns)}")
print("\nFirst 5 rows:")
print(dataset1.head())

# 2. CREATE SECOND DATASET: Common features across all products
print("\n" + "="*50)
print("Creating Dataset 2: Common Features")
print("="*50)

# Create a mapping of product names to rows in raw data
# Match by product name, price, and point to find corresponding raw data rows
print(f"\nMatching Dataset 1 products with raw data features...")

# Create a merged dataset with features
# For each product in dataset1, find the matching row in raw df
dataset2_list = []

for idx, row in dataset1.iterrows():
    product_name = row['product_name']
    product_price = row['product_price']
    product_point = row['product_point']
    
    # Find matching row in raw data (by name, price, and point)
    matching_raw = df[(df['urun_adi'] == product_name) & 
                      (df['fiyat_tl'] == product_price) & 
                      (df['puan'] == product_point)]
    
    if len(matching_raw) > 0:
        # Use the first match
        dataset2_list.append(matching_raw.iloc[0])

dataset2_raw = pd.DataFrame(dataset2_list).reset_index(drop=True)
print(f"Matched records: {len(dataset2_raw)}")

# Identify columns that have values in most/all products
# These are the "common features"
print("\nAnalyzing column coverage...")
column_coverage = dataset2_raw.notna().sum() / len(dataset2_raw) * 100

# Select columns with at least 50% coverage (adjustable threshold)
coverage_threshold = 50
common_columns = column_coverage[column_coverage >= coverage_threshold].index.tolist()

print(f"\nColumns with >= {coverage_threshold}% data coverage:")
for col in common_columns[:20]:  # Show first 20
    coverage = column_coverage[col]
    print(f"  {col}: {coverage:.1f}%")

# Create dataset 2 with common features
# Include product name for reference, then common feature columns
dataset2 = dataset2_raw[['urun_adi'] + common_columns].copy()
dataset2.columns = ['product_name'] + common_columns
dataset2 = dataset2.reset_index(drop=True)

# Save dataset 2
dataset2_path = os.path.join(processed_data_dir, 'products_common_features.csv')
dataset2.to_csv(dataset2_path, index=False)
print(f"\n✓ Dataset 2 saved to: {dataset2_path}")
print(f"  Records: {len(dataset2)}")
print(f"  Columns: {len(dataset2.columns)}")
print(f"  Common feature columns: {len(common_columns)}")

# Summary
print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print(f"\n📊 Dataset 1 (Basic Product Info):")
print(f"   Location: {dataset1_path}")
print(f"   Rows: {len(dataset1)}")
print(f"   Columns: product_name, product_price, product_point")
print(f"   Description: All product records (including variants) with both price and point data")

print(f"\n📊 Dataset 2 (Common Features):")
print(f"   Location: {dataset2_path}")
print(f"   Rows: {len(dataset2)} (same as Dataset 1)")
print(f"   Columns: {len(dataset2.columns)} (product_name + {len(common_columns)} features)")
print(f"   Description: Common features for all product records with price and point data")

print("\n✅ Datasets created successfully!")
