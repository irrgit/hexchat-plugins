__module_name__ = "hexchat-oper"
__module_version__ = "1.1"
__module_description__ = "Ban/akill/shun user by copying their nickname and pressing a hotkey."

import hexchat
try:
	import pyperclip
except:
	print("Pyperclip is not installed")

#should move these to a config file on next release
shun_time ='5m'
shun_reason ='Pushim'
akill_time = '2d' #2 days


#below are mibbit and irccloud IPs to exclude from bans
#this list could be  dynamically added from a separate file if needed
EXCLUDE_LIST = [
'109.169.29.95'	, 
'207.192.75.252', 
'64.62.228.82'  , 
'78.129.202.38' ,
'192.184.9.108'	,
'192.184.9.110'	,
'192.184.9.112'	,
'192.184.10.118',
'192.184.10.9'	,
'170.178.187.131' 
]

#IRC protocol reply numerics on whois. Some are missing.
numerics = [
"311",
"379",
"378",
"319",
"312",
"313",
"310",
"317",
"318",
"307",
"335",
"320"
]

#main function to hook a button to a command, its parameter is fetched from the clipboard
def xline_cb(word,word_eol, _):
	global numerics

	xline_timer_handle = None


	xline_hooks = []

	#get the nickname from the clipboard
	xline_nick = pyperclip.paste()

	#issue whois on nickname
	hexchat.command("whois " + str(xline_nick))

	#function to be called later to unhook all numeric hooks
	def xline_unhook():
		for hook in xline_hooks:
			hexchat.unhook(hook)

		hexchat.unhook(xline_timer_handle)
		

	def xline_notice_cb(word, word_eol, _):

		if word[1] == '378':
			connecting_ip =  str(word[8])
			if(connecting_ip  not in str (EXCLUDE_LIST)):
				print ("os akill "+ str(connecting_ip))

		return hexchat.EAT_ALL	


	def xline_timeout_cb(_):

		xline_unhook()


	xline_hooks = [hexchat.hook_server(numeric, xline_notice_cb) for numeric in numerics]
	
	xline_timer_handle = hexchat.hook_timer(1000, xline_timeout_cb)

	return hexchat.EAT_ALL


def xshun_cb(word,word_eol, _):
	global numerics
	xshun_timer_handle = None

	#IRC protocol reply numerics on whois. Some are missing.

	xshun_hooks = []

	#get the nickname from the clipboard
	xshun_nick = pyperclip.paste()

	#issue whois on nickname
	hexchat.command("whois " + str(xshun_nick))

	#function to be called later to unhook all numeric hooks
	def xshun_unhook():
		for hook in xshun_hooks:
			hexchat.unhook(hook)

		hexchat.unhook(xshun_timer_handle)
		

	def xshun_notice_cb(word, word_eol, _):

		if word[1] == '378':
			connecting_ip =  str(word[8])
			if(connecting_ip  not in str (EXCLUDE_LIST)):
				hexchat.command("shun +*@%s %s %s" % (str(connecting_ip),shun_time,shun_reason))

		return hexchat.EAT_ALL	


	def xshun_timeout_cb(_):

		xshun_unhook()


	xshun_hooks = [hexchat.hook_server(numeric, xshun_notice_cb) for numeric in numerics]
	
	xshun_timer_handle = hexchat.hook_timer(1000, xshun_timeout_cb)

	return hexchat.EAT_ALL		


hexchat.hook_command("xshun", xshun_cb, help="/xshun <nick> , Shuns user from the server.")

hexchat.hook_command("xline", xline_cb, help="/xline <nick> , Akills user from the server.")

print(__module_version__ + " version " + __module_name__ + " loaded.")
