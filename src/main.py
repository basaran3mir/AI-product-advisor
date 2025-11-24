import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

url = "https://www.epey.com/akilli-telefonlar/"

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    },
)

driver.get(url)
time.sleep(4)

try:
    driver.execute_script("sirala('tiklama:DESC')")
    time.sleep(5)
except Exception as e:
    print("Sıralama JS fonksiyonu çalıştırılamadı:", e)

# Dinamik oluşan URL'yi al
populer_base_url = driver.current_url
print("Popüler ürünler base URL:", populer_base_url)z

driver.quit()
