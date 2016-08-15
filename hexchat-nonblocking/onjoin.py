__module_name__ = "oper-onjoin"
__module_version__ = "1.1"
__module_description__ = "Override join messages in a channel"

import hexchat
import threading
import sys
import os
if(sys.version_info > (3, 0)):
    import urllib.request
    from urllib.error import HTTPError
else:
    import urllib2
import json
import re

# Configs below
freegeoip_json_api = 'http://freegeoip.net/json/'
email = 'irrgit@gmail.com'
flags = 'm'
script_path = os.getcwd()
exempt_file_path = script_path + r'C:\Users\test\Desktop\ipfile.txt'


edited = False
mydata = {}

IRCCloud = [
'192.184.9.108' ,
'192.184.9.110' ,
'192.184.9.112' ,
'192.184.10.118',
'192.184.10.9'  ,
'170.178.187.131' 
]
# End configs
exempt_list = []
def load_exempt_ips():
    global exempt_list
    #empty the list
    exempt_list[:] = []
    with open(exempt_file_path) as f:
        for line in f:
            if '.' in line:
                ip = line.rstrip()
                ip = ip.replace("*","")
                exempt_list.append(ip)
    
load_exempt_ips()
def get_data_py3(nick,ip):
    request_url = freegeoip_json_api + ip
    try:
        response = urllib.request.urlopen(request_url).read().decode('utf-8')
        data = json.loads(response)   
        country_name = data['country_name']
        country_code = data['country_code']
        if(any(exempt_ip in ip for exempt_ip in exempt_list) or country_name == 'Albania'):
            user_info = [ip,country_name,country_code,'Exempt']
            mydata[nick] = user_info
        else:
            try:
                proxy = ''
                ipintel_api_link = "http://check.getipintel.net/check.php?ip=%s&contact=%s&flags=%s" % (ip,email,flags)
                request_obj = urllib.request.Request(ipintel_api_link,data=None, headers={'User-Agent': 'Mozilla'})
                ipintel_response = urllib.request.urlopen(request_obj).read().decode('utf-8')
                proxy_data = str(ipintel_response)
                if(str(proxy_data) =='1'):
                    proxy = 'Proxy'
                user_info = [ip,country_name,country_code,proxy]
                mydata[nick] = user_info
            except HTTPError as err:
                print("Something went wrong when trying to get Proxy data, PY3")
    except:
        print("Print something went wrong when trying to get IP data , PY3")


def get_data_py2(nick,ip):
    request_url = freegeoip_json_api + ip

    try:
        response = urllib2.urlopen(request_url).read().decode('utf-8')
        data = json.loads(response)
        country_name = data['country_name']
        country_code = data['country_code']
        if(any(exempt_ip in ip for exempt_ip in exempt_list) or country_name == 'Albania'):
            user_info = [ip,country_name,country_code,'Exempt']
            user_info = user_info = [s.encode('utf-8') for s in user_info]
            mydata[nick] = user_info

        else:
            try:
                proxy =''
                ipintel_api_link = "http://check.getipintel.net/check.php?ip=%s&contact=%s&flags=%s" % (ip,email,flags)
                request_obj = urllib2.Request(ipintel_api_link,data=None, headers={'User-Agent': 'Mozilla'})
                ipintel_response = urllib2.urlopen(request_obj).read().decode('utf-8')
                proxy_data = str(ipintel_response)
                if (proxy_data == '1'):
                    proxy = 'Proxy'
                else:
                    proxy = ''
                user_info = [ip,country_name,country_code,proxy]
                user_info = [s.encode('utf-8') for s in user_info]
                mydata[nick] = user_info
            except urllib2.HTTPError as err:
                print("Something went wrong when trying to get proxy data, PY2")
    except:
        print("Domething went wrong when trying to get IP data , PY2")  





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

    elif 'Client exiting' in notice:
        nickname = re.findall(r": ([^!]+)",notice)[0]
        if nickname in mydata:
            del mydata[nickname]

    elif 'forced to change his/her nickname' in notice:
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

    elif 'has changed his/her nickname' in notice:
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
    else:
        return 
        

 
