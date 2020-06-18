import datetime
import asyncio
import discord
from discord.ext import commands
from discord import Emoji
import os

description = 'Bot para marcar presença em guerra e criar lista de espera'
bot = commands.Bot(command_prefix='.', description=description)
token = os.getenv('BOT_TOKEN')
message_id = int(os.getenv('BOT_MESSAGE_ID'))

print(message_id)
attend = []
renegades = []
pa_list = []
pepe_mage = '<:bdohogwards:697145353992011907>'

async def check_reactions(payload):
	if payload.message_id == message_id and payload.user_id != bot.user.id:
		if payload.emoji.name == '👍':
			attend.append(payload.member.display_name)
			print('go ' + str(payload.member.display_name))

		if payload.emoji.name == 'bdohogwards':
			pa_list.append(payload.member.display_name)
			print('PA ' + str(payload.member.display_name))

async def remove_reaction(payload):
	payload_member = bot.get_guild(payload.guild_id).get_member(payload.user_id)
	if payload.message_id == message_id:
		if payload_member.display_name not in renegades:
			timestamp = datetime.datetime.now()
			print('renegade ' + payload_member.display_name + ' ' + timestamp.strftime("%d/%m %H:%M"))
			renegades.append(payload_member.display_name + ' ' + payload.emoji.name + ' ' + timestamp.strftime("%d/%m %H:%M"))
		if payload.emoji.name == '👍':
			attend.remove(payload_member.display_name)
		if payload.emoji.name == 'bdohogwards':
			pa_list.remove(payload_member.display_name)

bot.add_listener(check_reactions, 'on_raw_reaction_add')
bot.add_listener(remove_reaction, 'on_raw_reaction_remove')

@bot.event
async def on_ready():
	print('Bot ID: ', bot.user.id)
	print('Bot name: ', bot.user.name)
	print('---------------')
	print('This bot is ready for action!')
	print('I\'m currently on those servers: ')
	for guild in bot.guilds:
		print(guild)

@bot.command()
async def peixinho(ctx):
	'''glub! '''
	await ctx.send('_glub glub_')

@bot.command()
async def updatelist(ctx):
	async for message in ctx.channel.history(limit=None):
		if message.author.id is bot.user.id:
			global message_id
			message_id = message.id
			for reaction in message.reactions:
				if reaction.emoji == '👍':
					async for user in reaction.users():
						if user not in attend and user.id is not bot.user.id:
							attend.append(user.display_name)
				
				if isinstance(reaction.emoji, Emoji):
					if reaction.emoji.name == 'bdohogwards':
						async for user in reaction.users():
							if user not in pa_list and user.id is not bot.user.id:
								pa_list.append(user.display_name)

	print('attend' + str(len(attend)))
	print('pa' + str(len(pa_list)))

@bot.command()
async def guerra(ctx, *, text):
	'''Cria uma mensagem para os participantes reagirem se vão ou não vão '''
	message = await ctx.send(text)
	global message_id
	message_id = message.id
	os.environ['BOT_MESSAGE_ID'] = str(message_id)

	global attend
	global renegades
	global pa_list 

	attend = []
	renegades = []
	pa_list = []

	for emoji in ('👍', pepe_mage):
		await message.add_reaction(emoji)

@bot.command()
async def lista(ctx, threshold:str = '100'):
	'''lista os players que vão pra guerra com fila de espera e lista de PA'''
	separator_go = '\n+'
	separator = '\n!'

	if len(attend) <= int(threshold):
		await ctx.send("```diff\nCONFIRMADOS (" + str(len(attend)) + "): \n+"+separator_go.join(attend)+"```")
	else:
		wait = '\n-'
		await ctx.send("```diff\nCONFIRMADOS (" + threshold + "): \n+"+separator_go.join(attend[:int(threshold)])+"```")
		await ctx.send("```diff\nLISTA DE ESPERA (" + str((len(attend) - int(threshold))) + "): \n-"+wait.join(attend[int(threshold):])+"```")
		
	await ctx.send("```diff\nPA (" + str(len(pa_list)) + "): \n!"+separator.join(pa_list)+"```")

@bot.command()
async def renegados(ctx):
	'''lista os players que marcaram e tiraram a marcação'''
	separator = '\n-'
	await ctx.send("```diff\nRENEGADOS (" + str(len(renegades)) + "): \n-"+separator.join(renegades)+"```")

bot.run(token)
