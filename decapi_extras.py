#!/usr/bin/env python3
'''
Gitago's Stream Extras Plugin
'''

import sys
import TouchPortalAPI as TP
import requests
import re
import urllib.request as urllib2
import random
import time
from threading import Thread
from collections import deque
# imports below are optional, to provide argument parsing and logging functionality
from argparse import ArgumentParser
from logging import (getLogger, Formatter, NullHandler, FileHandler, StreamHandler, DEBUG, INFO, WARNING)

__version__ = "1.4"

PLUGIN_ID = "gitago.streamextras.plugin"

TP_PLUGIN_INFO = {
    'sdk': 3,
    'version': int(float(__version__) * 1),  
    'name': "Stream Extras",
    'id': PLUGIN_ID,
    'configuration': {
        'colorDark': "#a1a915",
        'colorLight': "#676767",
    }
}   

TP_PLUGIN_SETTINGS = {
    'TwitchChannelID': {
        'name': "Twitch ID",
        'type': "text",
        'default': "",
        'readOnly': False, 
    },
    'YoutubeID': {
        'name': "Youtube ID",
        'type': "text",
        'default': "",
        'readOnly': False, 
    
    },
    'WaitTime': {
        'name': "Wait Time",
        'type': "number",
        'default': "3",
        'readOnly': False, 
    
    }
}

TP_PLUGIN_CATEGORIES = {
    "streamextras": {
        'id': PLUGIN_ID + ".streamextras",
        'name': "Stream Extras",
        'imagepath': "%TP_PLUGIN_FOLDER%Countdown Plugin/timer_git.png"
    },
    "lists": {
        'id': PLUGIN_ID + ".lists",
        'name': "List Stuff",
        'imagepath': "%TP_PLUGIN_FOLDER%Countdown Plugin/timer_git.png"
    }
}


