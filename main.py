import openai

import pykanka
import discord
import re

from discord.ext import commands

import yaml
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

with open("secrets.yaml", "r") as f:
    tokens = yaml.unsafe_load(f)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="&", intents=intents)

openai.api_key = tokens.get("openai")

kanka_key = tokens.get("kanka")

client: "pykanka.CampaignClient"


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


@bot.command()
async def image(ctx, *prompt):
    await ctx.send(create_image(prompt=" ".join(prompt)))


@bot.command()
async def create(ctx, entity_type, *description):
    if client is None:
        await ctx.send("You must set a campaign first. Use &campaign {campaign.id}")
        return

    boilerplate = f"For a fantasy world, create a {entity_type} based on the following description. Provide a short " \
                  f"description, point out connections to other things in the world. Be concise and creative, think of " \
                  f"names where applicable. First provide the name, then in a new line provide the description" \
                  f"Here is the prompt: \n"

    prompt = boilerplate + " ".join(description)
    if not prompt.endswith("."):
        prompt += "."

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=512
    )

    text = response["choices"][0]["text"]

    try:
        name_unparsed, entry = text.strip("\n\r ").split("\n", maxsplit=1)

        name = re.match(r"(?:[Nn]ame(?: is)*[:=]*)* *(.+)", name_unparsed).group(0)
    except ValueError:
        await ctx.send("Couldn't parse response, try again or add manually: \n" + text)
        return

    image_prompt_boilerplate = f"Write a DALL-E prompt that generates a image for the following description. " \
                               f"It should be short and concise and only describe what there is to see in the image." \
                               f"It should fit a DnD-campaign with a serious, low fantasy tone. " \
                               f"Here's the description: \n"
    image_prompt = openai.Completion.create(
        model="text-davinci-003",
        prompt=image_prompt_boilerplate + entry,
        max_tokens=256
    )
    image_text = image_prompt["choices"][0]["text"]

    image_response = create_image(image_text)

    entity = client.create_entity(entity_type=entity_type, name=name, entry=entry, image_url=image_response)

    await ctx.send(f"Created {name}: entity.urls.view\n{image_response}{entry}")

@bot.command()
async def campaign(ctx, campaign_id):
    global client
    client = pykanka.CampaignClient(campaign_id=campaign_id, token=tokens.get("kanka"), locale="en")
    await ctx.send(f"Set campaign to {campaign_id}")


def create_image(prompt):
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    return response["data"][0]["url"]


bot.run(tokens.get("discord"))
