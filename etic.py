from datetime import datetime
from typing import List, Tuple

class Kategori:
    def __init__(self, isim: str, aciklama: str = ""):
        """
        Initialize a product category
        :param isim: Category name
        :param aciklama: Category description (optional)
        """
        self.isim = isim
        self.aciklama = aciklama
        self.urunler: List['Urun'] = []
        self.olusturulma_tarihi = datetime.now()
        self.guncelleme_tarihi = datetime.now()

    def urun_ekle(self, urun: 'Urun') -> None:
        """Add a product to this category"""
        if urun not in self.urunler:
            self.urunler.append(urun)
            self.guncelleme_tarihi = datetime.now()
            print(f"{urun.isim} ürünü {self.isim} kategorisine eklendi.")
        else:
            print(f"{urun.isim} zaten bu kategoride mevcut.")

    def urun_cikar(self, urun: 'Urun') -> None:
        """Remove a product from this category"""
        if urun in self.urunler:
            self.urunler.remove(urun)
            self.guncelleme_tarihi = datetime.now()
            print(f"{urun.isim} ürünü kategoriden çıkarıldı.")
        else:
            print(f"{urun.isim} bu kategoride bulunamadı.")

    def urunleri_listele(self) -> None:
        """List all products in this category with details"""
        print(f"\n{'='*50}")
        print(f"{self.isim} Kategorisi ({len(self.urunler)} ürün)")
        print(f"Oluşturulma: {self.olusturulma_tarihi.strftime('%d.%m.%Y %H:%M')}")
        print(f"Son Güncelleme: {self.guncelleme_tarihi.strftime('%d.%m.%Y %H:%M')}")
        print(f"Açıklama: {self.aciklama}")
        print(f"\nÜrün Listesi:")
        for i, urun in enumerate(self.urunler, 1):
            print(f"{i}. {urun.bilgileri_goster()}")
        print("="*50)

    def __str__(self) -> str:
        return f"{self.isim} Kategorisi ({len(self.urunler)} ürün)"


class Urun:
    def __init__(self, isim: str, fiyat: float, stok: int, kategori: Kategori, 
                 aciklama: str = "", indirim: float = 0.0):
        """
        Initialize a product
        :param isim: Product name
        :param fiyat: Unit price
        :param stok: Stock quantity
        :param kategori: Product category
        :param aciklama: Product description (optional)
        :param indirim: Discount percentage (0-100)
        """
        self.isim = isim
        self.fiyat = max(0, fiyat)
        self.stok = max(0, stok)
        self.kategori = kategori
        self.aciklama = aciklama
        self.indirim = min(100, max(0, indirim))
        self.olusturulma_tarihi = datetime.now()
        self.kategori.urun_ekle(self)

    @property
    def indirimli_fiyat(self) -> float:
        """Calculate discounted price"""
        return self.fiyat * (1 - self.indirim / 100)

    def bilgileri_goster(self) -> str:
        """Display product information"""
        fiyat_bilgisi = f"{self.indirimli_fiyat:.2f} TL"
        if self.indirim > 0:
            fiyat_bilgisi += f" (%{self.indirim} indirim, normal fiyat {self.fiyat:.2f} TL)"
        
        return (f"{self.isim} - {fiyat_bilgisi} - Stok: {self.stok} "
                f"- Kategori: {self.kategori.isim}")

    def stok_guncelle(self, miktar: int) -> bool:
        """Update stock quantity"""
        if self.stok + miktar >= 0:
            self.stok += miktar
            return True
        print(f"Stok güncelleme başarısız! Yetersiz stok: {self.isim}")
        return False

    def indirim_uygula(self, indirim: float) -> None:
        """Apply discount to product"""
        self.indirim = min(100, max(0, indirim))
        print(f"{self.isim} ürününe %{indirim} indirim uygulandı.")

    def __str__(self) -> str:
        return self.bilgileri_goster()


