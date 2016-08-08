__module_name__ = "hexchat-xline"
__module_version__ = "1.1"
__module_description__ = "Ban/akill/shun user by copying their nickname and pressing a hotkey."
import os
import hexchat
if os.name =="posix":
	import pyperclip
elif os.name == "nt":
	import ctypes	
else:
	raise Exception("Unknown/unsupported OS")
import re
import urllib2
import json
json_api_website = 'http://freegeoip.net/json/'

edited = False

#should move these to a config file on next release
shun_time ='5m'
shun_reason ='Pushim'
akill_time = '+2d' #2 days
akill_reason ='Proxy/Ofendime/Flood/Abuse'

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

## Windows get clipboard function
def getclip():
	CF_TEXT = 1
	kernel32 = ctypes.windll.kernel32
	user32 = ctypes.windll.user32
	ret = None
	user32.OpenClipboard(0)
	if user32.IsClipboardFormatAvailable(CF_TEXT):
	    data = user32.GetClipboardData(CF_TEXT)
	    data_locked = kernel32.GlobalLock(data)
	    text = ctypes.c_char_p(data_locked)
	    ret = text.value
	    kernel32.GlobalUnlock(data_locked)
	else:
	    print('no text in clipboard')
	user32.CloseClipboard()
	return ret
#################################





#main function to hook a button to a command, its parameter is fetched from the clipboard
def xline_cb(word,word_eol, _):
	global numerics
	xline_nick = None
	xline_timer_handle = None
	xline_hooks = []

	#get the nickname from the clipboard
	if os.name =="posix":
		xline_nick = pyperclip.paste()

	if os.name =="nt":
		xline_nick = getclip()

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
				hexchat.command("os akill add %s *@%s %s" % (akill_time,str(connecting_ip),akill_reason))			

		return hexchat.EAT_ALL	

	def xline_timeout_cb(_):
		xline_unhook()

	xline_hooks = [hexchat.hook_server(numeric, xline_notice_cb) for numeric in numerics]	
	xline_timer_handle = hexchat.hook_timer(1000, xline_timeout_cb)

	return hexchat.EAT_ALL


def xshun_cb(word,word_eol, _):
	global numerics
	xshun_timer_handle = None
	xshun_nick = None
	xshun_hooks = []

	#get the nickname from the clipboard
	if os.name =="posix":
		xshun_nick = pyperclip.paste()

	if os.name =="nt":
		xshun_nick = getclip()
		

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
############################################################################3
def on_join(word, word_eol, event,attr):
	global edited
	if edited or attr.time or not len(word) > 1:
		return
	nick = word[0]
	chan = word[1]
	ident = str(re.findall(r"(.*)\@",word[2]))
	ident = ident[2:-2]		
	userip_hook = None
	timer_handle = None
	hexchat.command("USERIP "+ nick)

	def unhook():
		hexchat.unhook(userip_hook)
		hexchat.unhook(timer_handle)

	def userip_cp(word, word_eol, _):
		global edited
		unhook()	

		nick_cb = str(re.findall(r"\:(.*)\=", str(word[3])))
		nick_cb = nick_cb[2:-2]
		if(word[1] == '340' and nick == nick_cb):

			ip = str(word[3])
			ip = str(re.findall(r"\@(.*)",ip))
			ip = ip[2:-2]
			request_url = json_api_website + ip

			try:
				response = urllib2.urlopen(request_url)
				data = json.load(response)
				chan_context = hexchat.find_context(channel=chan)
				country_name = str(data['country_name'])
				country_code = str(data['country_code'])
				location = ident +" "+ ip +" "+ country_name +"/"+country_code
				edited = True
				chan_context.emit_print("Join", nick_cb, chan, location)
				edited = False
				return hexchat.EAT_ALL
			except:
				pass		
				

	def onjoin_timeout_cb(_):
		unhook()

	userip_hook = hexchat.hook_server("340", userip_cp)
	timer_handle = hexchat.hook_timer(1000, onjoin_timeout_cb)
	return hexchat.EAT_ALL	

hexchat.hook_print_attrs("Join", on_join,"Join",priority=hexchat.PRI_HIGH)
hexchat.hook_command("xshun", xshun_cb, help="/xshun <nick> , Shuns user from the server.")
hexchat.hook_command("xline", xline_cb, help="/xline <nick> , Akills user from the server.")
print(__module_version__ + " version " + __module_name__ + " loaded.")
