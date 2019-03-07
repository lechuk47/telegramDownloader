from telethon import TelegramClient, sync, functions, types
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputMessagesFilterDocument
from telethon.errors import FloodWaitError
import asyncio
import time
import os
import sys
import re

loop = asyncio.get_event_loop()

API_ID=os.environ["TG_API_ID"]
API_HASH=os.environ["TG_API_ID"]
CHANNEL_NAME=os.environ["CHANNEL"]
DL_PATH="/media"

last_current=0
last_time=0

def progress_callback(current, total):
    global last_current, last_time
    now = time.time()
    speed = round(((current-last_current)/(now-last_time))/1000)
    last_current = current
    last_time = now
    percent = int((current/total)*100)
    #print('{} % .... {} KB/s'.format(percent, speed))
    sys.stdout.write("Download progress: %d%% %d KB/s  \r" % (percent, speed) )
    sys.stdout.flush()

def chunkify(list, elements):
    for i in range(0, len(list), elements):
        yield list[i:i + elements]

        
def messageKey(m):
    return m.media.document.attributes[0].file_name

async def main():
    client = TelegramClient('lechuk-dl', API_ID, API_HASH)
    await client.start()
    await client(functions.channels.JoinChannelRequest(channel=CHANNEL_NAME))

    messages = []
    async for message in client.iter_messages(CHANNEL_NAME, filter=InputMessagesFilterDocument):
        filename = message.media.document.attributes[0].file_name
        size = message.media.document.size
        dest_filename = DL_PATH + "/" + filename
    #    if not re.match("[45][xX]", filename ):
    #        continue
        #print(message.stringify())
        #print(filename + " -> " + str(size))
        if os.path.isfile(dest_filename):
            if os.path.getsize(dest_filename) != size:
                # partial download, redownload the file
                os.remove(dest_filename)
                messages.append(message)
            else:
                print("File %s already downloaded with its correct size" % filename)
        else:
            messages.append(message)
            #messages[message.id] = message



    #keys = [ k for k in list(messages.keys()) ]
    last_current=0
    last_time=0

    for message in sorted(messages,key=lambda x: x.id):
        try:
            print("Downloading %s" % message.media.document.attributes[0].file_name)
            await client.download_media(message, DL_PATH, progress_callback=progress_callback)
            print("")
        except FloodWaitError as fwe:
            print("FloodWaitError -> Sleeping: %d", fwe.seconds)
            sleep(fwe.seconds)




    await client.disconnect()
#    chunks = chunkify(messages.sort(key=lambda x: x.media.document.attributes[0].file_name),2)
#    for chunk in list(chunks):
#        try:

#        except FloodWaitError:


#        await asyncio.gather(
#            *[ client.download_media(message, DL_PATH) for message in chunk ],
#        )



loop.run_until_complete(main())
