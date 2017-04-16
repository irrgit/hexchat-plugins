__module_name__ = "hexchat-nonewline"
__module_version__ = "0.1"
__module_description__ = "Remove newlines"


## HOOK keypress, wait for enter, check for newlines, and then remove
import hexchat

def nonewline(word, word_eol, userdata):

	if not word[0] == '65293': # Enter
		return

	text = hexchat.get_info('inputbox').replace("\n"," ")
	hexchat.command('settext {}'.format(text))
	
hexchat.hook_print("Key Press",nonewline)

print(__module_name__ +" version "  + __module_version__ +  " loaded.")



