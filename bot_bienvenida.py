from keep_alive import keep_alive
import discord
import os
# Configuración de permisos (Intents)
intents = discord.Intents.default()
intents.members = True  # <--- VITAL para ver quién entra y sale

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
            title="¡Nuevo Tripulante a bordo!", 
            description=f"Bienvenido al servidor, {member.mention}", # Usamos mention para que le llegue notificación
            color=0x00ff00 # Verde
        )
        # Ponemos la foto del usuario
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        await canal.send(embed=embed)
        print(f"Bienvenida enviada para {member.name}")

# --- EVENTO DE SALIDA (DESPEDIDA) ---
@client.event
async def on_member_remove(member):
    canal = client.get_channel(ID_CANAL_DESPEDIDA)
    
    if canal:
        embed = discord.Embed(
            title="Un tripulante ha partido...", 
            description=f"**{member.name}** ha abandonado la nave.", # Sin mention, solo el nombre
            color=0xff0000 # Rojo
        )
        # Ponemos la foto del usuario
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        await canal.send(embed=embed)
        print(f"Despedida enviada para {member.name}")

# Pega aquí tu NUEVO TOKEN (regenera el que mostraste por seguridad)
keep_alive()
TOKEN = os.getenv("DISCORD_TOKEN")