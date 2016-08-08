__module_name__ = "hexchat-onjoin"
__module_version__ = "1.1"
__module_description__ = "Override Join messages"

import hexchat
import re
import urllib2
import json
json_api_website = 'http://freegeoip.net/json/'

edited = False

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
				location = ident +" "+ ip +" "+ "\00320"+country_name +"/"+country_code
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

print(__module_name__ +" version " + __module_version__ +" loaded.")