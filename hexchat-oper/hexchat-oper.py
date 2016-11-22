__module_name__ = "hexchat-oper"
__module_version__ = "2.1"
__module_description__ = "Python 3 Windows"
import os
import sys
# path = str((os.getcwd()))
# sys.path.insert(0,path)
# print(path)
import hexchat
import threading
sys.path.append(os.path.join(os.path.dirname("__file__"), "extras"))
path = os.path.join(os.path.dirname("__file__"), "extras")
geoip_dat = os.path.join(path,"GeoIP" + "." + 'dat')
import pygeoip

if(sys.version_info > (3, 0)):
    import urllib.request
    from urllib.error import HTTPError

if os.name == "nt":
    import ctypes   
else:
    raise Exception("Unknown/unsupported OS")
import json
import re

# Configs below

email = 'irrgit@gmail.com'
flags = 'm'
script_path = os.getcwd()
exempt_file_path = script_path + '/excludeip.txt'
shun_time ='5m'
shun_reason ='Pushim'
akill_time = '+2d' #2 days
akill_reason ='Proxy/Ofendime/Flood/Abuse'
sqline_reason = 'Nick/Banal'
check_proxy = False # set to check each IP if its a proxy, Warning this could get slow


edited = False

#Channel Ban text event 
edited_ban = False
#Channel UnBan text event 
edited_unban = False
#used to recompile a hostmask to a regex that matches said mask
wildcards = {'?':r'.', '*': r'.*'}

mydata = {}

IRCCloud = [
'192.184.9.108' ,
'192.184.9.110' ,
'192.184.9.112' ,
'192.184.10.118',
'192.184.10.9'  ,
'170.178.187.131' 
]
numerics = ["311","379","378","319","312","313",
            "310","317","318","307","335","320"]

exempt_list = []
gi = pygeoip.GeoIP(geoip_dat)
# End configs

def load_exempt_ips():
    global exempt_list
    #empty the list

    exempt_list[:] = []
    try:
        with open(exempt_file_path) as f:
            for line in f:
                if '.' in line:
                    ip = line.rstrip()
                    ip = ip.replace("*","")
                    exempt_list.append(ip)
    except:
        print("Error loading file.")
load_exempt_ips()

def getclip():
    CF_TEXT = 1
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    ret = None
    user32.OpenClipboard(0)
    if user32.IsClipboardFormatAvailable(CF_TEXT):
        data = user32.GetClipboardData(CF_TEXT)
        data_locked = kernel32.GlobalLock(data)
        text = ctypes.c_char_p(data_locked)
        ret = text.value
        kernel32.GlobalUnlock(data_locked)
    else:
        print('no text in clipboard')
    user32.CloseClipboard()
    return ret



def get_data_py3(nick,ip):
    
    try:
        country_code = gi.country_code_by_addr(ip)  
        country_name = gi.country_name_by_addr(ip)
        
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
        return

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
        return

    elif 'Client exiting' in notice:
        nickname = re.findall(r": ([^!(]+)",notice)[0]
        nickname = nickname.replace(" ","")
        if nickname in mydata:
            mydata.pop(nickname, None)
        else:
            print("Not in the dictionary")
        return

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

        return
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
        return
    else:
        return 
        

 
