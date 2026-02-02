# AI Product Advisor

A machine learning-based product recommendation system for smartphones, built on comprehensive phone specifications and user ratings.

## Overview

This project analyzes smartphone products from EPEY database, extracting key features and pricing information to build recommendation models. The dataset includes 159 smartphone product records (86 unique products with variants) with detailed specifications and user ratings.

## Datasets

### 1. **products_basic_info.csv**
Basic product information for analysis and filtering.

**Purpose:** Essential product details - name, price, and rating.

**Columns:**
- `product_name`: Smartphone name
- `product_price`: Price in Turkish Lira (₺)
- `product_point`: User rating (0-100)

**Statistics:**
- **Records:** 159 products/variants
- **Unique Products:** 86
- **File Size:** ~8 KB
- **Data Coverage:** 100% complete

**Price Range:** ₺6,799 - ₺159,049 (Avg: ₺35,479)
**Rating Range:** 43.0 - 99.0 (Avg: 72.61)

---

### 2. **products_common_features.csv**
Comprehensive features dataset for advanced analysis and ML models.

**Purpose:** Feature analysis, product comparisons, machine learning applications.

**Structure:**
- **Records:** 159 (synchronized with Dataset 1)
- **Columns:** 121 total
  - 1 identifier (product_name)
  - 120 common features (≥50% data coverage)

**Feature Categories:**
- Display (size, technology, resolution, refresh rate, brightness, etc.)
- Battery (capacity, charging speed, technology, etc.)
- Camera (resolution, aperture, stabilization, video recording, etc.)
- Hardware (chipset, CPU, GPU, RAM, storage, etc.)
- Design (dimensions, weight, materials, colors, etc.)
- Network (2G/3G/4G/5G, WiFi, NFC, GPS, Bluetooth, etc.)
- Operating System (OS, version, UI)
- Sensors (accelerometer, gyroscope, compass, etc.)

**Data Coverage:** All features have 50%-100% data availability

---

## Dataset Generation

Both datasets are automatically generated from the raw data using the provided script:

```bash
python src/create_datasets.py
```

The script:
1. Reads raw phone specifications CSV
2. Filters for products with both price and rating
3. Removes incomplete records
4. Selects common features based on data availability
5. Exports clean, synchronized datasets

---

## Directory Structure

```
src/
├── create_datasets.py          # Dataset generation script
├── verify_datasets.py          # Dataset validation script
└── outputs/
    └── datasets/
        ├── raw/
        │   └── epey_popular_phones_full.csv
        └── processed/
            ├── products_basic_info.csv
            └── products_common_features.csv
```

---

## Usage Examples

### Load Datasets

```python
import pandas as pd

# Load basic product information
basic = pd.read_csv('src/outputs/datasets/processed/products_basic_info.csv')
print(basic.head())

# Load features dataset
features = pd.read_csv('src/outputs/datasets/processed/products_common_features.csv')
print(features.shape)
```

### Analysis Examples

```python
# Price statistics
print(f"Avg Price: ₺{basic['product_price'].mean():,.0f}")
print(f"Price Range: ₺{basic['product_price'].min():,.0f} - ₺{basic['product_price'].max():,.0f}")

# Rating analysis
print(f"Avg Rating: {basic['product_point'].mean():.2f}/100")
print(f"Top 5 Products:")
print(basic.nlargest(5, 'product_point')[['product_name', 'product_price', 'product_point']])

# Price vs Rating correlation
correlation = basic[['product_price', 'product_point']].corr()
print(f"Price-Rating Correlation: {correlation.iloc[0, 1]:.3f}")
```

---

## Data Quality

- **Dataset 1:** All 159 records have complete price and rating data
- **Dataset 2:** Synchronized with Dataset 1, all features with ≥50% availability
- **Duplicates:** Multiple variants of same product preserved (different storage, colors, regions)
- **Source:** EPEY smartphone database

---

## Future Work

- [ ] Feature normalization for ML models
- [ ] Product similarity/clustering analysis
- [ ] Price prediction models
- [ ] Recommendation system implementation
- [ ] Data export to additional formats (JSON, Parquet)
- [ ] Web scraper for data updates
- [ ] Dashboard for visualization

---

## License

Under development...

---

*Last Updated: February 2, 2026*