TP_PLUGIN_ACTIONS = {

    'action2': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".act.get.game2",
        'name': "Twitch Extras",
        'prefix': TP_PLUGIN_CATEGORIES['streamextras']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "Get {$gitago.streamextras.plugin.act.get.choice$} for {$gitago.streamextras.plugin.act.viewer.name$} ",
        'data': {
            'viewername': {
                'id': PLUGIN_ID + ".act.viewer.name",
                'type': "text",
                'label': "viewer name",
                'default': "",
            },
            'hours': {
                'id': PLUGIN_ID + ".act.get.choice",
                'type': "choice",
                'label': "Your Choice",
                'default': "",
                'valueChoices': ["Game/Category", "Avatar", "Status", "Account Age", "Follow Age", "Follower Count", "Random User", "Up-Time", "Highlights", "Most Recent Upload", "Total Views", "Viewer Count" ]
            },
        }
    },
    'action1': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".act.get.game1",
        'name': "Get (X) Followers [100 max]",
        'prefix': TP_PLUGIN_CATEGORIES['streamextras']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "Retrieve {$gitago.streamextras.plugin.act.get.count$} {$gitago.streamextras.plugin.act.get.choice2$} for {$gitago.streamextras.plugin.act.viewer.name2$} {$gitago.streamextras.plugin.act.asc.desc$} ",
        'data': {
            'viewername': {
                'category': "streamextras",
                'id': PLUGIN_ID + ".act.viewer.name2",
                'type': "text",
                'label': "viewer name",
                'default': "",
            },
            'hours': {
                'category': "streamextras",
                'id': PLUGIN_ID + ".act.get.choice2",
                'type': "choice",
                'label': "See Multiple Followers or Videos",
                'default': "Follower(s)",
                'valueChoices': [ "Follower(s)" ]
            },
            'count': {
                'id': PLUGIN_ID + ".act.get.count",
                'type': "number",
                'label': "count",
                'default': "0",
                "minValue": 0,
                "maxValue": 100,
                'allowDecimals': False
            },
            'desc/asc': {
                'id': PLUGIN_ID + ".act.asc.desc",
                'type': "choice",
                'label': "asc or desc",
                'default': "Descending",
                'valueChoices': ["Ascending", "Descending"]
            },
        } 
    },
        'action4': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".act.get.youtubevideo",
        'name': "Get Youtube Video URL + Description",
        'prefix': TP_PLUGIN_CATEGORIES['streamextras']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "Retrieve latest {$gitago.streamextras.plugin.act.get.choice3$}",
        'data': {
            'viewername': {
                'category': "streamextras",
                'id': PLUGIN_ID + ".act.viewer.name3",
                'type': "text",
                'label': "viewer name",
                'default': "",
            },
            'hours': {
                'category': "streamextras",
                'id': PLUGIN_ID + ".act.get.choice3",
                'type': "choice",
                'label': "See Multiple Followers or Videos",
                'default': "Youtube Video",
                'valueChoices': [ "Youtube Video" ]
            },
        } 
    },
   'Live Youtube URL': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".act.live.youtubeurl",
        'name': "Get Live Youtube URL",
        'prefix': TP_PLUGIN_CATEGORIES['streamextras']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "Get the Live Youtube URL for {$gitago.streamextras.plugin.act.youtuber.name$}",
        'data': {
            'Live Stream to Get': {
            'category': "streamextras",
            'id': PLUGIN_ID + ".act.youtuber.name",
            'type': "text",
            'label': "Retrieve Live Youtube URL / Channel Trailer ",
            'default': "",
            }
        }
    },
    'action3': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".act.random",
        'name': "Pick Random Active Chatter",
        'prefix': TP_PLUGIN_CATEGORIES['streamextras']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "Get Random {$gitago.streamextras.plugin.act.get.randomchoice$}",
        'data': {
            'randomchoice': {
            'category': "streamextras",
            'id': PLUGIN_ID + ".act.get.randomchoice",
            'type': "choice",
            'label': "Your Choice",
            'default': "",
            'valueChoices': ["Random User"]
            },
        }
    },
    'List Stuff': {
        'category': "lists",
        'id': PLUGIN_ID + ".act.list",
        'name': "Add or Remove to/from Lists",
        'prefix': TP_PLUGIN_CATEGORIES['streamextras']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "{$gitago.streamextras.plugin.act.list.add.remove$} {$gitago.streamextras.plugin.act.list.chatter$} to the list {$gitago.streamextras.plugin.act.list.name$}",
        'data': {
            'List Names .act.list': {
            'id': PLUGIN_ID + ".act.list.name",
            'type': "choice",
            'label': "Pick a Name",
            'default': "Chatter List",
            'valueChoices': ["Chatter List", "Giveaway List"]
            },
             'Add or Remove Person': {
            'id': PLUGIN_ID + ".act.list.add.remove",
            'type': "choice",
            'label': "Lists: Add / Remove Person ",
            'default': "Add",
            'valueChoices': ["Add", "Remove"]
            },
            'name of person': {
                'id': PLUGIN_ID + ".act.list.chatter",
                'type': "text",
                'label': "Chatter to Add or Remove",
                'default': "",
            },
        }
    },
    'Clear List': {
        'category': "lists",
        'id': PLUGIN_ID + ".act.clearlist",
        'name': "Pick Random, or Clear List",
        'prefix': TP_PLUGIN_CATEGORIES['lists']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "{$gitago.streamextras.plugin.act.list.clear.or.random$} the list {$gitago.streamextras.plugin.act.list.clear$}",
        'data': {
            'List Names .act.list.clear': {
            'category': "lists",
            'id': PLUGIN_ID + ".act.list.clear",
            'type': "choice",
            'label': "Clear a List",
            'default': "",
            'valueChoices': ["Chatter List", "Giveaway List"]
            },
            'Clear or Random': {
            'category': "lists",
            'id': PLUGIN_ID + ".act.list.clear.or.random",
            'type': "choice",
            'label': "Clear a List",
            'default': "",
            'valueChoices': ["Pick Random from", "Clear"]
            }
        }
    },
    ###
    'Start/Stop/Pause Active Queue': {
        'category': "lists",
        'id': PLUGIN_ID + ".act.queue",
        'name': "Start/Stop Chatter Queue",
        'prefix': TP_PLUGIN_CATEGORIES['streamextras']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "{$gitago.streamextras.plugin.act.queue.choice$} the New Chatter Queue ",
        'data': {
            'List Names .act.list': {
            'id': PLUGIN_ID + ".act.queue.choice",
            'type': "choice",
            'label': "Start or stop",
            'default': "Stop",
            'valueChoices': ["Start", "Stop", "Pause"]
            },
        }
    },
    ##
}

