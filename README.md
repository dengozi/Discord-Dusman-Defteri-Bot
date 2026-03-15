# ⚔️ Kin Defteri - Discord Kara Liste Botu

Bu bot, özellikle **Minecraft PvP** (NethPot, Tier sistemleri vb.) toplulukları için tasarlanmış profesyonel bir kara liste yönetim sistemidir. Düşmanlarınızı kayıt altına almanızı, nedenlerini saklamanızı ve canlı bir liste üzerinden takip etmenizi sağlar.

## ✨ Özellikler
* **Canlı Liste:** `/liste-baslat` komutuyla tek bir mesaj üzerinden sürekli güncellenen düşman listesi.
* **Detaylı Arşiv:** `/detay [isim]` komutuyla kişinin neden listede olduğunu ve eklenme tarihini görme.
* **Görsel Arayüz:** Embed mesajlar ve hareketli GIF desteği ile şık tasarım.
* **Güvenli:** `.env` desteği ile bot tokeni kodun içinde gözükmez.
* **Hızlı:** SQLite veritabanı sayesinde veriler bot kapansa bile silinmez.

## 🛠️ Kurulum

1. Bu projeyi bilgisayarınıza indirin.
2. Gerekli kütüphaneleri kurun:
   ```bash
   pip install discord.py python-dotenv
