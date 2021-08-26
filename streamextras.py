#!/usr/bin/env python3
### send new update to github.. ugh


####                    ATTENTION


#####          SEMI EXPIRMENTAL BUILD


##try .ljust and .rjust to get text file to save better for OBS preview

#Add Custom column alignmetn choice
#print(tabulate([["one", "two"], ["three", "four"]], colalign=("right",))   example..




#line 794, keep adding in the TOP chatter variables.. all seems well so far..  








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
from tabulate import tabulate
from threading import Thread
from collections import deque
# imports below are optional, to provide argument parsing and logging functionality
from argparse import ArgumentParser
from logging import (getLogger, Formatter, NullHandler, FileHandler, StreamHandler, DEBUG, INFO, WARNING)

__version__ = "2.2"

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
        'name': "SE | Stream Extras",
        'imagepath': "%TP_PLUGIN_FOLDER%Countdown Plugin/timer_git.png"
    },
    "lists": {
        'id': PLUGIN_ID + ".lists",
        'name': "SE | Lists",
        'imagepath': "%TP_PLUGIN_FOLDER%Countdown Plugin/timer_git.png"
    },
     "giveaway_lists": {
        'id': PLUGIN_ID + ".giveawaylist",
        'name': "SE | Lists: Giveaway",
        'imagepath': "%TP_PLUGIN_FOLDER%Countdown Plugin/timer_git.png"
    },
     "youtube_extras": {
        'id': PLUGIN_ID + ".youtube_extras",
        'name': "SE | Youtube",
        'imagepath': "%TP_PLUGIN_FOLDER%Countdown Plugin/timer_git.png"
    }
}