# Plugin static or dynamic state(s). 
TP_PLUGIN_STATES = {
    'recentfollowers': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.recentchannelfollower",
        'type': "text",
        'desc': "Channel's Recent Follower(s)",
        'default': ""
    },
    'highlights': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.highlight",
        'type': "text",
        'desc': "Channel's Highlights URL",
        'default': ""
    },
    'viewer_game': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.gametitle",
        'type': "text",
        'desc': "User - Last Game/Category Streamed",
        'default': ""
    },
    'channel_status': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.channelstatus",
        'type': "text",
        'desc': "User - Channel Description",
        'default': ""
    },
    'avatar_URL': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.avatarurl",
        'type': "text",
        'desc': "User - Avatar URL",
        'default': ""
    },
    'followercount': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.followerscount",
        'type': "text",
        'desc': "User - Follower Count",
        'default': ""
    },
    'viewercount': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.viewercount",
        'type': "text",
        'desc': "User - Viewer Count",
        'default': ""
    },
    'totalviews': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.totalviews",
        'type': "text",
        'desc': "User - Total Channel Views",
        'default': ""
    },
    'creationdate': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.accountage",
        'type': "text",
        'desc': "User - Created Date",
        'default': ""
    },
    'Follow Age': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.followage",
        'type': "text",
        'desc': "User - Follow Age",
        'default': ""
    },
    'randompick': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.randompick",
        'type': "text",
        'desc': "Random - Pick",
        'default': ""
    },
    'randomuser': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.randomuser",
        'type': "text",
        'desc': "Random - Active User Selection",
        'default': ""
    },
    'recentupload': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.recentupload",
        'type': "text",
        'desc': "Recent - Upload Full Details ",
        'default': ""
    },
    'Most Recent Video: URL': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.uploadurl",
        'type': "text",
        'desc': "Recent Video - Upload URL",
        'default': ""
    },
    'Most Recent Video: Title': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.uploadtitle",
        'type': "text",
        'desc': "Recent Video - Upload Title",
        'default': ""
    },
    'Youtube Live Video: Full URL': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.youtubeliveurl",
        'type': "text",
        'desc': "Youtube LIVE - Full URL ",
        'default': ""
    },
    'Youtube Recent Video: Full Info': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.youtubevideofull",
        'type': "text",
        'desc': "Youtube Video - Description + URL ",
        'default': ""
    },
    'Youtube Recent Video: URL': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.youtubevideourl",
        'type': "text",
        'desc': "Youtube Video - URL",
        'default': ""
    },
    'Youtube Recent Video: Description': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.youtubevideodescription",
        'type': "text",
        'desc': "Youtube Video - Description",
        'default': ""
    },
#    'New Chatter Status': {
#        'category': "lists",
#        'id': PLUGIN_ID + ".state.chatterlist.queuestatus",
#        'type': "text",
#        'desc': "Chatter List: Queue Status",
#        'default': "False"
#    },
    'New Chatter Name': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.chattername",
        'type': "text",
        'desc': "New Chatter Name",
        'default': ""
    },
    'Chatter List Status': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.status",
        'type': "text",
        'desc': "Chatter List - Status",
        'default': ""
    },
    'Chatter List Total': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.chattertotal",
        'type': "text",
        'desc': "Chatter List - Total Chatters",
        'default': ""
    },
    'Chatter Queue Total': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.queuetotal",
        'type': "text",
        'desc': "Chatter List - Chat Queue Total",
        'default': ""
    },   
    'Chatter List Random Pick': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.random",
        'type': "text",
        'desc': "Chatter List - Random Pick",
        'default': ""
    },
    'Giveaway List Status': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.giveawaylist.status",
        'type': "text",
        'desc': "Giveaway List - Status",
        'default': ""
    },
    'Giveaway List Total': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.giveawaylist.total",
        'type': "text",
        'desc': "Giveaway List - Total",
        'default': ""
    },
    'Giveaway List Random Pick': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.giveawaylist.random",
        'type': "text",
        'desc': "Giveaway List - Random Pick",
        'default': ""
    },
}

