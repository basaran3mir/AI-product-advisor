import requests

API_URL = "http://127.0.0.1:5000/predict"

# Gerçek dataset formatında örnek veri (step3_keep_selected_columns.csv)
sample_data = {
    "ekran_ekran_boyutu": "6.9 İnç",
    "ekran_ekran_teknolojisi": "OLED",
    "ekran_ekran_çözünürlüğü_standardı": "FHD+",
    "ekran_ekran_yenileme_hızı": "120 Hz",
    "batarya_batarya_kapasitesi_tipik": "4832 mAh",
    "batarya_hızlı_şarj": "Var",
    "batarya_hızlı_şarj_gücü_maks.": "40 W",
    "batarya_kablosuz_şarj": "Var",
    "kamera_kamera_çözünürlüğü": "48 MP",
    "kamera_optik_görüntü_sabitleyici_ois": "Var",
    "kamera_video_kayıt_çözünürlüğü": "2160p (Ultra HD) 4K",
    "kamera_video_fps_değeri": "60 fps",
    "kamera_ön_kamera_çözünürlüğü": "18 MP",
    "temel_donanim_cpu_çekirdeği": "6 Çekirdek",
    "temel_donanim_cpu_üretim_teknolojisi": "3 nm",
    "temel_donanim_antutu_puanı_v10": "2.697.900 Puan",
    "temel_donanim_bellek_ram": "12 GB",
    "temel_donanim_dahili_depolama": "256 GB",
    "tasarim_kalınlık": "8.75 mm",
    "tasarim_ağırlık": "231 Gram",
    "tasarim_gövde_malzemesi_kapak": "Cam",
    "ağ_bağlantilari_5g": "Var",
    "kablosuz_bağlantilar_bluetooth_versiyonu": "6.0",
    "kablosuz_bağlantilar_nfc": "Var",
    "i̇şleti̇m_si̇stemi̇_i̇şletim_sistemi": "iOS",
    "özelli̇kler_suya_dayanıklılık": "Var"
}

response = requests.post(API_URL, json=sample_data)

print("Status Code:", response.status_code)
print("Response:", response.json())
