from keep_alive import keep_alive
import discord
import os

# Configuración de permisos (Intents)
intents = discord.Intents.default()
intents.members = True  # Necesario para detectar join/leave

client = discord.Client(intents=intents)

# TUS CANALES
ID_CANAL_BIENVENIDA = 875180338366803979
ID_CANAL_DESPEDIDA = 875184506548662272

@client.event
async def on_ready():
    print(f'Bot conectado y listo como {client.user}')

# --- EVENTO DE ENTRADA (BIENVENIDA) ---
@client.event
async def on_member_join(member):
    canal = client.get_channel(ID_CANAL_BIENVENIDA)
    
    if canal:
        embed = discord.Embed(
            title="¡Nuevo Tripulante a bordo! 🚀",
            description=f"Bienvenido al servidor, {member.mention}",
            color=0x00ff00
        )

        # Foto del usuario
        embed.set_thumbnail(
            url=member.avatar.url if member.avatar else member.default_avatar.url
        )

        # 👉 Si quieres agregar un GIF aquí, descomenta esta línea:
        embed.set_image(url="https://i.pinimg.com/originals/7a/e5/c3/7ae5c335819cffea1cbdf982d78a7fc7.gif")

        await canal.send(embed=embed)
        print(f"Bienvenida enviada para {member.name}")

# --- EVENTO DE SALIDA (DESPEDIDA) ---
@client.event
async def on_member_remove(member):
    canal = client.get_channel(ID_CANAL_DESPEDIDA)
    
    if canal:
        embed = discord.Embed(
            title="Un tripulante ha partido... 💔",
            description=f"**{member.name}** ha abandonado la nave.",
            color=0xff0000
        )

        embed.set_thumbnail(
            url=member.avatar.url if member.avatar else member.default_avatar.url
        )

        # 👉 Si quieres GIF de despedida:
        embed.set_image(url="https://imgur.com/RTmvbzu.gif")

        await canal.send(embed=embed)
        print(f"Despedida enviada para {member.name}")

# INICIA EL SERVIDOR FLASK
keep_alive()

# TOKEN
TOKEN = os.getenv("DISCORD_TOKEN")

# EJECUTAR EL BOT
client.run(TOKEN)