# Plugin Event(s).
TP_PLUGIN_EVENTS = {}

try:
    TPClient = TP.Client(
        pluginId=PLUGIN_ID, 
        sleepPeriod=0.05,  
        autoClose=True,  
        checkPluginId=True,  
        maxWorkers=4, 
        updateStatesOnBroadcast=False,  
    )
except Exception as e:
    sys.exit(f"Could not create TP Client, exiting. Error was:\n{repr(e)}")

#### Main Variables n Such ####
global totalchatterlist
global chatterlist
global giveawaylist #no idea if this global is needed
totalchatterlist = ""
queue = deque([])
cl = []
giveawaylist = []
#have chatterlist = cl because of old code and not tryin to get confused lol
chatterlist = cl
queue_switch = "pause"
running = False
### Settings Stuff #####
#wait = 5
twitchid = ""
youtubeid = ""
#### NOT SURE IF THIS IS NEEDED SINCE IT SETS ELSEWHERE WITH LEGIT INFO??
#########

#####  LIST AND QUEUE THINGS #####

def checkchatter(cn, listname):
    global cl
    global queue
    if cn == "":
        print("its blank")
    if queue_switch =="":
        print("something went wrong")
    if queue_switch == "on" and listname =="Chatter List" and cn not in cl:
        addname(cn, listname)
        print(" name not in list so we adding")
        if queue_switch == "on" and not running:
            main_loop('check')
        if queue_switch =="on" and running:
            print(" sorry its already running you gonna break stuff..")
    elif queue_switch == "on" and listname =="Chatter List" and cn in cl:
        print("No Duplicates allowed")
    if queue_switch == "pause" and listname == "Chatter List" and cn not in cl:
        print("Queue = Paused, but we still accepting entries")
        cl.append(cn)
        queue.append(cn)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuetotal", str(len(queue)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chattertotal", str(len(cl)))
        print("Chatter list ", cl)
        print("Queue List: ", queue)

    if queue_switch == "off" and cn not in cl:
        print("Queue = OFF, No longer accepting entries")
##when TP data matches, it sends info to checkchatter(), if chatter is new it sends over to both lists..
def addname(cn, listname):
    if listname == "Chatter List":
        cl.append(cn)
        queue.append(cn)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuetotal", str(len(queue)))
    
    if listname == "Giveaway List":       
        giveawaylist.append(cn)
        totalgiveawaylist = len(giveawaylist)
        #subtracting -1 every time because of the BLANK entry in the giveawaylist variable
        TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.status", cn + " added.")
        TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.total", str(totalgiveawaylist))

def main_loop(data):
    global running
    if data == "check":
        if queue_switch == "off":
            pass
        if queue_switch == "pause":
            pass
        if queue_switch == "on" and (len(queue)) > 0:
            running = True
            Thread(target = startqueue).start()
                   
        if queue_switch == "on" and (len(queue)) == 0:
            print("But its empty...")
            running = False

        if queue_switch == "off" and (len(queue)) > 0:
            print("queue is off, and we have people waiting")
            running = False

        if queue_switch == "pause" and (len(queue)) > 0:
            print("queue is paused, and we have people waiting")
            running = False

def startqueue():
    while (len(queue)):
        time.sleep(1)
        item = queue.popleft()
        print(item)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chattername", item)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuetotal", str(len(queue)))
        time.sleep(int(wait))
        #wait time controlled via settings depending on what streamer wants.
        #### THIS CONTROLS THE START/STOP ABILITY OF STUFF
        if queue_switch == "off":
            print("Can not continue, Queue is OFF")
            break
        if queue_switch == "pause":
            print("Can not continue, Queue is Paused")
            break
    if queue_switch == "on":
        print("Ok, Queue Started")
##switch is controlled by TP data as well, which looks to see if queue_switch is on/off/paused.. andthen decides what to do then...
def switch(data):
    global queue_switch
    if data == "on":
        queue_switch = "on"
        main_loop('check')
        print("Switch On Initiated: ",queue_switch)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuestatus", "On")
    if data== "off":
        queue_switch = "off"
        print("Switch Off Initiated: ",queue_switch)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuestatus", "Off")
    if data == "pause":
        queue_switch = "pause"
        print("Pause Initiated: ", queue_switch)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuestatus", "Paused")
          