class Siparis:
    def __init__(self, musteri_adi: str, musteri_email: str = "", musteri_adres: str = ""):
        """
        Initialize an order
        :param musteri_adi: Customer name
        :param musteri_email: Customer email (optional)
        :param musteri_adres: Customer address (optional)
        """
        self.musteri_adi = musteri_adi
        self.musteri_email = musteri_email
        self.musteri_adres = musteri_adres
        self.urunler: List[Tuple[Urun, int]] = []
        self.tarih = datetime.now()
        self.durum = "Hazırlanıyor"
        self.siparis_no = self._generate_order_number()

    def _generate_order_number(self) -> str:
        """Generate a unique order number"""
        return f"ORD-{self.tarih.strftime('%Y%m%d-%H%M%S')}-{hash(self.musteri_adi) % 10000:04d}"

    def urun_ekle(self, urun: Urun, adet: int = 1) -> bool:
        """Add product to order"""
        if adet <= 0:
            print("Geçersiz adet miktarı!")
            return False
            
        if urun.stok >= adet:
            self.urunler.append((urun, adet))
            urun.stok -= adet
            print(f"{adet} adet {urun.isim} siparişe eklendi.")
            return True
        else:
            print(f"Yetersiz stok: {urun.isim} (Kalan: {urun.stok}, İstenen: {adet})")
            return False

    def urun_cikar(self, urun: Urun, adet: int = None) -> bool:
        """Remove product from order"""
        for item in self.urunler:
            if item[0] == urun:
                if adet is None or adet >= item[1]:
                    # Remove all of this product
                    urun.stok += item[1]
                    self.urunler.remove(item)
                    print(f"{urun.isim} ürünü siparişten tamamen çıkarıldı.")
                else:
                    # Remove partial quantity
                    item[1] -= adet
                    urun.stok += adet
                    print(f"{adet} adet {urun.isim} siparişten çıkarıldı.")
                return True
        print(f"{urun.isim} bu siparişte bulunamadı.")
        return False

    def siparis_durumu_guncelle(self, yeni_durum: str) -> None:
        """Update order status"""
        durumlar = ["Hazırlanıyor", "Kargoda", "Teslim Edildi", "İptal Edildi"]
        if yeni_durum in durumlar:
            self.durum = yeni_durum
            print(f"Sipariş durumu '{yeni_durum}' olarak güncellendi.")
        else:
            print(f"Geçersiz durum! Geçerli durumlar: {', '.join(durumlar)}")

    def toplam_tutar(self) -> float:
        """Calculate total order amount"""
        return sum(urun.indirimli_fiyat * adet for urun, adet in self.urunler)

    def detaylar(self) -> None:
        """Display order details"""
        print(f"\n{'='*50}")
        print(f"SİPARİŞ DETAYLARI")
        print(f"Sipariş No: {self.siparis_no}")
        print(f"Müşteri: {self.musteri_adi}")
        if self.musteri_email:
            print(f"E-posta: {self.musteri_email}")
        if self.musteri_adres:
            print(f"Adres: {self.musteri_adres}")
        print(f"Tarih: {self.tarih.strftime('%d.%m.%Y %H:%M')}")
        print(f"Durum: {self.durum}")
        print("\nÜrünler:")
        for i, (urun, adet) in enumerate(self.urunler, 1):
            print(f"{i}. {urun.isim} x {adet} = {urun.indirimli_fiyat * adet:.2f} TL")
        print(f"\nToplam Tutar: {self.toplam_tutar():.2f} TL")
        print("="*50)

    def __str__(self) -> str:
        return (f"Sipariş #{self.siparis_no} - {self.musteri_adi} - "
                f"{self.toplam_tutar():.2f} TL - {self.durum}")


# Example Usage
if __name__ == "__main__":
    # Create categories
    elektronik = Kategori("Elektronik", "Tüm elektronik ürünler")
    ev_yasam = Kategori("Ev & Yaşam", "Ev ve yaşam ürünleri")

    # Create products
    telefon = Urun("Akıllı Telefon", 5000, 10, elektronik, 
                  "Yeni model akıllı telefon", 10)
    tablet = Urun("Tablet", 3000, 5, elektronik, "10 inç tablet")
    süpürge = Urun("Robot Süpürge", 2500, 8, ev_yasam, "Akıllı robot süpürge", 15)

    # List categories
    elektronik.urunleri_listele()
    ev_yasam.urunleri_listele()

    # Create an order
    siparis = Siparis("Ahmet Yılmaz", "ahmet@example.com", "İstanbul, Türkiye")
    siparis.urun_ekle(telefon, 2)
    siparis.urun_ekle(tablet, 1)
    siparis.urun_ekle(süpürge, 1)

    # Show order details
    siparis.detaylar()

    # Update order status
    siparis.siparis_durumu_guncelle("Kargoda")

    # Remove a product from order
    siparis.urun_cikar(tablet)

    # Show updated order details
    siparis.detaylar()
