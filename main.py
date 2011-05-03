import sys
import socket

reload(sys)
sys.setdefaultencoding("utf-8")

HOST='irc.freenode.net' #The server we want to connect to
PORT=6667 #The connection port which is usually 6667
NICK='MariaBot' #The bot's nickname
IDENT='Maria'
REALNAME='what u talkin about'
channel_list='#elweb' #The default channel for the bot

MODULES_LOAD='urldb'

modules = {}

irc_socket = None

def connectAndProcess():
    global irc_socket
    
    irc_buffer = ""
    irc_socket=socket.socket( ) #Create the socket
    irc_socket.connect((HOST, PORT)) #Connect to server
    irc_socket.send('NICK '+NICK+'\r\n') #Send the nick to server
    irc_socket.send('USER '+IDENT+' '+HOST+' bla :'+REALNAME+'\r\n') #Identify to server

    while 1:
        irc_buffer=irc_buffer+irc_socket.recv(1024) #recieve server messages
        
        irc_lines = irc_buffer.split('\n')
        irc_buffer = irc_lines.pop()
        
        for line in irc_lines:
            processLine(line)

def processLine(line):
    print line #server message is output
    
    if line.find('End of /MOTD command.')!=-1: 
        for channel in channel_list.split():
            joinChannel(channel)
        initModules()
        
    # if line.find('NickServ!NickServ@services. NOTICE')!=-1:
    #     print 'Identifying...'
        # irc_socket.send('PRIVMSG NickServ :identify 12345\r\n')
    
    if line.find('PRIVMSG')!=-1: #Call a parsing function
        parseMessage(line)
        
        for module in modules:
            print 'Sending to module: %s' % module
            try:
                modules[module].parseMessage(line)
            except Exception, e:
                print 'Error in module: %s' % module
                print e
                
    line=line.rstrip() #remove trailing 'rn'
    line=line.split()
    if(line[0]=='PING'): #If server pings then pong
        print 'PONG'
        irc_socket.send('PONG '+line[1]+'\r\n')

def joinChannel(channel):
    irc_socket.send('JOIN '+channel+'\r\n') #Join a channel
    
def parseMessage(line):
    """docstring for fname"""
    print 'Got a line i should parse...'
    line_items=line.split(' ', 3)
    
    line_txt = line_items[3][1:].rstrip()
    
    print line_txt
    
    if line_txt == '@reload':
        for module in modules:
            print 'Reloading module: %s' % module
            reload(modules[module])

        initModules()
            
    elif line_txt == '@quit 12345':
        sys.exit(0)    

def loadModule(module_name):
    global modules
    
    print 'Loading: %s' % module_name
    modules[module_name] = __import__('modules.%s' % module_name, None, None, ['*'])

def initModules():
    for module in modules:
        print 'Initializing module: %s' % module
        modules[module].socket = irc_socket
        modules[module].nickname = NICK

def loadDefaultModules():
    global modules
    
    for module in MODULES_LOAD.split():
        loadModule(module)
        
loadDefaultModules()
connectAndProcess()