# hexchat-oper
Oper helper plugin for hexchat with the following features:  
Adds a command to place a shun by nick : `/xshun `  
Adds a command to place an akill by nick : `/xline `  
Adds a command to place an sqline by nick : `/xsqline `  
These commands do not take a paramater after them but rather the paramater is taken from the clipboard. So selecting the nick and then issuing the command by hand. It is recommended to add shortcuts for each of these commands.  

Uses freegeoip API to display the location of the users that join a channel.
Then if you want to be able to execute these commands with keyboard shortcuts:  

	On Linux: sudo pip install pyperclip  
        
	On Windows no additional modules are needed.    

To enable keyboard shortcuts add the commands like shown below. 
The commands are called /xline and /xshun. <b>xline</b> places an akill while <b>xshun</b> places a shun. 

Also overrides join messages and appends the users IP.

![alt tag](http://i.imgur.com/zBIQbhK.png)
