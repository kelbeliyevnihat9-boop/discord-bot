import discord
from discord.ext import commands
from datetime import timedelta
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

AUTHORIZED_ROLES = ["Nihad", "Yetkili", "Moderatör"]
AUTO_ROLE_NAME = "Üye"

user_stats = {}

def has_permission(member: discord.Member):
    return any(role.name in AUTHORIZED_ROLES for role in member.roles)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot aktif: {bot.user}")

@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name=AUTO_ROLE_NAME)
    if role:
        await member.add_roles(role)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = message.author.id
    if uid not in user_stats:
        user_stats[uid] = {"messages": 0, "images": 0}

    user_stats[uid]["messages"] += 1

    if message.attachments:
        user_stats[uid]["images"] += len(message.attachments)

    text = message.content.lower()

    replies = {
        "selam": "Selam dostum 👋",
        "merhaba": "Merhaba dostum 🫡",
        "günaydın": "Günaydın dostum 🌅",
        "iyi akşamlar": "İyi akşamlar, dostum 🌃",
        "iyi geceler": "İyi geceler, dostum 🌉"
    }

    if text in replies:
        await message.reply(replies[text])

    if "nasılsın" in text or "iyi misin" in text:
        await message.reply("İyiyim dostum 💙 Sen nasılsın?")

    await bot.process_commands(message)

@bot.tree.command(name="info", description="Sunucu bilgisi")
async def info(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Bu sunucu, **Hile ve Expoları sizle bölüşmek için yapılmış**, "
        "**Sahibi nihadiniz olan bir hile, roblox sunucusudur.**"
    )

@bot.tree.command(name="mute", description="Kullanıcıyı sustur")
async def mute(interaction: discord.Interaction, member: discord.Member, dakika: int):
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
        return

    await member.timeout(timedelta(minutes=dakika))
    await interaction.response.send_message(
        f"🔇 {member.mention} {dakika} dakika mute edildi."
    )

@bot.tree.command(name="ban", description="Kullanıcıyı banla")
async def ban(interaction: discord.Interaction, member: discord.Member, sebep: str):
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
        return

    await member.ban(reason=sebep)
    await interaction.response.send_message(
        f"⛔ {member} banlandı.\nSebep: {sebep}"
    )

@bot.tree.command(name="mesaj-sil", description="Mesaj ID ile sil")
async def mesaj_sil(interaction: discord.Interaction, mesaj_id: str):
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
        return

    try:
        msg = await interaction.channel.fetch_message(int(mesaj_id))
        await msg.delete()
        await interaction.response.send_message("🗑️ Mesaj silindi.")
    except:
        await interaction.response.send_message("❌ Mesaj bulunamadı.")

@bot.tree.command(name="user-info", description="Kullanıcı bilgileri")
async def user_info(interaction: discord.Interaction, member: discord.Member):
    stats = user_stats.get(member.id, {"messages": 0, "images": 0})
    güven = "GÜVENİLİR ✅" if stats["messages"] >= 20 else "DİKKAT ⚠️"

    embed = discord.Embed(title="👤 Kullanıcı Bilgisi", color=discord.Color.blue())
    embed.add_field(name="📅 Hesap Açma", value=member.created_at.strftime("%d.%m.%Y"), inline=False)
    embed.add_field(name="📥 Sunucuya Katılma", value=member.joined_at.strftime("%d.%m.%Y"), inline=False)
    embed.add_field(name="💬 Mesaj Sayısı", value=stats["messages"])
    embed.add_field(name="🖼️ Görsel Sayısı", value=stats["images"])
    embed.add_field(name="🔐 Güven", value=güven, inline=False)

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
