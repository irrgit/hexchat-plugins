import hexchat

__module_name__ = "oper-oper-filter"
__module_version__ = "1.1"
__module_description__ = "Filter server notices to separate tabs."


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
	print ("in parse_notice()")
	#to do here
	#multithreaded function that feteches a notice and displays it where its needed


def server_notice(word, word_eol, userdata):
	for network in network_contexts:
		network.emit_print("Channel Message", "RandomNick", "Random Chan Message")

hexchat.hook_command('testprint', server_notice)