TP_PLUGIN_ACTIONS = {
    'action1': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".act.get.game2",
        'name': "Twitch Extras (Get Info)",
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
    'action2': {
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
        'action3': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".act.get.youtubevideo",
        'name': "Get YT Video URL + Description",
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
   'Action 4': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".act.live.youtubeurl",
        'name': "Get YT Live URL",
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
    'action5': {
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
    'action6': {
        'category': "lists",
        'id': PLUGIN_ID + ".act.list",
        'name': "Add or Remove to/from a List",
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
    'action7': {
        'category': "lists",
        'id': PLUGIN_ID + ".act.clearlist",
        'name': "Save or Clear a List",
        'prefix': TP_PLUGIN_CATEGORIES['lists']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "{$gitago.streamextras.plugin.act.list.clear.or.save$} the list {$gitago.streamextras.plugin.act.list.clear$} in the format {$gitago.streamextras.plugin.act.list.listsaveformat$}",
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
            'id': PLUGIN_ID + ".act.list.clear.or.save",
            'type': "choice",
            'label': "Save or Clear a List",
            'default': "",
            'valueChoices': ["Save", "Clear"]
            },
            'List Save Format': {
            'category': "lists",
            'id': PLUGIN_ID + ".act.list.listsaveformat",
            'type': "choice",
            'label': "Save Format",
            'default': "",
            'valueChoices': ["Grid", "Fancy_Grid", "Github", "Simple", "Presto", "Pretty", "PSQL", "Pipe", "Orgtbl", "Jira", "Rst", "MoinMoin", "YouTrack", "Textile", "HTML", "Latex"]
            }
        }
    },
    'action8': {
        'category': "lists",
        'id': PLUGIN_ID + ".act.random.hold",
        'name': "On Hold Random Pick",
        'prefix': TP_PLUGIN_CATEGORIES['lists']['name'],
        'type': "communicate",
        "tryInline": True,
        "hasHoldFunctionality": True,
        'format': "Pick a Random Person from {$gitago.streamextras.plugin.act.onhold.listchoice$}  ",
        'data': {
            'on hold random pick': {
                'id': PLUGIN_ID + ".act.onhold.listchoice",
                'type': "choice",
                'label': "Your Choice",
                'default': "",
                'valueChoices': [ "Chatter List", "Giveaway List"]
            },
        }
    },
    'action9': {
        'category': "lists",
        'id': PLUGIN_ID + ".act.list.pickrandom",
        'name': "Pick Random from List",
        'prefix': TP_PLUGIN_CATEGORIES['lists']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "Select a Random User from {$gitago.streamextras.plugin.act.list.choice$}",
        'data': {
            'List Names .act.list.clear': {
            'category': "lists",
            'id': PLUGIN_ID + ".act.list.choice",
            'type': "choice",
            'label': "Pick a Random Choice",
            'default': "",
            'valueChoices': ["Chatter List", "Giveaway List"]
            }
        }
    },
    ###
    'action10': {
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
### giveawaylist.status  needs looked at... its telling what person was removed/added.. 
## need something like it, but to tel lif the giveaway is actively running or not...
# Plugin static or dynamic state(s). 
TP_PLUGIN_STATES = {
    'recentfollowers': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.recentchannelfollower",
        'type': "text",
        'desc': "SE | Channel's Recent Follower(s)",
        'default': ""
    },
    'highlights': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.highlight",
        'type': "text",
        'desc': "SE | Channel's Highlights URL",
        'default': ""
    },
    'viewer_game': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.gametitle",
        'type': "text",
        'desc': "SE | User - Last Game/Category Streamed",
        'default': ""
    },
    'channel_status': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.channelstatus",
        'type': "text",
        'desc': "SE | User - Channel Description",
        'default': ""
    },
    'avatar_URL': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.avatarurl",
        'type': "text",
        'desc': "SE | User - Avatar URL",
        'default': ""
    },
    'followercount': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.followerscount",
        'type': "text",
        'desc': "SE | User - Follower Count",
        'default': ""
    },
    'viewercount': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.viewercount",
        'type': "text",
        'desc': "SE | User - Viewer Count",
        'default': ""
    },
    'totalviews': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.totalviews",
        'type': "text",
        'desc': "SE | User - Total Channel Views",
        'default': ""
    },
    'creationdate': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.accountage",
        'type': "text",
        'desc': "SE | User - Created Date",
        'default': ""
    },
    'Follow Age': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.followage",
        'type': "text",
        'desc': "SE | User - Follow Age",
        'default': ""
    },
    'randompick': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.randompick",
        'type': "text",
        'desc': "SE | Random Active User OTHER",
        'default': ""
    },
    'randomuser': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.randomuser",
        'type': "text",
        'desc': "SE | Random - Active User",
        'default': ""
    },
    'recentupload': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.recentupload",
        'type': "text",
        'desc': "SE | Recent Upload - Full Details ",
        'default': ""
    },
    'Most Recent Video: URL': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.uploadurl",
        'type': "text",
        'desc': "SE | Recent Video - Upload URL",
        'default': ""
    },
    'Most Recent Video: Title': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.uploadtitle",
        'type': "text",
        'desc': "SE | Recent Video - Upload Title",
        'default': ""
    },
    'Youtube Live Video: Full URL': {
        'category': "youtube_extras",
        'id': PLUGIN_ID + ".state.youtubeliveurl",
        'type': "text",
        'desc': "SE | Youtube LIVE - Full URL ",
        'default': ""
    },
    'Youtube Recent Video: Full Info': {
        'category': "youtube_extras",
        'id': PLUGIN_ID + ".state.youtubevideofull",
        'type': "text",
        'desc': "SE | Youtube Video - Description + URL ",
        'default': ""
    },
    'Youtube Recent Video: URL': {
        'category': "youtube_extras",
        'id': PLUGIN_ID + ".state.youtubevideourl",
        'type': "text",
        'desc': "SE | Youtube Video - URL",
        'default': ""
    },
    'Youtube Recent Video: Description': {
        'category': "youtube_extras",
        'id': PLUGIN_ID + ".state.youtubevideodescription",
        'type': "text",
        'desc': "SE | Youtube Video - Description",
        'default': ""
    },
    'New Chatter Status': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.chatterstatus",
        'type': "text",
        'desc': "SE | New Chatter Status",
        'default': "False"
    },
    'The Chatter Queue Status': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.queuestatus",
        'type': "text",
        'desc': "SE | Chatter List: Queue Status",
        'default': ""
    },
    'New Chatter Name': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.chattername",
        'type': "text",
        'desc': "SE | New Chatter Name",
        'default': ""
    },
    'Chatter List Status': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.status",
        'type': "text",
        'desc': "SE | Chatter List - Status",
        'default': ""
    },
    'Chatter List Total': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.chattertotal",
        'type': "text",
        'desc': "SE | Chatter List - Total Chatters",
        'default': ""
    },
    'Chatter Queue Total': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.queuetotal",
        'type': "text",
        'desc': "SE | Chatter List - Chat Queue Total",
        'default': ""
    },   
    'Chatter List Random Pick': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.random",
        'type': "text",
        'desc': "SE | Chatter List - Random Pick",
        'default': ""
    },
    'Giveaway List Status': {
        'category': "giveaway_lists",
        'id': PLUGIN_ID + ".state.giveawaylist.status",
        'type': "text",
        'desc': "SE | Giveaway List - Status",
        'default': ""
    },
    'Giveaway List Total': {
        'category': "giveaway_lists",
        'id': PLUGIN_ID + ".state.giveawaylist.total",
        'type': "text",
        'desc': "SE | Giveaway List - Total",
        'default': ""
    },
    'Giveaway List Random Pick': {
        'category': "giveaway_lists",
        'id': PLUGIN_ID + ".state.giveawaylist.random",
        'type': "text",
        'desc': "SE | Giveaway List - Random Pick",
        'default': ""
    },
    'Top Chatter #1': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatter_first",
        'type': "text",
        'desc': "SE | Top Chatter #1",
        'default': ""
    },
    'Top Chatter #2': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatter_second",
        'type': "text",
        'desc': "SE | Top Chatter #2",
        'default': ""
    },
    'Top Chatter #3': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatter_third",
        'type': "text",
        'desc': "SE | Top Chatter #3",
        'default': ""
    },
    'Top Chatter #4': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatter_fourth",
        'type': "text",
        'desc': "SE | Top Chatter #4",
        'default': ""
    },
    'Top Chatter #5': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatter_fifth",
        'type': "text",
        'desc': "SE | Top Chatter #5",
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
cl = {}
giveawaylist = []
#have chatterlist = cl because of old code and not tryin to get confused lol
chatterlist = cl
queue_switch = "pause"
running = False
### Settings Stuff #####
wait = 0
twitchid = ""
youtubeid = ""
#### NOT SURE IF THIS IS NEEDED SINCE IT SETS ELSEWHERE WITH LEGIT INFO??


