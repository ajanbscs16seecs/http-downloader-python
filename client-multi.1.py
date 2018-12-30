# Socket client example in python

import socket
import sys
import re
import os
import io

from threading import Thread

CHUNK_SIZE = 4096
CRLF = b"\r\n\r\n"





'''
CLASSES
'''
class Headers:
    def __init__(self,headers):
        self.headers = headers

    def getContentLength(self):
        p = "Content-Length: (\d+)"
        m = re.search(p,self.headers)
        return int(m.group(1))
    def __str__(self):
        return str("HEADERS:\n"+self.headers)
class Response:
    data=b''
    response_code =""
    request_line = ""
    headers=""
    body=b''
    def __init__(self, data):
        self.data = data
        

    def parse(self):
        splitted = self.data.split(CRLF, 1)
        headers = splitted[0].decode()
        self.request_line = headers.split('\n')[0]
        self.response_code = self.request_line.split()[1]
        headers = headers.replace(self.request_line, '')
        self.headers = Headers(headers)
        self.body = self.data.replace(headers.encode(), b'').replace(self.request_line.encode(), b'').replace(CRLF,b'')
    def __str__(self):
        return str("RESPONSE:\n"+self.response_code+"\n"+str(self.headers)+("" if self.body==b'' else "\nBODY EXISTS: "+str(self.headers.getContentLength())))


class DownloadTask:

    host = ''
    uri = ''
    total = 0
    start=0
    end = 0
    def __init__(self, host,uri,total=0,start=0,end=0):
        self.host = host
        self.uri = uri
        self.total = total
        self.start = start
        self.end = end
    
'''
FUNCTIONS
'''


# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(now,total):
    barLength = 50 # Modify this to change the length of the progress bar
    status = ""
    progress = now/total
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2} bytes of {3} {4}".format( ">"*block + "-"*(barLength-block), progress*100,now,total, status)
    sys.stdout.write(text)
    sys.stdout.flush()



def receive_all(sock, chunk_size=CHUNK_SIZE ,temp=0, total =0):
    '''
    Gather all the data from a request.
    '''
    chunks = []    
    while True:
        chunk = sock.recv(int(chunk_size))
        if chunk:
            chunks.append(chunk)            
            temp+=len(chunk)
            if total != 0:
                update_progress(temp,total)

        else:
            break
    return b''.join(chunks)

def parseResponse(data):
    splitted = data.split(CRLF, 1)
    headers = splitted[0].decode()
    request_line = headers.split('\n')[0]
    response_code = request_line.split()[1]
    headers = headers.replace(request_line, '')


def get(host,path,now=0,till=0,total=0):
    # create socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Failed to create socket')
        sys.exit()
    try:
        remote_ip = socket.gethostbyname( host )
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting')
        sys.exit()
    # Connect to remote server
    s.connect((remote_ip , port))
    # Send data to remote server
    request = ("GET " if total!=0 else "HEAD ")+uri+" HTTP/1.0\r\nHost: "+ host+"\r\n\r\n"
    print(request)
    try:
        s.sendall(request.encode())
    except socket.error:
        print('Send failed')
        sys.exit()

    # Receive data
    data = receive_all(s,CHUNK_SIZE,0,99999  if total == 0 else total)
    

    return Response(data)


def getHeader(host,path):
    return get(host,path)


'''
THREADS
'''
class MyThread(Thread):
    downloadTask:DownloadTask 
    def __init__(self, downloadTask):
        ''' Constructor. '''
        Thread.__init__(self)
        self.downloadTask = downloadTask

 
 
    def run(self):
        response = get(self.downloadTask.host,self.downloadTask.path)
        response.parse()
        # print(downloadResponse.body)
        print(response)


'''
//////////////////////////////////// START
'''



print(sys.argv)



ARG_NO_OF_CONNECTIONS =  sys.argv[1] if sys.argv[1] else "1"
ARG_INTERVAL = sys.argv[2] if sys.argv[2] else "1"
ARG_CON_TYPE = sys.argv[3] if sys.argv[3] else  "tcp"
ARG_URL = sys.argv[4] if sys.argv[4] else "https://s.aolcdn.com/hss/storage/midas/9177f1bff2326923725e0ed737583830/201851840/putinmeme02.jpg"
ARG_SAVE_AT = sys.argv[5] if sys.argv[5] else  "output/.default"
ARG_RESUME = sys.argv[6] if sys.argv[6] else  "1"

    
ARG_URL = "http://localhost/add_item.png"
ARG_URL = "http://www.gsfdcy.com/data/img1/60/1826675-natur-wallpaper.jpg" 


host = 'localhost'
port = 80  # web

p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
p = '(https?://)([^:^/]*)(:\\d*)?(.*)?'

m = re.search(p,ARG_URL)
host = m.group(2) if m.group(2) else 'localhost'
port = int(m.group(3)) if m.group(3) else 80
uri =  m.group(4) if m.group(4) else ''
print(host)
print(port)
print(uri)


response = getHeader(host,uri)
response.parse()
print(response)
total = response.headers.getContentLength()

downloadResponse = get(host,uri,0,total,total)


downloadResponse.parse()
# print(downloadResponse.body)
print(downloadResponse)




# save
f = open('output/'+ARG_SAVE_AT, 'wb+')
f.write(downloadResponse.body)
f.close()


# open
adsPath = os.path.abspath('output/'+ARG_SAVE_AT)
os.startfile(adsPath)
print("The file is downloaded as: "+adsPath)
