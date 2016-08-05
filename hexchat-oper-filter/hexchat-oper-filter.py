__module_name__ = "oper-oper-filter"
__module_version__ = "1.1"
__module_description__ = "Filter server notices to separate tabs."

import hexchat
import os
osname = os.name
import thread





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

#test print to all network tabs


def parse_notice(notice):
	
	blue ='\00323'
	gray = '\00331'
	connected = blue + 'Connected'
	conn_tab = hexchat.find_context(r'{CONNECTIONS}')
	conn_tab.emit_print("Channel Message", connected, str(notice))


# def server_notice(word, word_eol, userdata):
# 	for network in network_contexts:
# 		network.emit_print("Channel Message", "RandomNick", "Random Chan Message")

def on_server_notice(word, word_eol, userdata):
	notice = str(word[0])
	if 'Client connecting' in notice:
		thread.start_new_thread(parse_notice,(notice,))


hexchat.hook_print("Server Notice", on_server_notice)