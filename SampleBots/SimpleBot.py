import os
import random

import discord

client = discord.Client()

@client.event
async def on_ready():
	print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_member_join(member):
	await member.create_dm()
	await member.dm_channel.send(
		f'Hi {member.name}, welcome to my Discord server!'
	)

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	starter_pokemon = [
		'I choose you, Bulbasaur!',
		'I choose you, Charmander!',
		'I choose you, Squirtle!',
	]

	if message.content == 'Which starter do I choose?':
		response = random.choice(starter_pokemon)
		await message.channel.send(response)

client.run(TOKEN)