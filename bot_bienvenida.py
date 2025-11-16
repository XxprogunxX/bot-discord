from keep_alive import keep_alive
import discord
import os
import aiohttp
import asyncio
import time

# ------------------ CONFIG DISCORD ------------------
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

ID_CANAL_BIENVENIDA = 875180338366803979
ID_CANAL_DESPEDIDA = 875184506548662272
ID_CANAL_TWITCH = 1439420598316175481

# ------------------ CONFIG TWITCH ------------------
TWITCH_USER = os.getenv("TWITCH_USER")
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
CHECK_SECONDS = int(os.getenv("TWITCH_CHECK_SECONDS", 60))

ya_notificado = False

# Cache del token
TWITCH_TOKEN = None
TOKEN_EXPIRE = 0


# ------------------ TOKEN TWITCH ASYNC ------------------
async def obtener_token_twitch(session):
    global TWITCH_TOKEN, TOKEN_EXPIRE

    if TWITCH_TOKEN and time.time() < TOKEN_EXPIRE:
        return TWITCH_TOKEN

    print("🟣 Obteniendo nuevo token de Twitch...")

    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }

    async with session.post(url, data=payload) as resp:
        data = await resp.json()

    TWITCH_TOKEN = data["access_token"]
    TOKEN_EXPIRE = time.time() + data["expires_in"] - 60

    return TWITCH_TOKEN


# ------------------ VERIFICAR STREAM (ASYNC) ------------------
async def verificar_stream(session):
    global ya_notificado

    token = await obtener_token_twitch(session)

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }

    url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USER}"

    try:
        async with session.get(url, headers=headers) as resp:

            # Manejo de límite de peticiones
            if resp.status == 429:
                print("⛔ RATE LIMIT Twitch — esperando 60s")
                await asyncio.sleep(60)
                return

            data = await resp.json()

    except Exception as e:
        print(f"⚠ Error al consultar Twitch: {e}")
        return

    # Si está en vivo:
    if data.get("data"):
        stream = data["data"][0]

        if not ya_notificado:
            canal = client.get_channel(ID_CANAL_TWITCH)

            titulo = stream["title"]
            juego = stream.get("game_name", "Desconocido")

            embed = discord.Embed(
                title="🟣 ¡STREAM EN VIVO!",
                description=f"**{TWITCH_USER}** acaba de iniciar directo.\n\n**{titulo}**",
                color=0x9146FF
            )

            embed.add_field(name="Juego", value=juego)
            embed.add_field(name="Ver Stream", value=f"https://twitch.tv/{TWITCH_USER}")
            embed.set_image(url=f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{TWITCH_USER}-640x360.jpg")

            await canal.send(embed=embed)
            print("🔔 Notificación enviada")

            ya_notificado = True

    else:
        # Directo finalizado (no notificar)
        if ya_notificado:
            print("🟤 Stream finalizado. Esperando siguiente directo.")
        ya_notificado = False


# ------------------ READY EVENT ------------------
@client.event
async def on_ready():
    print(f"Bot listo como {client.user}")

    async with aiohttp.ClientSession() as session:
        while True:
            await verificar_stream(session)
            await asyncio.sleep(CHECK_SECONDS)


# ------------------ BIENVENIDA ------------------
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


# ------------------ DESPEDIDA ------------------
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


# ------------------ KEEP ALIVE ------------------
keep_alive()

# ------------------ RUN ------------------
TOKEN = os.getenv("DISCORD_TOKEN")
client.run(TOKEN)
