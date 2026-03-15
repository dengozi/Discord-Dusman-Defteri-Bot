import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
from datetime import datetime

# --- AYARLAR ---
TOKEN = 'Token'

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        db_setup()
        await self.tree.sync()
        print(f"---------------------------------")
        print(f"{self.user} | CANLI LISTE & PRO ARAYUZ AKTIF")
        print(f"---------------------------------")

bot = MyBot()

def db_setup():
    conn = sqlite3.connect('kin_defteri.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dusmanlar
                 (isim TEXT PRIMARY KEY, neden TEXT, tarih TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ayarlar (anahtar TEXT PRIMARY KEY, deger TEXT)''')
    conn.commit()
    conn.close()

# --- YARDIMCI: LISTE GUNCELLEME ---
async def liste_guncelle(interaction):
    conn = sqlite3.connect('kin_defteri.db')
    c = conn.cursor()
    c.execute("SELECT isim FROM dusmanlar")
    rows = c.fetchall()

    c.execute("SELECT deger FROM ayarlar WHERE anahtar = 'liste_mesaj_id'")
    msg_data = c.fetchone()
    c.execute("SELECT deger FROM ayarlar WHERE anahtar = 'liste_kanal_id'")
    chn_data = c.fetchone()
    conn.close()

    embed = discord.Embed(
        title="═══ ⚔️ KİN DEFTERİ / KARALİSTE ⚔️ ═══",
        description="*İntikam soğuk yenen bir yemektir...*",
        color=0x2f3136
    )

    if not rows:
        embed.description = "🕊️ **HUZUR HAKİM**\nDefter tertemiz, henüz bir hain çıkmadı."
    else:
        # Daha havalı bir liste tasarımı
        liste_str = ""
        for i, r in enumerate(rows, 1):
            liste_str += f"**{i}.** 🔴 `{r[0].upper()}`\n"

        embed.add_field(name="🚨 HEDEF LİSTESİ", value=liste_str or "Liste boş.", inline=False)
        embed.set_author(name=f"Aktif Kayıt Sayısı: {len(rows)}", icon_url="https://cdn-icons-png.flaticon.com/512/0/542.png")

    embed.set_image(url="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHpod2F0M2FucHpzbHEwNnpzdjFmMmk3OGcwenFsandnOWR6czJ3NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/kzl4ReEDcT3ewwJ4wl/giphy.gif") # Opsiyonel: Buraya PvP temalı bir banner linki koyabilirsin
    embed.set_footer(text=f"Son Güncelleme: {datetime.now().strftime('%H:%M:%S')} | Detaylar için: /detay [isim]")

    if msg_data and chn_data:
        try:
            kanal = bot.get_channel(int(chn_data[0]))
            mesaj = await kanal.fetch_message(int(msg_data[0]))
            await mesaj.edit(embed=embed)
        except:
            pass

# --- KOMUTLAR ---

@bot.tree.command(name="liste-baslat", description="Canlı listeyi bu kanalda başlatır ve sabitler.")
@commands.has_permissions(administrator=True)
async def liste_baslat(interaction: discord.Interaction):
    await interaction.response.send_message("⚙️ Canlı liste sistemi kuruluyor...", ephemeral=True)

    embed = discord.Embed(title="⚔️ KİN DEFTERİ YÜKLENİYOR...", color=0x2f3136)
    mesaj = await interaction.channel.send(embed=embed)

    try:
        await mesaj.pin()
    except:
        pass # Yetki yoksa sabitleyemez ama çalışır

    conn = sqlite3.connect('kin_defteri.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO ayarlar (anahtar, deger) VALUES (?, ?)", ('liste_mesaj_id', str(mesaj.id)))
    c.execute("INSERT OR REPLACE INTO ayarlar (anahtar, deger) VALUES (?, ?)", ('liste_kanal_id', str(interaction.channel_id)))
    conn.commit()
    conn.close()
    await liste_guncelle(interaction)

@bot.tree.command(name="dusman-ekle", description="Hain birini deftere ekler.")
@app_commands.describe(isim="Düşman adı", neden="Suçu nedir?")
async def dusman_ekle(interaction: discord.Interaction, isim: str, neden: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("🚫 Yetkin yok!", ephemeral=True)

    tarih = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn = sqlite3.connect('kin_defteri.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO dusmanlar (isim, neden, tarih) VALUES (?, ?, ?)", (isim.lower(), neden, tarih))
        conn.commit()
        await interaction.response.send_message(f"💀 **{isim.upper()}** deftere işlendi!", ephemeral=True)
        await liste_guncelle(interaction)
    except sqlite3.IntegrityError:
        await interaction.response.send_message("❌ Bu şahıs zaten kayıtlı.", ephemeral=True)
    finally:
        conn.close()

@bot.tree.command(name="detay", description="Düşmanın sabıka kaydını açar.")
@app_commands.describe(isim="Bakılacak kişinin adı")
async def detay(interaction: discord.Interaction, isim: str):
    conn = sqlite3.connect('kin_defteri.db')
    c = conn.cursor()
    c.execute("SELECT neden, tarih FROM dusmanlar WHERE isim = ?", (isim.lower(),))
    row = c.fetchone()
    conn.close()

    if row:
        embed = discord.Embed(title=f"🔎 DOSYA: {isim.upper()}", color=0xff0000)
        embed.add_field(name="📂 Yapılan Hainlik", value=f"```fix\n{row[0]}```", inline=False)
        embed.add_field(name="🗓️ Kayıt Tarihi", value=row[1], inline=True)
        embed.set_footer(text="Bu dosya arşive eklenmiştir.")
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"🔍 `{isim}` adına bir kayıt bulunamadı.", ephemeral=True)

@bot.tree.command(name="dusman-sil", description="Hesabı kesilen birini siler.")
async def dusman_sil(interaction: discord.Interaction, isim: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("🚫 Yetkin yok!", ephemeral=True)

    conn = sqlite3.connect('kin_defteri.db')
    c = conn.cursor()
    c.execute("DELETE FROM dusmanlar WHERE isim = ?", (isim.lower(),))
    if conn.total_changes > 0:
        conn.commit()
        await interaction.response.send_message(f"🤝 **{isim.upper()}** defterden silindi.", ephemeral=True)
        await liste_guncelle(interaction)
    else:
        await interaction.response.send_message("🔍 İsim bulunamadı.", ephemeral=True)
    conn.close()

bot.run('token')
