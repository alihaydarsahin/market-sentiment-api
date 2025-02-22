from datetime import datetime

def save_text_summary():
    summary = """
HABER ANALİZİ PROJESİ - ÖZET

1. VERİ TOPLAMA
   - News API'den güncel haberler
   - Kategorilere göre sınıflandırma
   - 9 farklı kategori

2. ANALİZ TÜRLERİ
   - Duygu Analizi (TextBlob)
   - Etkileşim Analizi
   - Kategori Analizi
   - Etki Analizi

3. GÖRSELLEŞTİRMELER
   - Kategori dağılımları
   - Duygu-etkileşim ilişkileri
   - En etkili haberler

4. ÇIKTILAR
   - JSON raporları
   - Grafikler
   - Log kayıtları

Tarih: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    with open('data/analysis/summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)

if __name__ == "__main__":
    save_text_summary() 