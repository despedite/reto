# New encryption method (1.6)!
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract, delete
import tinydb_encrypted_jsonstorage as tae
from os.path import join as join_path
from os.path import exists
from random import *
import string
import sys
import os

# Boolean to string parser.
from distutils.util import strtobool

def createConfigFile():
	print("We haven't detected a config file! Let's do some setup before we get started.\n")
	
	if not exists("json/"):
		os.mkdir('json')
	cfg = TinyDB("json/config.json") #Creates the config file.

	# Encryption key
	print("Enter the ENCRYPTION KEY (1/8)")
	print("The bot automatically encrypts its databases, so not you nor anyone else can access them. This is the encryption key the bot uses to encrypt said databases. This string can be anything, but it's recommended to use a strong, randomly-chosen password, just in case. DO NOT SHARE THIS KEY.")
	# Generate a secure password.
	characters = string.ascii_letters + string.punctuation  + string.digits
	randomPassword =  "".join(choice(characters) for x in range(randint(16, 32)))
	print("(default: " + randomPassword + ")")
	pwdInput = input("")
	if not pwdInput:
		pwdInput = randomPassword
	
	# Bot token
	print("\nEnter BOT TOKEN (2/8)")
	print("This is the bot token Discord generates for you when you've created a bot on the Discord Developer Portal. Here's an in-depth guide on how to create a Discord bot, if you haven't done so already. DO NOT SHARE THIS TOKEN.")
	tknInput = input("")
	if not tknInput:
		sys.exit()

	# Bot name
	print("\nEnter BOT NAME (3/8)")
	print("Replaces all instances of the bot's name (in this case, Reto) to its own. Change this if you'll name your bot anything other than Reto.")
	print("(default: Reto)")
	nmeInput = input("")
	if not nmeInput:
		nmeInput = "Reto"
	
	# Prefix
	print("\nEnter PREFIX (4/8):")
	print("The default prefix Reto uses on DMs and all servers that haven't set their own custom prefix.")
	print("(default: ?)")
	prxInput = input("")
	if not prxInput:
		prxInput = "?"
	
	# Support server
	print("\nEnter SUPPORT SERVER (5/8):")
	print("Links to the support server shown on the ?setup command, error messages, et cetera.")
	print("(default: https://discord.gg/rrszpTN)")
	ssvInput = input("")
	if not ssvInput:
		ssvInput = "https://discord.gg/rrszpTN"
	
	# Bot version
	print("\nEnter BOT VERSION (6/8):")
	print("The bot's current version. Appears on its Activities and other places.")
	print("(default: 1.6a)")
	verInput = input("")
	if not verInput:
		verInput = "1.6a"

	# Bot owner
	print("\nEnter BOT OWNER (7/8):")
	print("An array of the people that are the bot's developers. You should fill this out with your user ID to gain access to certain bot owner specific commands (and a badge on your ?profile).")
	print("(enter IDs one after the other, press ENTER on an empty new line when you're done)")
	ownInput = []
	ownInput.append(input(""))
	if not ownInput[0]:
		sys.exit()
	while ownInput[len(ownInput) - 1]:
		ownInput.append(input(""))
	ownInput.remove(ownInput[len(ownInput)-1])

	# Debug
	print("\nEnter DEBUG (8/8):")
	print("Boolean (True/False) that's useful if you wanna test certain commands alone. Its main use is letting you vote on your own posts. Make sure this is set as 'False' when you're done coding.")
	print("(True/False, default/invalid: False)")
	dbgInput = input("")
	if (dbgInput!= "True" or "False") or not dbgInput:
		dbgInput = "False"
	
	# Insert all that data!
	cfg.insert({'key': pwdInput, 'bottoken': tknInput, "botname": nmeInput, "prefix": prxInput, "support": ssvInput, "botver": verInput, "botowner": ownInput, "debug": dbgInput})

if not exists("json/") or not exists("json/config.json"):
	createConfigFile()

# Unencrypted! This NEEDS to be editable by a simple text editor.
cfg = TinyDB("json/config.json") #Config file: stores configurations for the bot. Modify at your heart's content!

for c in cfg:
	bottoken = c['bottoken']
	botname  = c['botname']
	support  = c['support']
	botver   = c['botver']
	prefix   = c['prefix']
	botowner = c['botowner']
	key 	 = c['key']
	debug    = c['debug']
	debug    = bool(strtobool(debug)) # Otherwhise, it's a string.



db           = TinyDB(encryption_key=key, path=join_path("db/","profile.reto"), storage=tae.EncryptedJSONStorage) #Database file: stores points of every user.
srv          = TinyDB(encryption_key=key, path=join_path("db/","srv.reto"), storage=tae.EncryptedJSONStorage) #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.
activity     = TinyDB(encryption_key=key, path=join_path("db/","activity.reto"), storage=tae.EncryptedJSONStorage) #Activity file: the "Playing" commands the bot has.
post         = TinyDB(encryption_key=key, path=join_path("db/","comments.reto"), storage=tae.EncryptedJSONStorage) #Comment leaderboard.
priv         = TinyDB(encryption_key=key, path=join_path("db/","blacklist.reto"), storage=tae.EncryptedJSONStorage) #Privacy Mode blacklist. Users with PM on will not have their messages logged in the comment leaderboard.
best         = TinyDB(encryption_key=key, path=join_path("db/","best.reto"), storage=tae.EncryptedJSONStorage) #Best Of name: Used to look up the Best-Of name of the channel.
dm           = TinyDB(encryption_key=key, path=join_path("db/","deletables.reto"), storage=tae.EncryptedJSONStorage) #Message deletion for Leaderboards.
customprefix = TinyDB(encryption_key=key, path=join_path("db/","customprefix.reto"), storage=tae.EncryptedJSONStorage) #Prefix file: custom prefixes per server.
chan         = TinyDB(encryption_key=key, path=join_path("db/","channels.reto"), storage=tae.EncryptedJSONStorage) #Channel file: Used for Autovotes and other channel specific features.