def removename(chattername, listname):
    global chatterlist

    if listname =="Chatter List":
        if chattername in chatterlist:
            chatterlist.remove(chattername)
            totalchatterlist = len(chatterlist)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuetotal", str(totalchatterlist))
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.status", chattername + " removed from list")
            print("1 removed chatter list")

    if listname =="Giveaway List":
        if chattername in giveawaylist:
            giveawaylist.remove(chattername)
            totalgiveawaylist = len(giveawaylist)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.total", str(totalgiveawaylist))
            TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.status", chattername + " removed from list")
            print("1 removed from giveaway list")
        
def clearlist(listclearname):
    global totalchatterlist
    global totalgiveawaylist
    global chatterlist
    global cl
    global giveawaylist

    #put this global in so it can clear queue when it clears chatter list..
    global queue
    if listclearname == "Chatter List":
        print("Chatter List CLEARED")
        cl = []
        chatterlist = []
        queue = deque([])
        totalchatterlist = "0"
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuetotal", str(len(queue)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chattertotal", totalchatterlist)
        print(cl)
    elif listclearname == "Giveaway List":
        print("Giveaway List CLEARED")
        giveawaylist = []
        totalgiveawaylist = "0"
        TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.total", totalgiveawaylist)
#used mainly just to pick a random active chatter
def randomlistpick(listname):
    if listname == "Chatter List":
        randompick = ""
        randompick = random.choice(chatterlist)
        while randompick == "":
            print("but its empty")
            randompick = random.choice(chatterlist)
        else:
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.random", randompick)

    if listname == "Giveaway List":
        randompick = ""
        randompick = random.choice(giveawaylist)
        while randompick == "":
            print("but its empty")
            randompick = random.choice(giveawaylist)
        else:
            TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.random", randompick)

#### END OF LIST/QUEUE FUNCTIONS #####

# TP Client event handler callbacks

# Initial connection handler
@TPClient.on(TP.TYPES.onConnect)
def onConnect(data):
    global twitchid
    global youtubeid
    global wait
    twitchid = data['settings'][0]['Twitch ID']
    youtubeid = data['settings'][1]['Youtube ID']
    wait = data['settings'][2]['Wait Time']
    print("connected")
    


# Settings handler
@TPClient.on(TP.TYPES.onSettingUpdate)
def onSettingUpdate(data):
    global twitchid
    global youtubeid
    global wait
    twitchid = data["values"][0]['Twitch ID']
    youtubeid = data["values"][1]['Youtube ID']
    wait = data['values'][2]['Wait Time']
    


# Action handler
@TPClient.on(TP.TYPES.onAction)
def onAction(data):
    print(data)
    global twitchid
    global youtubeid
    global wait
    youtubename = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.youtuber.name")
    clearorrandom = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.list.clear.or.random")
    queuechoice = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.queue.choice")
    listclearname = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.list.clear")  
    listname = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.list.name")    
    addorremove = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.list.add.remove")   
    chattername = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.list.chatter")
    ascdesc = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.asc.desc")
    viewersname = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.viewer.name")
    viewersname2 = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.viewer.name2")
    viewersname3 = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.viewer.name3")
    count = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.get.count")
    choice = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.get.choice")
    choice2 = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.get.choice2")
    choice3 = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.get.choice3")
    randomchoice = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.get.randomchoice")
    number = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.number")

    if data['actionId'] == "gitago.streamextras.plugin.act.get.game":
            url = ("https://decapi.me/twitch/game/" + viewersname2)
            r = requests.get(url)
            Game = r.text
            TPClient.stateUpdate("gitago.streamextras.plugin.state.gametitle", Game)
    if data['actionId'] == "gitago.streamextras.plugin.act.get.youtubevideo":
                if choice3 == "Youtube Video":
                    url = ("https://decapi.me/youtube/" + "latest_video" +"?id=" + youtubeid)
                    r = requests.get(url)
                    urlcontent = r.text
                    #this is everything after the -
                    uploadurl = re.search(r'(?<= - ).*', urlcontent)
                    #this is everything before the - 
                    uploadtitle = re.search(r'.*(?= - )', urlcontent)
                    TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideourl", uploadurl.group(0))
                    TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideodescription", uploadtitle.group(0))
                    TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideofull", r.text)      

