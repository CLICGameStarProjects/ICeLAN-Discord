import os
import csv
import requests
import uuid
import re

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client(intents=discord.Intents.default())
pattern = re.compile(r"^.{3,32}#[0-9]{4}$")

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author.id == client.user.id:
        return

    # Only private messages
    if str(message.channel.type) != "private":
        return

    author = message.author

    if message.attachments:
        try:
            path = os.path.join("stickers", str(message.author))
            if not os.path.exists(path):
                os.makedirs(path)

            url = message.attachments[0].url
            filext = url.split(".")[-1]

            # Securiti
            print("[PHOTO]", author, url)

            with open("photos.csv", "a") as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                writer.writerow([author, url])

            response = requests.get(url)
            open(os.path.join(path, f"{uuid.uuid4()}.{filext}"), "wb").write(response.content)

            await message.reply("J'ai bien reçu ton fichier ! Il sera vérifié par un opérateur très très vite (;.", mention_author=False)
        except:
            print("[PHOTO] Error")

    else:
        try:
            tournoi, adversaire, score = message.clean_content.split(":")

            if tournoi == "" or adversaire == "" or score == "":
                await message.reply("N'oublie pas de remplir tous les champs, aucun ne doit être vide !", mention_author=False)
                return

            if not pattern.match(adversaire):  # ^.{3,32}#[0-9]{4}$
                await message.reply("Le pseudo Discord semble faux. Pour rappel, c'est du texte, puis un #, puis quatre chiffres !", mention_author=False)
                return

            # Securiti
            print("[SCORE]", tournoi, author, score, adversaire)

            with open("scores.csv", "a") as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                writer.writerow([tournoi, author, score, adversaire])

            await message.reply(f"J'ai bien reçu ton score au tournoi {tournoi} contre {adversaire}, score {author} {score} {adversaire} !\nLe résultat sera vérifié par un opérateur très très vite (:.", mention_author=False)
        except ValueError:
            await message.reply("Je n'ai pas bien compris ta demande.\n\n- Si tu souhaites donner le résultat d'un match de tournoi, utilise `Nom du tournoi:Pseudo Discord de ton adversaire:Ton score-Score de l'adversaire`;  par exemple, si tu as perdu 5-4 contre Cammonte#2347 sur Fortnite, envoie `Fortnite:Cammonte#2347:4-5`.\n- Si tu veux partager un sticker que tu as trouvé, envoie simplement la photo.\n\nBesoin d'aide ? N'hésite pas à le demander directement sur le channel discussions-générales, et à ping un @Comité !", mention_author=False)


client.run(TOKEN)