#####  LIST AND QUEUE THINGS #####
def checkchatter(chatname, listname):
    global cl
    global queue
    global running
    if chatname == "":
        print("its blank")
    if queue_switch =="":
        print("something went wrong")

    # IF CHATTER LIST ON OR PAUSED
    if queue_switch == "on" or queue_switch == "pause" and listname =="Chatter List":
        update_top_list()
        if chatname in cl: 
            cl[chatname] += 1
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chattertotal", str(len(cl)))           
            print(cl)                   
    #IF NOT IN LIST JUST ADD NAME with 1 and add to queue

        if chatname not in cl:
            cl[chatname] = 1
            queue.append(chatname)
           # print("New Chatter:", chatname, "Added")
            #print("")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chattertotal", str(len(cl)))
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuetotal", str(len(queue)))

        if not running and queue_switch == "on" and (len(queue)) > 0:
            print("startin it up since its off and chatter not in list")
            running = True
            Thread(target = startqueue).start()
        if not running and queue_switch == "pause" and (len(queue)) > 0:
            pass
    # just some what ifs below
        if queue_switch =="on" and running:
            pass

    if queue_switch == "off" and (len(queue)) > 0:
        print("queue is off, and we have people waiting")
        running = False
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chatterstatus", "FALSE")



 #maybe use this for 'multiple lists'..