# Action 1 Stuff
    if data['actionId'] == "gitago.streamextras.plugin.act.get.game1":
            if choice2 == "Follower(s)":
                if count == "" or count == "0":
                    if ascdesc == "Descending":
                        print("ok its 0 or empty")
                        url = ("https://decapi.me/twitch/" + "followers" +"?channel=" + viewersname2 + "&direction=desc")
                        r = requests.get(url)
                        TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)
                    if ascdesc == "Ascending":                     
                        url = ("https://decapi.me/twitch/" + "followers" +"?channel=" + viewersname2 + "&direction=asc")
                        r = requests.get(url)
                        TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)
                            
                else:
                    if ascdesc =="Descending":
                        url = ("https://decapi.me/twitch/" + "followers" +"?channel=" + viewersname2 +"&count=" + count + "&num&separator=%20-%20" + "&direction=desc")
                        r = requests.get(url)
                        TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)
                    if ascdesc =="Ascending":
                        url = ("https://decapi.me/twitch/" + "followers" +"?channel=" + viewersname2 +"&count=" + count + "&num&separator=%20-%20" + "&direction=asc")
                        r = requests.get(url)
                        TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)

            if choice2 == "Video(s)":
                if count == "" or count == "0":
                    url = ("https://decapi.me/twitch/" +"videos/" + viewersname2)
                    r = requests.get(url)
#                    TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)
                    print(url)
                else:
                    url = ("https://decapi.me/twitch/" +"videos/" + viewersname2 + "?limit=" + count +"&separator=%20-%20")
                    r = requests.get(url)
#                    TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)
                    print(url)

            if choice2 == "Youtube Video":
                url = ("https://decapi.me/youtube/" + "latest_video" +"?id=" + youtubeid)
                r = requests.get(url)
                urlcontent = r.text
                print(r.text)
                #this is everything after the -
                uploadurl = re.search(r'(?<= - ).*', urlcontent)
                #this is everything before the - 
                uploadtitle = re.search(r'.*(?= - )', urlcontent)
                TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideourl", uploadurl.group(0))
                TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideodescription", uploadtitle.group(0))
                TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideofull", r.text) 
                print(uploadtitle.group(0))
                print(uploadurl.group(0))



