#!/usr/bin/env python3
'''
Gitago's Stream Extras Plugin
'''

import sys
import TouchPortalAPI as TP
import requests
import re
import random
import time
# imports below are optional, to provide argument parsing and logging functionality
from argparse import ArgumentParser
from logging import (getLogger, Formatter, NullHandler, FileHandler, StreamHandler, DEBUG, INFO, WARNING)

__version__ = "1.2"

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
        'name': "Pick Random From, or Clear List",
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
    'Most Recent Video URL': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.uploadurl",
        'type': "text",
        'desc': "Recent Video - Upload URL",
        'default': ""
    },
    'Most Recent Video Title': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.uploadtitle",
        'type': "text",
        'desc': "Recent Video - Upload Title",
        'default': ""
    },
    'Youtube Video Full Info': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.youtubevideofull",
        'type': "text",
        'desc': "Youtube Video - Description + URL ",
        'default': ""
    },
    'Youtube Video URL': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.youtubevideourl",
        'type': "text",
        'desc': "Youtube Video - URL",
        'default': ""
    },
    'Youtube Video Description': {
        'category': "streamextras",
        'id': PLUGIN_ID + ".state.youtubevideodescription",
        'type': "text",
        'desc': "Youtube Video - Description",
        'default': ""
    },
    'New Chatter Status': {
        'category': "lists",
        'id': PLUGIN_ID + ".state.chatterlist.chatterstatus",
        'type': "text",
        'desc': "New Chatter Status",
        'default': "False"
    },
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
        'id': PLUGIN_ID + ".state.chatterlist.total",
        'type': "text",
        'desc': "Chatter List - Total",
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



# Create the Touch Portal API client.
try:
    TPClient = TP.Client(
        pluginId=PLUGIN_ID, 
        sleepPeriod=0.05,  # allow more time than default for other processes
        autoClose=True,  
        checkPluginId=True,  
        maxWorkers=4, 
        updateStatesOnBroadcast=False,  # do not spam TP with state updates on every page change
    )
except Exception as e:
    sys.exit(f"Could not create TP Client, exiting. Error was:\n{repr(e)}")
global totalchatterlist
global chatterlist
global giveawaylist #no idea if this global is needed
totalchatterlist = ""
twitchid = ""
youtubeid = ""
chatterlist = [""]
giveawaylist = [""]

def addname(chattername, listname):
    global totalchatterlist
    global chatterlist
    global giveawaylist
    if listname == "Chatter List":
        chatterlist.append(chattername)
        totalchatterlist = len(chatterlist)
        #subtracting -1 every time because of the BLANK entry in the chatterlist variable
        totalchatterlist -= 1
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chatterstatus", "TRUE")
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chattername", chattername)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.status", chattername + " added.")
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.total", str(totalchatterlist))
        time.sleep(0.5)
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chatterstatus", "FALSE")

##this is for the giveaway list
    if listname == "Giveaway List":       
        giveawaylist.append(chattername)
        totalgiveawaylist = len(giveawaylist)
        #subtracting -1 every time because of the BLANK entry in the giveawaylist variable
        totalgiveawaylist -= 1
        TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.status", chattername + " added.")
        TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.total", str(totalgiveawaylist))

def removename(chattername, listname):
    global chatterlist

    if listname =="Chatter List":
        if chattername in chatterlist:
            chatterlist.remove(chattername)
            totalchatterlist = len(chatterlist)
            totalchatterlist -= 1
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.total", str(totalchatterlist))
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.status", chattername + " removed from list")
            print("1 removed chatter list")

    if listname =="Giveaway List":
        if chattername in giveawaylist:
            giveawaylist.remove(chattername)
            totalgiveawaylist = len(giveawaylist)
            totalgiveawaylist -= 1
            TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.total", str(totalgiveawaylist))
            TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.status", chattername + " removed from list")
            print("1 removed from giveaway list")
        
def clearlist(listclearname):
    global totalchatterlist
    global totalgiveawaylist
    global chatterlist
    global giveawaylist
    print(listclearname)
    if listclearname == "Chatter List":
        print("Chatter List CLEARED")
        chatterlist = [""]
        totalchatterlist = "0"
        TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.total", "0")
    elif listclearname == "Giveaway List":
        print("Giveaway List CLEARED")
        giveawaylist = [""]
        totalgiveawaylist = "0"
        TPClient.stateUpdate("gitago.streamextras.plugin.state.giveawaylist.total", "0")

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
# TP Client event handler callbacks

# Initial connection handler
@TPClient.on(TP.TYPES.onConnect)
def onConnect(data):
    global twitchid
    global youtubeid
    twitchid = data['settings'][0]['Twitch ID']
    youtubeid = data['settings'][1]['Youtube ID']
    print("connected")
    


# Settings handler
@TPClient.on(TP.TYPES.onSettingUpdate)
def onSettingUpdate(data):
    global twitchid
    global youtubeid
    twitchid = data["values"][0]['Twitch ID']
    youtubeid = data["values"][1]['Youtube ID']
    


# Action handler
@TPClient.on(TP.TYPES.onAction)
def onAction(data):
    global twitchid
    global youtubeid
    clearorrandom = TPClient.getActionDataValue(data.get("data"),"gitago.streamextras.plugin.act.list.clear.or.random")
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
        print(data)
        if randomchoice == "Random User":
            url = ("https://decapi.me/twitch/" + "random_user" +"/" + twitchid.lower())
            r = requests.get(url)
            TPClient.stateUpdate("gitago.streamextras.plugin.state.randompick", r.text)


# If adding to Chatter List
    if data['actionId'] == "gitago.streamextras.plugin.act.list":
        if listname == "Chatter List" and addorremove == "Add" and chattername not in chatterlist:
            print("ok person wasnt in list")
            addname(chattername, listname)
        elif chattername in chatterlist:
            TPClient.stateUpdate("gitago.streamextras.plugin.state.chatterlist.chatterstatus", "FALSE")
## If removing from Chatter List
        if listname == "ChatterList" and addorremove == "Remove":
            removename(chattername, listname)
## If adding to Giveaway List
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



# Shutdown handler
@TPClient.on(TP.TYPES.onShutdown)
def onShutdown(data):
    print(data)


# Error handler
@TPClient.on(TP.TYPES.onError)
def onError(exc):
    print(exc)

#TPClient.connect()

