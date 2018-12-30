# Socket client example in python

import socket
import sys
import re
import os
import io
import time

from threading import Thread
from multiprocessing import Process, Lock

CHUNK_SIZE = 4096
CRLF = b"\r\n\r\n"


downloadSubTasks = []
finalFile  = []
mutex = Lock()


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
        return str("HEADERS:"+self.headers)
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
        return str("RESPONSE::::::::::::::::\n"+self.response_code+"\n"+str(self.headers)+("" if self.body==b'' else "\nBODY EXISTS: "+str(self.headers.getContentLength())))


class Requestt:
    index =-1
    host = ''
    uri = ''
    total = 0
    start=0
    end = 0
    count=0

    interval = 1000

    timeSnap = 0
    countSnap = 0
    speedSnap = 0
    def __init__(self,index, host,uri,total=0,start=0,end=0):
        self.index = index
        self.host = host
        self.uri = uri
        self.total = total
        self.start = start
        self.end = end
    
    def setCount(self,count):
        self.count = count
    def setTimeSnap(self,timeSnap):
        self.timeSnap = timeSnap
    def setCountSnap(self,count):
        self.countSnap = count
    def setSpeedSnap(self,speedSnap):
        self.speedSnap = speedSnap
'''
FUNCTIONS
'''


# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(now,request):
    barLength = 50 # Modify this to change the length of the progress bar
    end = request.total
    status = ""
    progress = now/total
    startFrom = request.start/total
    
    block = int(round(barLength*progress))
    blockBefore = int(round(barLength*startFrom))
    # with mutex:
    text = "\rThread{0} [{1}] {2} Kb/s".format( request.index, "-"*(blockBefore)+">"*block + "-"*(barLength-(block+blockBefore)) ,  request.speedSnap)
    sys.stdout.write(text)
    sys.stdout.flush()
    return text


'''
collects all the chucks
'''
def receive_all(sock,request, chunk_size=CHUNK_SIZE ):
    '''
    Gather all the data from a request.
    '''
    chunks = []   
    temp = 0 
    while True:
        chunk = sock.recv(int(chunk_size))
        if chunk:
            chunks.append(chunk)            
            temp+=len(chunk)
            request.setCount(temp)
            millis = int(round(time.time() * 1000))
            if millis - request.timeSnap > request.interval:
                request.setSpeedSnap(((temp-request.countSnap)/1024*1024)/request.interval )
                request.setCountSnap(temp)
                request.setTimeSnap(millis)
            if request.total != 0:
                text = update_progress(temp,request)
                # sys.stdout.write(text)
                # sys.stdout.flush()
        else:
            break
    return b''.join(chunks)

def parseResponse(data):
    splitted = data.split(CRLF, 1)
    headers = splitted[0].decode()
    request_line = headers.split('\n')[0]
    response_code = request_line.split()[1]
    headers = headers.replace(request_line, '')

'''
get http request and return response object
'''
def get(request):
    # create socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Failed to create socket')
        sys.exit()
    try:
        remote_ip = socket.gethostbyname( request.host )
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting')
        sys.exit()
    # Connect to remote server
    s.connect((remote_ip , port))
    # Send data to remote server

    start = request.start
    end = request.end
    total = request.total
    
    rangeHeader = "\r\n"+ "Range: bytes="+str(request.start)+"-"+str(request.end if request.end!=0 else request.total) 
    httpRequest = ("HEAD " if request.total == 0 else "GET ")+request.uri+" HTTP/1.0\r\nHost: "+ request.host + ("" if request.total == 0 else rangeHeader  )
    print("\n"+httpRequest)
    httpRequest +="\r\n\r\n"
    try:
        s.sendall(httpRequest.encode())
    except socket.error:
        print('Send failed')
        sys.exit()

    # Receive data
    data = receive_all(s,request,CHUNK_SIZE)
    

    return Response(data)

'''
Just headers 
'''
def getHeader(host,path):
    return get(Requestt(-1,host,path))


'''
THREADS
'''
class DownloaderThread(Thread):
    request:Requestt 
    def __init__(self, request):
        ''' Constructor. '''
        Thread.__init__(self)
        self.request = request

 
 
    def run(self):
        
        response = get(self.request)
        response.parse()
        with mutex:
            print("\n")
            # finalFile.insert(self.request.index,response.body)
            finalFile[self.request.index] = response.body
        
        # print(response)

class ProgressThread(Thread):
    interval = 1000
    def __init__(self,interval):
        ''' Constructor. '''
        Thread.__init__(self)
        self.interval = interval

 
 
    def run(self):
        time.sleep(self.interval)
        text = ''


        for dTask in downloadSubTasks:
            text +=update_progress(dTask.count,dTask)

        sys.stdout.write(text)
        sys.stdout.flush()
        # self.
'''
//////////////////////////////////// START
'''



print(sys.argv)



ARG_NO_OF_CONNECTIONS =  int(sys.argv[1] if sys.argv[1] else "1")
ARG_INTERVAL = int(sys.argv[2] if sys.argv[2] else "1000")
ARG_CON_TYPE = sys.argv[3] if sys.argv[3] else  "tcp"
ARG_URL = sys.argv[4] if sys.argv[4] else "https://s.aolcdn.com/hss/storage/midas/9177f1bff2326923725e0ed737583830/201851840/putinmeme02.jpg"
ARG_SAVE_AT = sys.argv[5] if sys.argv[5] else  "output/.default"
ARG_RESUME = sys.argv[6] if sys.argv[6] else  "1"

    
# ARG_URL = "http://localhost/add_item.png"
# ARG_URL = "https://sample-videos.com/video123/mp4/480/big_buck_bunny_480p_5mb.mp4"
# ARG_URL = "http://localhost/big_buck_bunny_480p_5mb.mp4"
# ARG_URL = "https://3.bp.blogspot.com/-FYjlw5lYV_Q/VCaXoNp-PTI/AAAAAAAAHmk/cLuCv4Ruq_U/s1600/37.jpg"
# ARG_URL = "http://www.gsfdcy.com/data/img1/60/1826675-natur-wallpaper.jpg" 



p = '(https?://)([^:^/]*)(:\\d*)?(.*)?'

m = re.search(p,ARG_URL)
host = m.group(2) if m.group(2) else 'localhost' #default is localhost
port = int(m.group(3)) if m.group(3) else 80 #default port is 80
uri =  m.group(4) if m.group(4) else ''
print(host)
print(port)
print(uri)

# get header only to find out the size of the file
response = getHeader(host,uri)
response.parse() # need to call parse() before using the response
print(response)
total = response.headers.getContentLength()



'''
Divide into sub tasks
'''

no_of_threads = ARG_NO_OF_CONNECTIONS
chunk = int(total /no_of_threads) 
temp = -1
threads = list()


# ProgressThread(ARG_INTERVAL).start()

# create threads 
for i in range(no_of_threads):
    start = temp+1 if temp<total else temp
    end = temp+chunk if total>= (temp+chunk) else total-1
    threads.append(DownloaderThread(Requestt(i,host,uri,total,start,end)))
    temp+=chunk

# initialize array before starting threads
for thread in threads:
    finalFile.append(b'')
    thread.start()

# wait for all of them to complete
for thread in threads:
    thread.join()









# print(finalFile)


# save
f = open('output/'+ARG_SAVE_AT, 'wb+')
for s in finalFile:
    f.write(s)
f.close()


# open
adsPath = os.path.abspath('output/'+ARG_SAVE_AT)
os.startfile(adsPath)
print("The file is downloaded as: "+adsPath)