def on_chan_join(word,word_eol,event, attr):
    global edited
    if edited or attr.time or not len(word) > 1:
        return
    nick = word[0]
    chan = word[1]
    chan_context = hexchat.find_context(channel=chan)
    try:
        ident = re.findall(r"(.*)\@",word[2])[0]
    except:
        return


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
            try:
                nick_cb = re.findall(r":([^*=]+)", str(word[3]))[0]
            except:
                return

            if(word[1] == '340' and nick == nick_cb):
                unhook()
                try:
                    ip = re.findall(r"\@(.*)",str(word[3]))[0]
                except:
                    return

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
             
                    response = None
                    data = None
                    country_name = None
                    country_code = None
                    if (sys.version_info >(3, 0)):
                        try:
                            country_code = gi.country_code_by_addr(ip)  
                            country_name = gi.country_name_by_addr(ip)
                            user_info = [ip,country_name,country_code,'Exempt']
                            mydata[nick] = user_info
                        except:
                            print("error py3 getting response") 
                    else:
                        try:
                            country_code = gi.country_code_by_addr(ip)  
                            country_name = gi.country_name_by_addr(ip)
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

                    response = None
                    data = None
                    country_name = None
                    country_code = None
                    proxy =''
                    if(sys.version_info > (3, 0)):
                        try:
                            country_code = gi.country_code_by_addr(ip)  
                            country_name = gi.country_name_by_addr(ip)
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
                            print(err.code)
                            print("Error py3 getting resonse for geoip")                 
                        
                    location =""
                    try:                        
                        location = " "+ident +" "+ ip +" "+ country_name +"/"+country_code +" "+ "\00320"+proxy
                    except:
                        print("Error in trying to setup location")
                        return
                    edited = True
                    chan_context.emit_print("Join", nick_cb, chan, location)
                    edited = False
                    return hexchat.EAT_ALL

            else:
                return

        def onjoin_timeout_cb(_):
            unhook()

        userip_hook = hexchat.hook_server("340", userip_callback)
        timer_handle = hexchat.hook_timer(1000, onjoin_timeout_cb)
        return hexchat.EAT_ALL




def match_mask(mask, searchmask ):
    if searchmask is None:
        searchmask = ''
    for match, repl in wildcards.items():
        mask = mask.replace(match,repl)
    return bool(re.match(mask,searchmask,re.IGNORECASE))
        


def get_user_list(context):
    list = context.get_list("users")
    return list

def on_chan_ban(word,word_eol,event,attr):

    mask_list = []
    nicks_matching = []
    chan_context = hexchat.get_context()
    emit_nicks = ""

    global edited_ban
    if edited_ban or attr.time or not len(word) > 1:
        return

    bnick = word[0]
    banmask = word[1]

    # ban of type nick below, nick!*@* , no need to edit check if last 4 chars match
    if banmask[-4:] == '!*@*':
        return

    user_list = get_user_list(chan_context)
    
    for user in user_list:
        fullhost =  '*!*' + user.host
        toappend = (user.nick, fullhost)
        mask_list.append(toappend)

    if len(mask_list) > 0:
        for user_nick , user_mask in mask_list:
            if match_mask(banmask,user_mask) == True:
                nicks_matching.append(user_nick)
    if len(nicks_matching) > 0:
        for nick in nicks_matching:
            emit_nicks += ("\00320"+str(nick) +" ")
    mask_addendum = "\00317 | " + banmask
    emit_nicks += mask_addendum
    
    edited_ban = True
    chan_context.emit_print("Channel Ban",bnick,emit_nicks)
    edited_ban = False

    return hexchat.EAT_ALL

def on_chan_unban(word,word_eol,event,attr):
    mask_list = []
    nicks_matching = []
    chan_context = hexchat.get_context()
    emit_nicks = ""

    global edited_unban
    if edited_unban or attr.time or not len(word) > 1:
        return

    bnick = word[0]
    unban_mask = word[1]

    if unban_mask[-4:] == '!*@*':
        return

    user_list = get_user_list(chan_context)

    for user in user_list:
        fullhost = '*!*' + user.host
        toappend = (user.nick,fullhost)
        mask_list.append(toappend)


    if len(mask_list) > 0:
        for user_nick, user_mask in mask_list:
            if match_mask(unban_mask,user_mask) == True:
                nicks_matching.append(user_nick)
    if len(nicks_matching) > 0:
        for nick in nicks_matching:
            emit_nicks += ("\00320" + str(nick) + " ")

    mask_addendum = "\00317 | " + unban_mask
    emit_nicks += mask_addendum

    edited_unban = True
    chan_context.emit_print("Channel UnBan",bnick,emit_nicks)
    edited_unban = False

    return hexchat.EAT_ALL

