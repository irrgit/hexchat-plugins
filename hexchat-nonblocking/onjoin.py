__module_name__ = "oper-onjoin"
__module_version__ = "1.1"
__module_description__ = "Override join messages in a channel"

import hexchat
import threading
import sys
if(sys.version_info > (3, 0)):
    import urllib.request
    from urllib.error import HTTPError
else:
    import urllib2
import json
import re

# Configs below
freegeoip_json_api = 'http://freegeoip.net/json/'
ipintel_api_link = 'http://check.getipintel.net/check.php?ip='
ipintel_email

edited = False
mydata = {}

# End configs

def get_data_py3(nick,ip):
    request_url = json_api_website + ip
    print("in py3 thread")
    try:
        response = urllib.request.urlopen(request_url).read().decode('utf-8')
        data = json.loads(response)   
        country_name = data['country_name']
        country_code = data['country_code']
        user_info = [ip,country_name,country_code]
        mydata[nick] = user_info 
    except:
        print("Print something went wrong when trying to get IP data , PY3")


def get_data_py2(nick,ip):
    request_url = json_api_website + ip
    try:
        response = urllib2.urlopen(request_url).read().decode('utf-8')
        data = json.loads(response)
        country_name = data['country_name']
        country_code = data['country_code']
        user_info = [ip,country_name,country_code]
        user_info = [s.encode('utf-8') for s in user_info]
        mydata[nick] = user_info 
    except:
        ("Print something went wrong when trying to get IP data , PY2")  





def on_server_join(word,word_eol,userdata):
    global mydata
    notice = word[0]
    if 'Client connecting' in notice:
        nickname = re.findall(r"\: (.*)\ \(",notice)[0]
        ip = re.findall(r"\@(.*)\)",notice)[0]
        if 'irccloud.com' in ip:
            user_info = [ip,'IRCCloud','US']
            mydata[nickname] = user_info
        elif 'mibbit.com' in ip:
            user_info = [ip,'Mibbit','US']
            mydata[nickname] = user_info
        else:
            if(sys.version_info > (3, 0)):
                send_to_thread = threading.Thread(target=get_data_py3,args=(nickname,ip,))
                send_to_thread.start()
            else:
                send_to_thread = threading.Thread(target=get_data_py2, args=(nickname,ip,))
                send_to_thread.start()

    if 'Client exiting' in notice:
        nickname = re.findall(r": ([^!]+)",notice)[0]
        if nickname in mydata:
            del mydata[nickname]

    if 'forced to change his/her nickname' in notice:
        oldnick = re.findall(r"-- ([^()]+) ",notice)[0]
        newnick = re.findall(r"nickname to ([^()]+)",notice)[0]
        ip = re.findall(r"@([^)]+)",notice)[0]
        if oldnick in mydata:
            v = mydata.pop(oldnick)
            mydata[newnick] = v
        else:
            if(sys.version_info > (3, 0)):
                send_to_thread = threading.Thread(target=get_data_py3,args=(newnick,ip,))
                send_to_thread.start()
            else:
                send_to_thread = threading.Thread(target=get_data_py2, args=(newnick,ip,))
                send_to_thread.start()

    if 'has changed his/her nickname' in notice:
        ip = re.findall(r"@([^)]+)",notice)[0]
        oldnick = re.findall(r"-- ([^()]+) ",notice)[0]
        newnick = re.findall(r"nickname to ([^()]+)",notice)[0]

        if oldnick in mydata:
            v = mydata.pop(oldnick)
            mydata[newnick] = v
        else:
            if(sys.version_info > (3, 0)):
                send_to_thread = threading.Thread(target=get_data_py3, args=(newnick,ip,))
                send_to_thread.start()
            else:
                send_to_thread = threading.Thread(target=get_data_py2, args=(newnick,ip,))
                send_to_thread.start()  
        

 
def on_chan_join(word,word_eol,event, attr):
    global edited
    if edited or attr.time or not len(word) > 1:
        return
    nick = word[0]
    chan = word[1]
    ident = re.findall(r"(.*)\@",word[2])[0]


    if nick in mydata:
        chan_context = hexchat.find_context(channel=chan)
        ip_from_data = mydata[nick][0]
        country_name = mydata[nick][1]
        country_code = mydata[nick][2]
        location = " "+ ident +" "+ ip_from_data +" " + country_name +"/"+ country_code 
        edited = True
        chan_context.emit_print("Join",nick,chan,location)
        edited = False
        return hexchat.EAT_ALL
    else:
        return
        # here hook to check again in 1 sec and if its not there then print normally
        # print("Not here yet")







hexchat.hook_print("Server Notice", on_server_join)
hexchat.hook_print_attrs("Join", on_chan_join, "Join",priority=hexchat.PRI_NORM)
print("Loaded-========================-")
            