def addname(chatname, listname):   
    if listname == "Chatter List":
        cl[chatname] += 1
        queue.append(chatname)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuetotal", str(len(queue)))   
    if listname == "Giveaway List":       
        giveawaylist.append(chatname)
        totalgiveawaylist = len(giveawaylist)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.status", chatname + " added.")
        TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.total", str(totalgiveawaylist))


def startqueue():
    global running
    while (len(queue)) >= 0:
        print("The Remaining Queue [",  (len(queue)),  "]: ",  queue)
        print("") 
        item = queue.popleft()
        print("Person removed: ", item, "next in: ", wait, "seconds")
        print("") 
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chatterstatus", "TRUE")
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chattername", item)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuetotal", str(len(queue)))
        time.sleep(2)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chatterstatus", "FALSE")
        time.sleep(int(wait))
        if (len(queue)) == 0:
            print(f"queue is {(str(len(queue)))}, Running is FALSE now")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chatterstatus", "FALSE")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuestatus", "Waiting")
            running = False
            break
        if queue_switch == "off":
            print("Can not continue, Queue is OFF")
            break
        if queue_switch == "pause":
            print("Can not continue, Queue is Paused")
            break
print("Ok, Loop Stopped")

 ##switch is controlled by TP data,  which looks to see if queue_switch is on/off/paused.. andthen decides what to do then...
def switch(data):
    global queue_switch
    global running
    if data == "on" and not running:
        if (len(queue)) == 0:
            queue_switch = "on"
            print("0 in QUEUE, Switch is now ON")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuestatus", "On")
            pass
        if (len(queue)) > 0:
            print(len(queue))
            queue_switch = "on"
            Thread(target = startqueue).start()
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
    #global totalgiveawaylist
    global chatterlist
    global cl
    global giveawaylist
    #put this global in so it can clear queue when it clears chatter list..
    global queue
    if listclearname == "Chatter List":
        print("Chatter List CLEARED")
        cl = {}
        chatterlist = cl
        queue = deque([])
        totalchatterlist = "0"
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuetotal", str(len(queue)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chattertotal", totalchatterlist)
        print(cl)
        print(chatterlist)
        print(queue)
    elif listclearname == "Giveaway List":
        print("Giveaway List CLEARED")
        giveawaylist = []
        totalgiveawaylist = "0"
        TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.total", totalgiveawaylist)
#used mainly just to pick a random active chatter

def randomlistpick(listname):
    if listname == "Chatter List":
        if (int(len(chatterlist))) == 0:
            print("sorry no body in list")
        elif (int(len(chatterlist))) > 0:    
            randompick = random.choice(cl)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.random", randompick)
            while randompick == "":
                print("Something went wrong, picking again")
                TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.random", randompick)
 #            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.random", randompick)

    if listname == "Giveaway List":
        if (int(len(giveawaylist))) == 0:
            print("sorry no body in list")
        elif (int(len(giveawaylist))) > 0:    
            randompick = random.choice(cl)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.random", randompick)
            while randompick == "":
                print("Something went wrong, picking again")
                TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.random", randompick)

