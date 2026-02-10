import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import base64
from urllib.parse import urljoin

# =========================
# SABİTLER
# =========================
BASE_URL = "https://www.epey.com"
LIST_BASE = "https://www.epey.com/akilli-telefonlar"
OUTPUT_CSV = "src/outputs/datasets/phones/raw/full_dataset.csv"

# =========================
# CLOUDSCRAPER
# =========================
scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
        "desktop": True
    }
)

# =========================
# POPÜLERLİK URL OLUŞTURUCU
# =========================
def build_sort_url(sort_value: str) -> str:
    payload = f'N;_s:{len(sort_value)}:"{sort_value}";'
    encoded = base64.b64encode(payload.encode("utf-8")).decode("utf-8")
    return f"{LIST_BASE}/e/{encoded}/"

# =========================
# POPÜLER ÜRÜNLER (PUAN + FİYAT)
# =========================
def get_popular_products(limit=100):
    sort_url = build_sort_url("tiklama:DESC")
    products = []
    page = 1

    while len(products) < limit:
        page_url = sort_url if page == 1 else f"{sort_url}{page}/"
        print(f"📄 Sayfa çekiliyor: {page_url}")

        resp = scraper.get(
            page_url,
            headers={"Referer": LIST_BASE},
            timeout=30
        )

        if resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("ul.metin.row")

        if not rows:
            break

        for ul in rows:
            name_el = ul.select_one("a.urunadi")
            price_el = ul.select_one("li.fiyat a")
            score_div = ul.select_one("li.puan div[data-text]")

            if not name_el:
                continue

            # 💰 FİYAT
            price = None
            if price_el:
                price = (
                    price_el.get_text(strip=True)
                    .split("TL")[0]
                    .replace(".", "")
                    .replace(",", ".")
                    .strip()
                )

            # ⭐ PUAN
            score = score_div["data-text"] if score_div else None

            products.append({
                "urun_ad": name_el.get_text(strip=True),
                "urun_url": urljoin(BASE_URL, name_el["href"]),
                "urun_fiyat": price,
                "urun_puan": score
            })

            if len(products) >= limit:
                break

        page += 1
        time.sleep(random.uniform(1.2, 2.0))

    return products

# =========================
# ÜRÜN DETAYLARI
# =========================
def get_product_detail(product_url: str):
    resp = scraper.get(
        product_url,
        headers={"Referer": LIST_BASE},
        timeout=30
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    data = {}

    for group in soup.select("div#ozellikler div#grup"):
        group_title = group.select_one("h3 span")
        group_name = group_title.get_text(strip=True).lower() if group_title else "genel"

        for li in group.select("ul.grup li"):
            key_el = li.select_one("strong")
            val_el = li.select_one("span.cell")

            if not key_el or not val_el:
                continue

            key = key_el.get_text(strip=True)

            links = val_el.find_all("a", recursive=True)
            if links:
                value = " | ".join(
                    dict.fromkeys(a.get_text(strip=True) for a in links)
                )
            else:
                value = val_el.get_text(strip=True)

            col_name = f"{group_name}_{key}".lower()
            col_name = (
                col_name.replace(" ", "_")
                .replace("/", "_")
                .replace("(", "")
                .replace(")", "")
                .replace("%", "yuzde")
                .replace("-", "_")
            )

            data[col_name] = value

    return data

# =========================
# MAIN
# =========================
def main():
    print("🚀 Popüler telefonlar alınıyor...")
    products = get_popular_products(limit=200)
    print(f"✅ {len(products)} ürün bulundu")

    all_data = []

    for i, p in enumerate(products, start=1):
        print(f"[{i}/{len(products)}] {p['urun_ad']}")
        try:
            detail = get_product_detail(p["url"])
            merged = {**p, **detail}
            all_data.append(merged)
            time.sleep(random.uniform(1.5, 3.0))
        except Exception as e:
            print("❌ Hata:", p["url"], e)

    df = pd.DataFrame(all_data)

    df.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"🎉 CSV hazır: {OUTPUT_CSV}")
    print(f"📊 Ürün: {len(df)}, Kolon: {len(df.columns)}")

if __name__ == "__main__":
    main()
