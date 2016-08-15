__module_name__ = "oper-oper-filter"
__module_version__ = "1.1"
__module_description__ = "Filter server notices to separate tabs."

import hexchat
import os
import re
osname = os.name
import thread



TEXT =  {
	'blue': '\00318',
	'green': '\00319',
	'red': '\00320',
	'brown': '\00321',
	'purple': '\00322',
	'orange': '\00323',
	'lightgreen': '\00325',
	'gray': '\00330',
	'bold':'\002',
	'underline':'\037'
}

#these will be the network tabs to print to.
TABS = [
r'{CONNECTIONS}', 
r'{OVERRIDES}' ,
r'{SPAMFILTER}',
r'{NICKCHANGES}'
]

#Below function opens the tabs needed/wanted, more can be added to the list above
def open_tabs():
	server_context = hexchat.get_info("server")
 	tab_options = hexchat.get_prefs('tab_new_to_front')
	hexchat.command("set -quiet tab_new_to_front 0")
	
	for tab in TABS:
		hexchat.command("NEWSERVER -noconnect %s" % tab)
#run above function to open all TABS we need as server tabs on plugin load		
open_tabs()
network_contexts = []
#the list below should contain the context of all the tabs we opened above
network_contexts =[hexchat.find_context(tab) for tab in TABS]

#pad nickname with spaces so it looks nice while printing for 'NICKLEN=30'
def pad_nick(nick):
	nick = (nick + " " *30)[:30]
	return nick



def parse_notice(notice):

	if 'Client connecting' in notice:
		#these below are for connections only
		server = TEXT['underline'] + TEXT['lightgreen'] + str(re.findall(r"at (\ ?.*)\:",notice)).strip("[]'")
		nickname = TEXT['bold']+TEXT['blue']+ str(re.findall(r"\: (.*)\ \(",notice)).strip("[]'")
		ip = TEXT['orange'] + str(re.findall(r"\@(.*)\)",notice)).strip("[]'")
		msg = pad_nick(nickname) +TEXT['gray']+" from "+ ip +" at "+ server


		connected = TEXT['green'] + 'Connected'
		conn_tab = hexchat.find_context(r'{CONNECTIONS}')
		conn_tab.emit_print("Channel Message", connected, msg)



# def server_notice(word, word_eol, userdata):
# 	for network in network_contexts:
# 		network.emit_print("Channel Message", "RandomNick", "Random Chan Message")

def on_server_notice(word, word_eol, userdata):
	notice = str(word[0])
	if 'Client connecting' in notice:
		thread.start_new_thread(parse_notice,(notice,))


hexchat.hook_print("Server Notice", on_server_notice)
print("Loaded-========================-")