def update_top_list():
    global cl
    sorted_chatlist = dict(sorted(cl.items(), key=lambda item: item[1], reverse = True))
    #print(len(cl))
    print(cl)
    if (len(cl)) == 0:
        
      pass

    if (len(cl)) == 1:
            for n, key in enumerate(sorted_chatlist.keys()):
                globals()["name%d"%n] = key
            for n, val in enumerate(sorted_chatlist.values()):
                globals()["count%d"%n] = val

            first = str(count0).ljust(3)+ ":  " + name0.ljust(27)
            
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_first", (str(first)))


    if (len(cl)) == 2:
        for n, key in enumerate(sorted_chatlist.keys()):
            globals()["name%d"%n] = key
        for n, val in enumerate(sorted_chatlist.values()):
            globals()["count%d"%n] = val

        first = str(count0).ljust(3)+ ":  " + name0.ljust(27)
        second = str(count1).ljust(3)+ ":  " + name1.ljust(27)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_first", (str(first)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_second", (str(second)))


    if (len(cl)) == 3:
        for n, key in enumerate(sorted_chatlist.keys()):
            globals()["name%d"%n] = key

        for n, val in enumerate(sorted_chatlist.values()):
            globals()["count%d"%n] = val  

        first = str(count0).ljust(3)+ ":  " + name0.ljust(27)
        second = str(count1).ljust(3)+ ":  " + name1.ljust(27)
        third = str(count2).ljust(3) + ":  " + name2.ljust(27) 
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_first", (str(first)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_second", (str(second)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_third", (str(third)))


    if (len(cl)) == 4:
        for n, key in enumerate(sorted_chatlist.keys()):
            globals()["name%d"%n] = key

        for n, val in enumerate(sorted_chatlist.values()):
            globals()["count%d"%n] = val  

        first = str(count0).ljust(3)+ ":  " + name0.ljust(27)
        second = str(count1).ljust(3)+ ":  " + name1.ljust(27)
        third = str(count2).ljust(3) + ":  " + name2.ljust(27)
        fourth = str(count3).ljust(3) + ":  " + name3.ljust(27)  
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_first", (str(first)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_second", (str(second)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_third", (str(third)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_fourth", (str(fourth)))


    if (len(cl)) == 5:
        for n, key in enumerate(sorted_chatlist.keys()):
            globals()["name%d"%n] = key

        for n, val in enumerate(sorted_chatlist.values()):
            globals()["count%d"%n] = val  

        first = str(count0).ljust(3)+ ":  " + name0.ljust(27)
        second = str(count1).ljust(3)+ ":  " + name1.ljust(27)
        third = str(count2).ljust(3) + ":  " + name2.ljust(27)
        fourth = str(count3).ljust(3) + ":  " + name3.ljust(27)  
        fifth = str(count4).ljust(3) + ":  " + name4.ljust(27)  
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_first", (str(first)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_second", (str(second)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_third", (str(third)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_fourth", (str(fourth)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_fifth", (str(fifth)))


    if (len(cl)) >= 6:
        for n, key in enumerate(sorted_chatlist.keys()):
            globals()["name%d"%n] = key

        for n, val in enumerate(sorted_chatlist.values()):
            globals()["count%d"%n] = val  

        first = str(count0).ljust(3)+ ":  " + name0.ljust(27)
        second = str(count1).ljust(3)+ ":  " + name1.ljust(27)
        third = str(count2).ljust(3) + ":  " + name2.ljust(27)
        fourth = str(count3).ljust(3) + ":  " + name3.ljust(27)  
        fifth = str(count4).ljust(3) + ":  " + name4.ljust(27)  
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_first", (str(first)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_second", (str(second)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_third", (str(third)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_fourth", (str(fourth)))
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatter_fifth", (str(fifth)))


def savelist(list, formatchoice):
    global cl

    if list =="Chat List":
        sorted_chatlist = dict(sorted(chatterlist.items(), key=lambda item: item[1], reverse = True))
        data = [[idx, key, val] for idx, (key, val) in enumerate(sorted_chatlist.items(), start =1)]
        headers = ["#", "Name", "Messages"]
        #print(tabulate(data, headers, tablefmt="presto"))
        print
        tabulated = (tabulate(data, headers, tablefmt= formatchoice.lower() ))
        print(tabulated)
        textfile = open("Active_Chatters.txt", "w")         
        textfile.write(tabulated)
        textfile.close()

    if list =="Giveaway List":
        num = 0
        totalgiveawaylist=(len(giveawaylist))
        textfile = open("Giveaway_List.txt", "w")
        textfile.write("Giveaway List" + " - " + (str(totalgiveawaylist)) + "\n")
        for element in giveawaylist:
            num +=1
            textfile.write(str(num).ljust(2) + " | " + element + "\n")
        textfile.close()

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
    TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.queuetotal", "0")
    TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chattertotal", "0")
    


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
    #print(data)
    global twitchid
    global youtubeid
    global wait
    youtubename = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.youtuber.name")
    queuechoice = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.queue.choice")
    clearorsave = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.list.clear.or.save")
    randomlistpickname = TPClient.getActionDataValue(data.get("data"), "gitago.streamextras.plugin.act.list.choice")
    listclearname = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.list.clear")  
    listname = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.list.name")
    listformat = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.list.listsaveformat")     
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
            r = requests.get(f"https://decapi.me/twitch/game/{viewersname2}")
            Game = r.text
            TPClient.stateUpdate("gitago.streamextras.plugin.state.gametitle", Game)
    if data['actionId'] == "gitago.streamextras.plugin.act.get.youtubevideo":
                if choice3 == "Youtube Video":
                    r = requests.get(f"https://decapi.me/youtube/latest_video?id={youtubeid}")
                    urlcontent = r.text
                    ### Regex - this is everything after the -
                    uploadurl = re.search(r'(?<= - ).*', urlcontent)
                    ## Regex - this is everything before the - 
                    uploadtitle = re.search(r'.*(?= - )', urlcontent)
                    TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideourl", uploadurl.group(0))
                    TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideodescription", uploadtitle.group(0))
                    TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideofull", r.text)      

# Action 1 Data
    if data['actionId'] == "gitago.streamextras.plugin.act.get.game1":
            if choice2 == "Follower(s)":
                if count == "" or count == "0":
                    if ascdesc == "Descending":
                        print("ok its 0 or empty")
                        r = requests.get(f"https://decapi.me/twitch/followers?channel={viewersname2}&direction=desc")
                        TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)
                    if ascdesc == "Ascending":                     
                        r = requests.get(f"https://decapi.me/twitch/followers?channel={viewersname2}&direction=asc")
                        TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)
                            
                else:
                    if ascdesc =="Descending":
                        r = requests.get(f"https://decapi.me/twitch/followers?channel={viewersname2}&count={count}&num&separator=%20-%20&direction=desc")
                        TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)
                    if ascdesc =="Ascending":
                        r = requests.get(f"https://decapi.me/twitch/followers?channel={viewersname2}&count={count}&num&separator=%20-%20&direction=asc")
                        TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)
            #### dont know if im even using this below ?
            if choice2 == "Video(s)":
                if count == "" or count == "0":
                    r = requests.get((f"https://decapi.me/twitch/videos/{viewersname2}"))
              #      TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)
                else:
                    r = requests.get(f"https://decapi.me/twitch/videos/{viewersname2}?limit={count}&separator=%20-%20")
              #      TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)

            if choice2 == "Youtube Video":
                r = requests.get(f"https://decapi.me/youtube/latest_video?id={youtubeid}")
                urlcontent = r.text
                ## Regex Stuff - this is everything after the -
                uploadurl = re.search(r'(?<= - ).*', urlcontent)
                #Regex Stuff - this is everything before the - 
                uploadtitle = re.search(r'.*(?= - )', urlcontent)
                TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideourl", uploadurl.group(0))
                TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideodescription", uploadtitle.group(0))
                TPClient.stateUpdate("gitago.streamextras.plugin.state.youtubevideofull", r.text) 


