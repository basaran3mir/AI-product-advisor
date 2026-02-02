import pandas as pd

print("="*60)
print("DATASET VERIFICATION")
print("="*60)

# Load both datasets
basic = pd.read_csv('src/outputs/datasets/processed/products_basic_info.csv')
common = pd.read_csv('src/outputs/datasets/processed/products_common_features.csv')

print(f"\n📊 Dataset 1 (Basic Product Info):")
print(f"   Records: {len(basic)}")
print(f"   Columns: {len(basic.columns)}")
print(f"   Column names: {list(basic.columns)}")

print(f"\n📊 Dataset 2 (Common Features):")
print(f"   Records: {len(common)}")
print(f"   Columns: {len(common.columns)}")

print(f"\n✓ Data Synchronization Check:")
print(f"   Products in Dataset 1: {len(basic)}")
print(f"   Products in Dataset 2: {len(common)}")

# Check if all products match
basic_products = set(basic['product_name'].values)
common_products = set(common['product_name'].values)

matching = basic_products == common_products
print(f"   All products match: {matching}")

if matching:
    unique_count = len(basic_products)
    total_records = len(basic)
    print(f"   ✅ SYNCHRONIZED: {total_records} product records")
    print(f"      ({unique_count} unique product names with multiple variants/prices)")
else:
    print(f"   ⚠️ Products in Dataset 1 only: {len(basic_products - common_products)}")
    print(f"   ⚠️ Products in Dataset 2 only: {len(common_products - basic_products)}")

print(f"\n📋 Sample Data:")
print(f"\nDataset 1 (first 5 rows):")
print(basic.head())

print(f"\nDataset 2 (first 5 rows, showing first 5 columns):")
print(common.iloc[:5, :5])

print(f"\n✓ Price Range:")
print(f"   Min: ₺{basic['product_price'].min():,.2f}")
print(f"   Max: ₺{basic['product_price'].max():,.2f}")
print(f"   Avg: ₺{basic['product_price'].mean():,.2f}")

print(f"\n✓ Rating Range:")
print(f"   Min: {basic['product_point'].min()}")
print(f"   Max: {basic['product_point'].max()}")
print(f"   Avg: {basic['product_point'].mean():.2f}")

print("\n" + "="*60)
print("✅ VERIFICATION COMPLETE")
print("="*60)
