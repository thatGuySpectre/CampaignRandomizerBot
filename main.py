import openai
import chatgpt
import pykanka
import discord
from discord.ext import commands

import yaml
import logging

with open("secrets.yaml", "r") as f:
    tokens = yaml.unsafe_load(f)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="&", intents=intents)

openai.api_key = tokens.get("openai")

kanka_key = tokens.get("kanka")


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


@bot.command()
async def image(ctx, prompt):
    a = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    await ctx.send(a)


@bot.command()
async def create(ctx, entity_type, description):
    pass

con = chatgpt.Conversation()
print(con.chat("Who are you?"))

bot.run(tokens.get("discord"))