# Action 2 Data
    if data['actionId'] == "gitago.streamextras.plugin.act.get.game2":
        if choice == "Game/Category":
                r = requests.get(f"https://decapi.me/twitch/game/{viewersname}")
                Game = r.text
                TPClient.stateUpdate("gitago.streamextras.plugin.state.gametitle", Game)

        if choice == "Status":
            r = requests.get(f"https://decapi.me/twitch/status/{viewersname}")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.channelstatus", r.text)
        
        if choice == "Avatar":
            r = requests.get(f"https://decapi.me/twitch/avatar/{viewersname}")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.avatarurl", r.text)
        
        if choice == "Follower Count":
            r = requests.get(f"https://decapi.me/twitch/followcount/{viewersname}")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.followerscount", r.text)

        if choice == "Highlights":
            r = requests.get(f"https://decapi.me/twitch/highlight/{viewersname}")
            stupidcheck = viewersname +" has no saved highlights."
            if r.text == stupidcheck:
                TPClient.stateUpdate("gitago.streamextras.plugin.state.highlight", "No Highlights Available")    
            else:
                TPClient.stateUpdate("gitago.streamextras.plugin.state.highlight", r.text)
        
        if choice == "Last Follower(s)":
            r = requests.get(f"https://decapi.me/twitch/followers?channel={viewersname}")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.recentchannelfollower", r.text)


        if choice == "Account Age":
            r = requests.get(f"https://decapi.me/twitch/accountage/{viewersname}")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.accountage", r.text)

        if choice == "Follow Age":
            r = requests.get(f"https://decapi.me/twitch/followage/{twitchid}/{viewersname}")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.followage", r.text)


        if choice == "Random User":
            r = requests.get(f"https://decapi.me/twitch/random_user/{viewersname.lower()}")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.randomuser", r.text)

        if choice == "Up-Time":
            r = requests.get(f"https://decapi.me/twitch/uptime/{viewersname}")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.uptime", r.text)

        if choice == "Viewer Count":
            r = requests.get(f"https://decapi.me/twitch/viewercount/{viewersname}")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.viewercount", r.text)

        if choice == "Total Views":
            r = requests.get(f"https://decapi.me/twitch/total_views/{viewersname}")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.totalviews", r.text)    

 ##########need to use regex to seperate this     #Its formatted like this...   TEC Season 2 Highlights  - https://www.twitch.tv/videos/876780091
        if choice == "Most Recent Upload":
            r = requests.get(f"https://decapi.me/twitch/upload/{viewersname}")
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
  