# Action 2 Stuff
    if data['actionId'] == "gitago.streamextras.plugin.act.get.game2":
        if choice == "Game/Category":
                url = ("https://decapi.me/twitch/" + "game" +"/" + viewersname)
                r = requests.get(url)
                Game = r.text
                TPClient.stateUpdate("gitago.streamextras.plugin.state.gametitle", Game)

        if choice == "Status":
            url = ("https://decapi.me/twitch/" + "status" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.channelstatus", r.text)
        
        if choice == "Avatar":
            url = ("https://decapi.me/twitch/" + "avatar" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.avatarurl", r.text)
        
        if choice == "Follower Count":
            url = ("https://decapi.me/twitch/" + "followcount" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.followerscount", r.text)

        if choice == "Highlights":
            url = ("https://decapi.me/twitch/" + "highlight" +"/" + viewersname)
            r = requests.get(url)
            stupidcheck = viewersname +" has no saved highlights."
            if r.text == stupidcheck:
                TPClient.stateUpdate("gitago.streamextras.plugin.state.highlight", "No Highlights Available")    
            else:
                TPClient.stateUpdate("gitago.streamextras.plugin.state.highlight", r.text)
        
        if choice == "Last Follower(s)":
            url = ("https://decapi.me/twitch/" + "followers" +"?channel=" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)


        if choice == "Account Age":
            url = ("https://decapi.me/twitch/" + "accountage" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.accountage", r.text)

        if choice == "Follow Age":
            url = ("https://decapi.me/twitch/" + "followage" +"/" + twitchid + "/" + viewersname)
            print(url)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.followage", r.text)


        if choice == "Random User":
            url = ("https://decapi.me/twitch/" + "random_user" +"/" + viewersname.lower())
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.randomuser", r.text)

        if choice == "Up-Time":
            url = ("https://decapi.me/twitch/" + "uptime" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.uptime", r.text)

        if choice == "Viewer Count":
            url = ("https://decapi.me/twitch/" + "viewercount" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.viewercount", r.text)

        if choice == "Total Views":
            url = ("https://decapi.me/twitch/" + "total_views" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.totalviews", r.text)    

###########need to use regex to seperate this     #Its formatted like this...   TEC Season 2 Highlights  - https://www.twitch.tv/videos/876780091
        if choice == "Most Recent Upload":
            url = ("https://decapi.me/twitch/" + "upload" +"/" + viewersname)
            r = requests.get(url)
            urlcontent = r.text
            if r.text == viewersname + " has no uploaded videos.":
                TPClient.stateUpdate("gitago.streamextras.plugin.state.uploadurl", r.text)
                TPClient.stateUpdate("gitago.streamextras.plugin.state.uploadtitle", r.text)
                TPClient.stateUpdate("gitago.streamextras.plugin.state.recentupload", r.text) 
            else:
                #this is everything after the -
                uploadurl = re.search(r'(?<= - ).*', urlcontent)
                #this is everything before the - 
                uploadtitle = re.search(r'.*(?= - )', urlcontent)
                TPClient.stateUpdate("gitago.streamextras.plugin.state.uploadurl", uploadurl.group(0))
                TPClient.stateUpdate("gitago.streamextras.plugin.state.uploadtitle", uploadtitle.group(0))
                TPClient.stateUpdate("gitago.streamextras.plugin.state.recentupload", r.text)     
  

# Action 3 Stuff
    if data['actionId'] == "gitago.streamextras.plugin.act.random":
        if randomchoice == "Random User":
            url = ("https://decapi.me/twitch/" + "random_user" +"/" + twitchid.lower())
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.randompick", r.text)


## If clearing the lists    
    if data['actionId'] == "gitago.streamextras.plugin.act.clearlist":
        if clearorrandom == "Clear" and listclearname == "Chatter List":
            clearlist(listclearname)
        if clearorrandom == "Clear" and listclearname == "Giveaway List":
            clearlist(listclearname)
## If picking random from list
## Maybe i should amke this a function, who knows...
        if clearorrandom == "Pick Random from" and listclearname == "Chatter List":
            randomlistpick(listclearname)
        if clearorrandom == "Pick Random from" and listclearname == "Giveaway List":
            randomlistpick(listclearname)
##live yuotube
    if data['actionId'] == "gitago.streamextras.plugin.act.live.youtubeurl":
        starturl = "http://www.youtube.com/channel/" + youtubename+ "/live"
        watchurl = "https://www.youtube.com/watch?v="
        r = urllib2.urlopen(starturl)
        decoded = (r.read().decode())
        video_ids = re.findall(r"watch\?v=(\S{11})", decoded)
        livevideoid = (video_ids[0])
        print(watchurl + livevideoid)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubeliveurl", watchurl + livevideoid)
            
 
 # If adding to Chatter List
    if data['actionId'] == "gitago.streamextras.plugin.act.list":
        if listname == "Chatter List" and addorremove == "Add":
            checkchatter(chattername, listname)

        if listname == "Giveaway List":
            if addorremove == "Add":
                if chattername in giveawaylist:
                    print("Giveaway List: Already Added")
                else:
                    addname(chattername, listname)
## If removing from Giveaway List
        if addorremove == "Remove":
            removename(chattername, listname)
            print(chatterlist)
 
    if data['actionId'] == "gitago.streamextras.plugin.act.queue":
        if queuechoice == "Stop":
            switch('off')
        if queuechoice == "Start":
            switch('on')
        if queuechoice == "Pause":
            switch('pause')



# Shutdown handler
@TPClient.on(TP.TYPES.onShutdown)
def onShutdown(data):
    print(data)


# Error handler
@TPClient.on(TP.TYPES.onError)
def onError(exc):
    print(exc)

TPClient.connect()

