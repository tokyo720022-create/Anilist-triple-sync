import discord
from discord.ext import commands
import os

# ==========================================
# ⚙️ 1. CORE INTENTS & INITIALIZATION
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================================
# 🚀 2. BOOT SEQUENCE
# ==========================================
@bot.event
async def on_ready():
    print("=== AEGIS OVERSEER: BOOT SEQUENCE INITIATED ===")
    print(f"✅ Logged in as {bot.user.name} (ID: {bot.user.id})")
    
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} command(s) to the server.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
        
    print("=== AEGIS OVERSEER IS FULLY ONLINE ===")

# ==========================================
# 📡 3. SLASH COMMANDS
# ==========================================
@bot.tree.command(name="status", description="Check the operational status of the Aegis Overseer.")
async def status(interaction: discord.Interaction):
    await interaction.response.send_message("🟢 **Aegis Overseer is online.** Telemetry and communication systems are nominal.")

# ==========================================
# 🔑 4. SYSTEM IGNITION
# ==========================================
# Securely pulls the token from the cloud server's vault
BOT_TOKEN = os.environ.get("MTUzOTI1MzU2MTAxMDAzMjc3Mg.GRoyMX.v_NUhwzFbjiJ1bZLQ4z1e25dCjYDQjewe1HThU")

if __name__ == '__main__':
    bot.run(BOT_TOKEN)