# Action 3 LISTS
    if data['actionId'] == "gitago.streamextras.plugin.act.random":
        if randomchoice == "Random User":
            r = requests.get(f"https://decapi.me/twitch/random_user/{twitchid.lower()}")
            TPClient.stateUpdate("gitago.streamextras.plugin.state.randompick", r.text)
 ### this below
    if data['actionId'] == "gitago.streamextras.plugin.act.list.pickrandom":
        if randomlistpickname == "Chatter List":
            randomlistpick("Chatter List")
        if randomlistpickname == "Giveaway List":
            randomlistpick("Giveaway List")
 ### LIST CLEAR AND SAVE ####  
    if data['actionId'] == "gitago.streamextras.plugin.act.clearlist":
        print(data)
        if clearorsave == "Clear" and listclearname == "Chatter List":
            print("clearing")
            clearlist(listclearname)
        if clearorsave == "Clear" and listclearname == "Giveaway List":
            clearlist(listclearname)


            
   # MAKE OPTION for save list by message order time, and or most message
        if clearorsave == "Save" and listclearname == "Chatter List":
            print(data)
            #num = 0
   ###open file and print table
            savelist('Chat List', listformat)

            
        if clearorsave == "Save" and listclearname == "Giveaway List":
           savelist('Giveaway List', listformat)

            
            
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
            
# 
# If adding to Chatter List
    if data['actionId'] == "gitago.streamextras.plugin.act.list":
        #can see about removing if listname, since checkchatter checks what list ?
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
            print(len(queue))
            switch('on')
        if queuechoice == "Pause":
            switch('pause')
            update_top_list()


### ON HOLD ACTIONS
@TPClient.on(TP.TYPES.onHold_down)
def holdAction(data):
    if data['actionId'] == "gitago.streamextras.plugin.act.random.hold":
        while TPClient.isActionBeingHeld("gitago.streamextras.plugin.act.random.hold"):
            time.sleep(.15)
            randomlistpick('Chatter List')
            print(data)

@TPClient.on(TP.TYPES.onHold_up)
def holdAction(data):
    if data['actionId'] == "gitago.streamextras.plugin.act.random.hold":
        print(data)



# Shutdown handler
@TPClient.on(TP.TYPES.onShutdown)
def onShutdown(data):
    print(data)


# Error handler
@TPClient.on(TP.TYPES.onError)
def onError(exc):
    print(exc)

TPClient.connect()
