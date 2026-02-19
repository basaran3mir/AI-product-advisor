import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import base64
from urllib.parse import urljoin
from pathlib import Path


class EpeyPhoneScraper:
    """
    Epey akıllı telefon scraper
    - Popüler ürünleri çeker
    - Ürün detaylarını parse eder
    - CSV olarak kaydeder
    """

    def __init__(
        self,
        base_url: str = "https://www.epey.com",
        list_base: str = "https://www.epey.com/akilli-telefonlar",
        output_csv: str | Path = "src/app/output/dataset/raw/full_dataset.csv",
        min_delay: float = 1.2,
        max_delay: float = 3.0,
        image_dir: str | Path = "src/app/output/image"
    ):
        self.base_url = base_url
        self.list_base = list_base
        self.output_csv = Path(output_csv)
        self.min_delay = min_delay
        self.max_delay = max_delay

        self.image_dir = Path(image_dir).resolve()
        self.image_dir.mkdir(parents=True, exist_ok=True)

        self.scraper = self._create_scraper()

    # =====================================
    # SCRAPER SETUP
    # =====================================

    def _create_scraper(self):
        return cloudscraper.create_scraper(
            browser={
                "browser": "chrome",
                "platform": "windows",
                "desktop": True
            }
        )

    # =====================================
    # UTILITIES
    # =====================================

    def _sleep(self):
        time.sleep(random.uniform(self.min_delay, self.max_delay))

    def _build_sort_url(self, sort_value: str) -> str:
        payload = f'N;_s:{len(sort_value)}:"{sort_value}";'
        encoded = base64.b64encode(payload.encode("utf-8")).decode("utf-8")
        return f"{self.list_base}/e/{encoded}/"

    # =====================================
    # POPULAR PRODUCTS
    # =====================================

    def get_popular_products(self, limit: int = 100) -> list[dict]:
        sort_url = self._build_sort_url("tiklama:DESC")
        products = []
        page = 1

        while len(products) < limit:
            page_url = sort_url if page == 1 else f"{sort_url}{page}/"
            print(f"📄 Sayfa: {page_url}")

            resp = self.scraper.get(
                page_url,
                headers={"Referer": self.list_base},
                timeout=30
            )

            if resp.status_code != 200:
                break

            soup = BeautifulSoup(resp.text, "lxml")
            rows = soup.select("ul.metin.row")

            if not rows:
                break

            for ul in rows:
                product = self._parse_list_item(ul)
                if product:
                    products.append(product)

                if len(products) >= limit:
                    break

            page += 1
            self._sleep()

        return products

    def _parse_list_item(self, ul) -> dict | None:
        name_el = ul.select_one("a.urunadi")
        if not name_el:
            return None

        price_el = ul.select_one("li.fiyat a")
        score_div = ul.select_one("li.puan div[data-text]")

        price = None
        if price_el:
            price = (
                price_el.get_text(strip=True)
                .split("TL")[0]
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )

        score = score_div["data-text"] if score_div else None

        return {
            "urun_ad": name_el.get_text(strip=True),
            "urun_url": urljoin(self.base_url, name_el["href"]),
            "urun_fiyat": price,
            "urun_puan": score
        }

    # =====================================
    # PRODUCT DETAIL
    # =====================================

    def get_product_detail(self, product_url: str, product_id: int) -> dict:
        resp = self.scraper.get(
            product_url,
            headers={"Referer": self.list_base},
            timeout=30
        )
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        big_image = soup.select_one("div.buyuk img")
        if big_image and big_image.get("src"):
            image_url = big_image["src"]
            self._download_image(image_url, product_id)

        data = {}

        for group in soup.select("div#ozellikler div#grup"):
            group_title = group.select_one("h3 span")
            group_name = (
                group_title.get_text(strip=True).lower()
                if group_title else "genel"
            )

            for li in group.select("ul.grup li"):
                parsed = self._parse_detail_row(li, group_name)
                if parsed:
                    key, value = parsed
                    data[key] = value

        return data

    def _parse_detail_row(self, li, group_name: str):
        key_el = li.select_one("strong")
        val_el = li.select_one("span.cell")

        if not key_el or not val_el:
            return None

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

        return col_name, value

    def _download_image(self, image_url: str, product_id: int):
        try:
            response = self.scraper.get(image_url, timeout=30)
            response.raise_for_status()

            image_path = self.image_dir / f"{product_id}.jpg"

            with open(image_path, "wb") as f:
                f.write(response.content)

        except Exception as e:
            print(f"⚠️ Resim indirilemedi ({product_id}):", e)

    # =====================================
    # FULL SCRAPE PIPELINE
    # =====================================

    def scrape(self, limit: int = 500) -> pd.DataFrame:
        print("🚀 Popüler telefonlar alınıyor...")
        products = self.get_popular_products(limit=limit)
        print(f"✅ {len(products)} ürün bulundu")

        all_data = []

        for i, p in enumerate(products, start=1):
            print(f"[{i}/{len(products)}] {p['urun_ad']}")

            try:
                detail = self.get_product_detail(
                    p["urun_url"],
                    product_id=i
                )
                merged = {**p, **detail}
                all_data.append(merged)
                self._sleep()
            except Exception as e:
                print("❌ Hata:", p["urun_url"], e)

        df = pd.DataFrame(all_data)
        df.insert(0, "urun_id", range(1, len(df) + 1))
        return df

    def save(self, df: pd.DataFrame):
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(
            self.output_csv,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"🎉 CSV hazır: {self.output_csv}")
        print(f"📊 Ürün: {len(df)}, Kolon: {len(df.columns)}")

    # =====================================
    # ENTRY POINT
    # =====================================

    def run(self, limit: int = 500):
        df = self.scrape(limit=limit)
        self.save(df)
        print("Scraping tamamlandı.")

if __name__ == "__main__":
    scraper = EpeyPhoneScraper()
    scraper.run(limit=1000)