def on_chan_join(word,word_eol,event, attr):
    global edited
    if edited or attr.time or not len(word) > 1:
        return
    nick = word[0]
    chan = word[1]
    chan_context = hexchat.find_context(channel=chan)
    ident = re.findall(r"(.*)\@",word[2])[0]


    if nick in mydata:
        chan_context = hexchat.find_context(channel=chan)
        user_info = mydata[nick]
        ip_from_data = user_info[0]
        country_name = user_info[1]
        country_code = user_info[2]
        additional_info = ''
        if len(user_info) == 4:
            if 'Exempt' in user_info[3]:
                additional_info = user_info[3]
            if 'Proxy' in user_info[3]:
                additional_info = user_info[3]
        location = " "+ ident +" "+ ip_from_data +" " + country_name +"/"+ country_code +" "+ additional_info
        edited = True
        chan_context.emit_print("Join",nick,chan,location)
        edited = False
        return hexchat.EAT_ALL
    else:
        hexchat.command("USERIP "+ nick)
        def unhook():
            hexchat.unhook(userip_hook)
            hexchat.unhook(timer_handle)

        def userip_callback(word,word_eol,_):
            global edited
            nick_cb = re.findall(r":([^*=]+)", str(word[3]))[0]

            if(word[1] == '340' and nick == nick_cb):
                unhook()
                ip = re.findall(r"\@(.*)",str(word[3]))[0]

                if(ip == '<unknown>'):
                    user_info = ['Bot','Earth','']
                    mydata[nick] = user_info
                    edited = True
                    chan_context.emit_print("Join",nick_cb,chan,mydata[nick][0])
                    edited = False
                    return hexchat.EAT_ALL

                elif(ip in IRCCloud):
                    user_info = [ip,'IRCCloud','']
                    mydata[nick] = user_info
                    location = " " + ident + " " + mydata[nick][1]
                    edited = True
                    chan_context.emit_print("Join",nick_cb,chan,location)
                    edited = False 
                    return hexchat.EAT_ALL

                elif (any(exempt_ip in ip for exempt_ip in exempt_list)):
                    request_url = freegeoip_json_api + ip
                    response = None
                    data = None
                    country_name = None
                    country_code = None
                    if (sys.version_info >(3, 0)):
                        try:
                            response = urllib.request.urlopen(request_url).read().decode('utf-8')
                            data = json.loads(response)
                            country_name = data['country_name']
                            country_code = data['country_code']
                            user_info = [ip,country_name,country_code,'Exempt']
                            mydata[nick] = user_info
                        except:
                            print("error py3 getting response") 
                    else:
                        try:
                            response = urllib2.urlopen(request_url).read().decode('utf-8')
                            data = json.loads(response)
                            country_name = data['country_name']
                            country_code = data['country_code']
                            user_info = [ip,country_name,country_code,'Exempt']
                            user_info = user_info = [s.encode('utf-8') for s in user_info]
                            mydata[nick] = user_info
                        except:
                            print("Error py2 getting response for exempt")
                    location = " "+ident +" "+ ip +" "+ country_name +"/"+ country_code + " "+ "\00320Exempt"
                    edited = True
                    chan_context.emit_print("Join",nick_cb,chan,location)
                    edited = False
                    return hexchat.EAT_ALL

                else:#below needs to be done almost the same as above but add getipintel
                    request_url = freegeoip_json_api + ip
                    response = None
                    data = None
                    country_name = None
                    country_code = None
                    proxy =''
                    if(sys.version_info > (3, 0)):
                        try:
                            response = urllib.request.urlopen(request_url).read().decode('utf-8')
                            data = json.loads(response)
                            country_name = data['country_name']
                            country_code = data['country_code']
                            try:
                                proxy = ''
                                ipintel_api_link = "http://check.getipintel.net/check.php?ip=%s&contact=%s&flags=%s" % (ip,email,flags)
                                request_obj = urllib.request.Request(ipintel_api_link,data=None, headers={'User-Agent': 'Mozilla'})
                                ipintel_response = urllib.request.urlopen(request_obj).read().decode('utf-8')
                                proxy_data = str(ipintel_response)
                                if(str(proxy_data) =='1'):
                                    proxy = 'Proxy'
                                user_info = [ip,country_name,country_code,proxy]
                                mydata[nick] = user_info  

                            except HTTPError as err:

                                print("Error py3 getting response for proxy")

                            #here query for proxy response and update the  variable
                        except:
                            print("Error py3 getting resonse for geoip")


                    else:
                        try:
                            response = urllib2.urlopen(request_url).read().decode('utf-8')
                            data = json.loads(response)
                            country_name = data['country_name']
                            country_code = data['country_code']
                            try:  
                                request_obj = urllib2.Request(ipintel_api_link,data=None, headers={'User-Agent': 'Mozilla'})
                                ipintel_response = urllib2.urlopen(request_obj).read().decode('utf-8')
                                proxy_data = str(ipintel_response)
                                if (proxy_data == '1'):
                                    proxy = 'Proxy'
                                else:
                                    proxy = ''
                                user_info = [ip,country_name,country_code,proxy]
                                user_info = [s.encode('utf-8') for s in user_info]
                                mydata[nick] = user_info

                            except urllib2.HTTPError as err:
                                print("Error py2 getting response for proxy")
                            #here query for proxy response and update the variable
                        except:
                            print("Error py2 getting response for geoip")

                    location = " "+ident +" "+ ip +" "+ country_name +"/"+country_code +" "+ "\00320"+proxy
                    edited = True
                    chan_context.emit_print("Join", nick_cb, chan, location)
                    edited = False
                    return hexchat.EAT_ALL

            else:
                return hexchat.EAT_NONE

        def onjoin_timeout_cb(_):
            unhook()

        userip_hook = hexchat.hook_server("340", userip_callback)
        timer_handle = hexchat.hook_timer(1000, onjoin_timeout_cb)
        return hexchat.EAT_ALL





def on_chan_ban(word,word_eol,event,attr):
    #override bans here
    print ("On chan ban funciton")





hexchat.hook_print("Server Notice", on_server_join)
hexchat.hook_print_attrs("Join", on_chan_join, "Join",priority=hexchat.PRI_NORM)
print("Loaded-========================-")
            



