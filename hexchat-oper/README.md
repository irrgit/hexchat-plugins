# hexchat-oper
Oper helper plugin for hexchat with the following features:  
Adds a command to place a shun by nick : `/xshun nick`  
Adds a command to place an akill by nick : `/xline nick`  
Uses freegeoip API to display the location of the users that join a channel.
Then if you want to be able to execute these commands with keyboard shortcuts:  

	#####On Linux: sudo pip install pyperclip  
        
	#####On Windows no additional modules are needed.    

To enable keyboard shortcuts add the commands like shown below. 
The commands are called /xline and /xshun. <b>xline</b> places an akill while <b>xshun</b> places a shun. 

Also overrides join messages and appends the users IP.

![alt tag](http://i.imgur.com/fSf9zyJ.png)
