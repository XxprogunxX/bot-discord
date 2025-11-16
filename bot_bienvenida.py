from keep_alive import keep_alive
import discord
import os
import requests
import asyncio

# -------- CONFIG DISCORD --------
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# CANALES DE DISCORD
ID_CANAL_BIENVENIDA = 875180338366803979
ID_CANAL_DESPEDIDA = 875184506548662272
ID_CANAL_TWITCH = 1439420598316175481  # Canal para notificaciones de Twitch

# -------- CONFIG TWITCH --------
TWITCH_USER = os.getenv("TWITCH_USER")
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
CHECK_SECONDS = int(os.getenv("TWITCH_CHECK_SECONDS", 60))

ya_notificado = False  # Para evitar SPAM


# -------- TWITCH TOKEN --------
async def obtener_token_twitch():
    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    r = requests.post(url, data=payload).json()
    return r["access_token"]


# -------- VERIFICAR STREAM --------
async def verificar_stream():
    global ya_notificado

    token = await obtener_token_twitch()
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }

    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USER}"
    r = requests.get(url, headers=headers).json()

    # ➤ Si está en directo
    if r["data"]:
        if not ya_notificado:  # Solo notifica UNA vez por stream
            canal = client.get_channel(ID_CANAL_TWITCH)

            data = r["data"][0]
            titulo = data["title"]
            juego = data["game_name"]

            embed = discord.Embed(
                title="🟣 ¡STREAM EN VIVO!",
                description=f"**{TWITCH_USER}** está EN DIRECTO.\n\n**{titulo}**",
                color=0x9146FF
            )

            embed.add_field(name="Juego", value=juego)
            embed.add_field(name="Ver en vivo", value=f"https://twitch.tv/{TWITCH_USER}")
            embed.set_image(url=f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{TWITCH_USER}-640x360.jpg")

            await canal.send(embed=embed)
            ya_notificado = True
    else:
        # ➤ NO notifiques que terminó el stream, solo resetea
        ya_notificado = False


# -------- EVENTO READY --------
@client.event
async def on_ready():
    print(f"Bot listo como {client.user}")

    # Bucle infinito que revisa Twitch cada X segundos
    while True:
        await verificar_stream()
        await asyncio.sleep(CHECK_SECONDS)


# -------- BIENVENIDA --------
@client.event
async def on_member_join(member):
    canal = client.get_channel(ID_CANAL_BIENVENIDA)
    
    if canal:
        embed = discord.Embed(
            title="¡Nuevo Tripulante a bordo! 🚀",
            description=f"Bienvenido al servidor, {member.mention}",
            color=0x00ff00
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_image(url="https://i.pinimg.com/originals/7a/e5/c3/7ae5c335819cffea1cbdf982d78a7fc7.gif")

        await canal.send(embed=embed)


# -------- DESPEDIDA --------
@client.event
async def on_member_remove(member):
    canal = client.get_channel(ID_CANAL_DESPEDIDA)

    if canal:
        embed = discord.Embed(
            title="Un tripulante ha partido... 💔",
            description=f"**{member.name}** ha abandonado la nave.",
            color=0xff0000
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_image(url="https://imgur.com/RTmvbzu.gif")

        await canal.send(embed=embed)


# -------- KEEP ALIVE --------
keep_alive()

# TOKEN DISCORD
TOKEN = os.getenv("DISCORD_TOKEN")
client.run(TOKEN)
