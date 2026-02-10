import csv
import pandas as pd
from pathlib import Path
from collections import Counter

class DatasetProcessor:
    
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parents[3]
        self.raw_input = self.base_dir / 'app' / 'outputs' / 'datasets' / 'phones' / 'raw' / 'full_dataset.csv'
        self.filtered_dataset = self.base_dir / 'app' / 'outputs' / 'datasets' / 'phones' / 'processed' / 'filtered_dataset.csv'

        self.selected_features = [
            'urun_fiyat',
            'urun_puan',
            'ekran_ekran_boyutu',
            'ekran_ekran_teknolojisi',
            'ekran_ekran_çözünürlüğü_standardı',
            'ekran_ekran_yenileme_hızı',
            'ekran_ekran_dayanıklılığı',
            'batarya_batarya_kapasitesi_tipik',
            'batarya_hızlı_şarj',
            'batarya_hızlı_şarj_gücü_maks.',
            'batarya_kablosuz_şarj',
            'kamera_kamera_çözünürlüğü',
            'kamera_optik_görüntü_sabitleyici_ois',
            'kamera_video_kayıt_çözünürlüğü',
            'kamera_video_fps_değeri',
            'kamera_ön_kamera_çözünürlüğü',
            'temel_donanim_yonga_seti_chipset',
            'temel_donanim_cpu_çekirdeği',
            'temel_donanim_cpu_üretim_teknolojisi',
            'temel_donanim_antutu_puanı_v10',
            'temel_donanim_bellek_ram',
            'temel_donanim_dahili_depolama',
            'tasarim_kalınlık',
            'tasarim_ağırlık',
            'tasarim_gövde_malzemesi_kapak',
            'ağ_bağlantilari_5g',
            'kablosuz_bağlantilar_bluetooth_versiyonu',
            'kablosuz_bağlantilar_nfc',
            'i̇şleti̇m_si̇stemi̇_i̇şletim_sistemi',
            'özelli̇kler_suya_dayanıklılık',
            'özelli̇kler_suya_dayanıklılık_seviyesi'
        ]

    def generate_filtered_dataset(self):
        print(f'Reading: {self.raw_input}')
        if not self.raw_input.exists():
            raise FileNotFoundError(f'Input CSV not found: {self.raw_input}')
        
        with self.raw_input.open(newline='', encoding='utf-8') as inf:
            reader = csv.DictReader(inf)
            existing = [c for c in self.selected_features if c in reader.fieldnames]
            missing = [c for c in self.selected_features if c not in reader.fieldnames]
            
            if missing:
                print('Warning - these selected columns were not found and will be skipped:')
                for m in missing:
                    print('  -', m)
            
            with self.filtered_dataset.open('w', newline='', encoding='utf-8') as outf:
                writer = csv.DictWriter(outf, fieldnames=existing)
                writer.writeheader()
                for row in reader:
                    out = {k: row.get(k, '') for k in existing}
                    writer.writerow(out)
        
        print(f'✓ Wrote: {self.filtered_dataset} (columns: {len(existing)})\n')
        return len(existing)
    
if __name__ == '__main__':
    processor = DatasetProcessor()
    
    print('='*70)
    print('UNIFIED DATASET PROCESSOR')
    print('='*70)
    
    print('[1/1] Generating filtered dataset...')
    processor.generate_filtered_dataset()
    
    print('\n' + '='*70)
    print('✓ All dataset operations complete!')
    print('='*70)