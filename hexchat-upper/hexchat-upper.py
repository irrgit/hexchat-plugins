__module_name__ = "hexchat-upper"
__module_version__ = "1.1"
__module_description__ = "Capitalize the last letter of every word to be annoying."

import hexchat

def upper(word, word_eol, userdata):
	line = word_eol[0]
	line = " ".join([x[:-1].lower()+x[len(x)-1].upper() for x in line.split()])
	hexchat.command(" ".join(["msg", hexchat.get_info("channel"), line]))
	return hexchat.EAT_ALL

hexchat.hook_command("",upper)

print(__module_name__ +" version "  + __module_version__ +  " loaded.")