def xsqline(word,word_eol, _):
    xsqline_nick = None
    if os.name =="nt":
        xsqline_nick = getclip()

    xsqline_nick = str(xsqline_nick)

    #unicode fix
    if(sys.version_info > (3, 0)):
        xsqline_nick = xsqline_nick[2:-1]
    #issue an sqline on that nickname
    command = "os sqline add +30d *%s* %s" % (xsqline_nick, sqline_reason)
    hexchat.command(command)

def xshun_cb(word,word_eol, _):
    global numerics
    xshun_timer_handle = None
    xshun_nick = None
    xshun_hooks = []

    if os.name =="nt":
        xshun_nick = getclip()        
    xshun_nick = str(xshun_nick)
    if(sys.version_info > (3, 0)):
        xshun_nick = xshun_nick[2:-1]
    #issue whois on nickname
    hexchat.command("whois " + str(xshun_nick))

    #function to be called later to unhook all numeric hooks
    def xshun_unhook():
        for hook in xshun_hooks:
            hexchat.unhook(hook)
        hexchat.unhook(xshun_timer_handle)      

    def xshun_notice_cb(word, word_eol, _):
        if word[1] == '378':
            connecting_ip =  str(word[8])
            if(connecting_ip  not in str (IRCCloud)):
                hexchat.command("shun +*@%s %s %s" % (str(connecting_ip),shun_time,shun_reason))

        return hexchat.EAT_ALL  

    def xshun_timeout_cb(_):
        xshun_unhook()

    xshun_hooks = [hexchat.hook_server(numeric, xshun_notice_cb) for numeric in numerics]   
    xshun_timer_handle = hexchat.hook_timer(1000, xshun_timeout_cb)

    return hexchat.EAT_ALL  

def xline_cb(word,word_eol, _):
    global numerics
    xline_nick = None
    xline_timer_handle = None
    xline_hooks = []

    if os.name =="nt":
        xline_nick = getclip()

    xline_nick = str(xline_nick)
    if(sys.version_info > (3, 0)):
        xline_nick = xline_nick[2:-1]

    #issue whois on nickname
    hexchat.command("whois " + str(xline_nick))

    #function to be called later to unhook all numeric hooks
    def xline_unhook():
        for hook in xline_hooks:
            hexchat.unhook(hook)
        hexchat.unhook(xline_timer_handle)      

    def xline_notice_cb(word, word_eol, _):
        if word[1] == '378':
            connecting_ip =  str(word[8])
            if(connecting_ip  not in str (IRCCloud)):
                hexchat.command("os akill add %s *@%s %s" % (akill_time,str(connecting_ip),akill_reason))           

        return hexchat.EAT_ALL  

    def xline_timeout_cb(_):
        xline_unhook()

    xline_hooks = [hexchat.hook_server(numeric, xline_notice_cb) for numeric in numerics]   
    xline_timer_handle = hexchat.hook_timer(1000, xline_timeout_cb)

    return hexchat.EAT_ALL
hexchat.hook_command("xline", xline_cb, help="/xline <nick> , Akills user from the server.")
hexchat.hook_command("xshun", xshun_cb, help="/xshun <nick> , Shuns user from the server.")
hexchat.hook_command("xsqline", xsqline, help="/xsqline <nick> , Places an sqline on the nick")
hexchat.hook_print("Server Notice", on_server_join)
hexchat.hook_print_attrs("Join", on_chan_join, "Join",priority=hexchat.PRI_NORM)
hexchat.hook_print_attrs("Channel Ban", on_chan_ban, "Channel Ban",priority=hexchat.PRI_NORM)
hexchat.hook_print_attrs("Channel UnBan", on_chan_unban, "Channel UnBan",priority=hexchat.PRI_NORM)
print(__module_version__ + " version " + __module_name__ + " loaded.")
            



'''
TODO

Add keyboard shortcuts inside this plugin if possible.
Move GeoIP checking to a local DB instead of using a web API.
Add country to whois info

'''