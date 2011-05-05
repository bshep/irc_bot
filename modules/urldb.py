import sqlite3
import re
import time
import datetime

urlRegEx = re.compile(r"https?://([^ ]+)")

sendMessageToChannel = None # This will be set to a function by main.py

def processCommand(command, line, line_info):
    if command == 'list':
        processComandList(line_info)
    else:
        sendMessageToChannel(line_info[1], line_info[0], 'Unknown command: %s' % command)
        
        
def processComandList(line_info):
    rows = runQuery('SELECT url, spoken_where, spoken_by, on_date, count FROM urls')
    
    sendMessageToChannel(line_info[0], line_info[0], 'URL List(Total = %i):' % len(rows))
    for row in rows:
        timestamp = datetime.datetime.isoformat(datetime.datetime.fromtimestamp(float(row[3])))
        sendMessageToChannel(line_info[0], line_info[0], 'url: %s spoken_by: %s channel: %s time: %s count: %s' %
            ( row[0], row[2], row[1], timestamp, row[4] )
            )
    pass
    
    
def parseMessage(line, line_info):
    for url in urlRegEx.finditer(line_info[2]):
        username = line_info[0]
        now = time.time()
        channel = line_info[1]
        
        checkURL(url.group(0), channel, username, now)

def checkURL(url, spoken_where, spoken_by, on_date):
    row = runQueryGetOne('SELECT url, spoken_where, spoken_by, on_date, count FROM urls WHERE spoken_where = ? AND url = ?', [spoken_where, url] )
    
    
    if row:
        timestamp = datetime.datetime.isoformat(datetime.datetime.fromtimestamp(float(row[3])))
        if row[4] == 1:
            sendMessageToChannel(spoken_where, spoken_by, '%s already shared %s on %s' % (row[2], url, timestamp))
        else:
            # pass
            sendMessageToChannel(spoken_where, spoken_by, '%s already shared %s on %s and has been repeated %i times' % (row[2], url, timestamp, row[4]+1))
        
        runQuery('UPDATE urls SET count=count+1 WHERE spoken_where = ? AND url = ?', [spoken_where, url])
    else:
        runQuery('INSERT INTO urls (url, spoken_where, spoken_by, on_date) VALUES (?, ?, ?, ?)', [url, spoken_where, spoken_by, on_date])

def runQueryGetOne(query, args = []):
    rows = runQuery(query, args)
    
    if len(rows) >= 1:
        ret = rows[0]
    else:
        ret = None
    
    return ret


def runQuery(query, args = []):
    conn = sqlite3.connect('dbs/urldb.db')
    cursor = conn.cursor()
    
    cursor.execute(query, args)
    
    rows = cursor.fetchall()
    
    conn.commit()
    conn.close()
    
    return rows
    
def initModule():
    runQuery('CREATE TABLE IF NOT EXISTS urls (url text, spoken_where text, spoken_by text, on_date text, count int)',[])

initModule()

if __name__ == '__main__':
    parseMessage('bshep http://cnn.com')