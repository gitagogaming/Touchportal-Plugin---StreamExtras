#!/usr/bin/env python3
'''
Touch Portal Plugin Example
'''

import sys
import TouchPortalAPI as TP
import requests
import re

# imports below are optional, to provide argument parsing and logging functionality
from argparse import ArgumentParser
from logging import (getLogger, Formatter, NullHandler, FileHandler, StreamHandler, DEBUG, INFO, WARNING)

# Version string of this plugin (in Python style).
__version__ = "1.0"

PLUGIN_ID = "gitago.decapi.plugin"

# Basic plugin metadata
TP_PLUGIN_INFO = {
    'sdk': 3,
    'version': int(float(__version__) * 1),  # TP only recognizes integer version numbers
    'name': "Decapi Stream Extras",
    'id': PLUGIN_ID,
    'configuration': {
        'colorDark': "#FF817E",
        'colorLight': "#676767",
    }
}   


# Setting(s) for this plugin. These could be either for users to
# set, or to persist data between plugin runs (as read-only settings).
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
    "decapi": {
        'id': PLUGIN_ID + ".decapi",
        'name': "Decapi - Stream Extras",
        'imagepath': "%TP_PLUGIN_FOLDER%Countdown Plugin/timer_git.png"
    }
}


TP_PLUGIN_ACTIONS = {

    'action2': {
        'category': "decapi",
        'id': PLUGIN_ID + ".act.get.game2",
        'name': "Twitch Extras",
        'prefix': TP_PLUGIN_CATEGORIES['decapi']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "Get {$gitago.decapi.plugin.act.get.choice$} for {$gitago.decapi.plugin.act.viewer.name$} ",
        'data': {
            'viewername': {
                'category': "decapi",
                'id': PLUGIN_ID + ".act.viewer.name",
                'type': "text",
                'label': "viewer name",
                'default': "",
            },
            'hours': {
                'category': "decapi",
                'id': PLUGIN_ID + ".act.get.choice",
                'type': "choice",
                'label': "Your Choice",
                'default': "",
                'valueChoices': ["Game/Category", "Avatar", "Follower Count", "Highlights", "Status", "Account Age", "Random User", "Up-Time", "Viewer Count", "Most Recent Upload", "Follow Age", "Total Views" ]
            },
#            'count': {
#                'id': PLUGIN_ID + ".act.count",
#                'type': "number",
#                'label': "Minutes",
#                'default': "0",
#                "minValue": 0,
#                "maxValue": 99,
#                'allowDecimals': False
#            },
        }
    },
    'action1': {
        'category': "decapi",
        'id': PLUGIN_ID + ".act.get.game1",
        'name': "Get (X) Followers [100 max]",
        'prefix': TP_PLUGIN_CATEGORIES['decapi']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "Retrieve {$gitago.decapi.plugin.act.get.count$} {$gitago.decapi.plugin.act.get.choice2$} for {$gitago.decapi.plugin.act.viewer.name2$} {$gitago.decapi.plugin.act.asc.desc$} ",
        'data': {
            'viewername': {
                'category': "decapi",
                'id': PLUGIN_ID + ".act.viewer.name2",
                'type': "text",
                'label': "viewer name",
                'default': "",
            },
            'hours': {
                'category': "decapi",
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
        'category': "decapi",
        'id': PLUGIN_ID + ".act.get.youtubevideo",
        'name': "Get Youtube Video URL + Description",
        'prefix': TP_PLUGIN_CATEGORIES['decapi']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "Retrieve {$gitago.decapi.plugin.act.get.choice3$} for {$gitago.decapi.plugin.act.viewer.name3$} ",
        'data': {
            'viewername': {
                'category': "decapi",
                'id': PLUGIN_ID + ".act.viewer.name3",
                'type': "text",
                'label': "viewer name",
                'default': "",
            },
            'hours': {
                'category': "decapi",
                'id': PLUGIN_ID + ".act.get.choice3",
                'type': "choice",
                'label': "See Multiple Followers or Videos",
                'default': "Youtube Video",
                'valueChoices': [ "Youtube Video" ]
            },
            'count': {
                'id': PLUGIN_ID + ".act.get.count",
                'type': "number",
                'label': "count",
                'default': "0",
                "minValue": 0,
                "maxValue": 99,
                'allowDecimals': False
            },
        } 
    },
    'action3': {
        'category': "decapi",
        'id': PLUGIN_ID + ".act.random",
        'name': "Pick Random",
        'prefix': TP_PLUGIN_CATEGORIES['decapi']['name'],
        'type': "communicate",
        "tryInline": True,
        'format': "Get Random {$gitago.decapi.plugin.act.get.randomchoice$}",
        'data': {
            'randomchoice': {
            'category': "decapi",
            'id': PLUGIN_ID + ".act.get.randomchoice",
            'type': "choice",
            'label': "Your Choice",
            'default': "",
            'valueChoices': ["Random User"]
            },
        }
    },
}

# Plugin static or dynamic state(s). 
TP_PLUGIN_STATES = {
    'recentfollowers': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.recentchannelfollower",
        'type': "text",
        'desc': "Channel's Recent Follower(s)",
        'default': ""
    },
        'highlights': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.highlight",
        'type': "text",
        'desc': "Channel's Highlights URL",
        'default': ""
    },
        'viewer_game': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.gametitle",
        'type': "text",
        'desc': "User - Last Game/Category Streamed",
        'default': ""
    },
        'channel_status': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.channelstatus",
        'type': "text",
        'desc': "User - Channel Description",
        'default': ""
    },
        'avatar_URL': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.avatarurl",
        'type': "text",
        'desc': "User - Avatar URL",
        'default': ""
    },
        'followercount': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.followerscount",
        'type': "text",
        'desc': "User - Follower Count",
        'default': ""
    },
        'viewercount': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.viewercount",
        'type': "text",
        'desc': "User - Viewer Count",
        'default': ""
    },
        'totalviews': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.totalviews",
        'type': "text",
        'desc': "User - Total Channel Views",
        'default': ""
    },
    'creationdate': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.accountage",
        'type': "text",
        'desc': "User - Created Date",
        'default': ""
    },
    'Follow Age': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.followage",
        'type': "text",
        'desc': "User - Follow Age",
        'default': ""
    },
        'randompick': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.randompick",
        'type': "text",
        'desc': "Random - Pick",
        'default': ""
    },
    'randomuser': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.randomuser",
        'type': "text",
        'desc': "Random - Active User Selection",
        'default': ""
    },
    'recentupload': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.recentupload",
        'type': "text",
        'desc': "Recent - Upload Full Details ",
        'default': ""
    },
    'Most Recent Video URL': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.uploadurl",
        'type': "text",
        'desc': "Recent Video - Upload URL",
        'default': ""
    },
    'Most Recent Video Title': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.uploadtitle",
        'type': "text",
        'desc': "Recent Video - Upload Title",
        'default': ""
    },
    'Youtube Video Full Info': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.youtubevideofull",
        'type': "text",
        'desc': "Youtube Video - Description + URL ",
        'default': ""
    },
    'Youtube Video URL': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.youtubevideourl",
        'type': "text",
        'desc': "Youtube Video - URL",
        'default': ""
    },
    'Youtube Video Description': {
        'category': "decapi",
        'id': PLUGIN_ID + ".state.youtubevideodescription",
        'type': "text",
        'desc': "Youtube Video - Description",
        'default': ""
    },
}

# Plugin Event(s).
TP_PLUGIN_EVENTS = {}

##
## End Python SDK declarations


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


twitchid = ""
youtubeid = ""

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
    ascdesc = TPClient.getActionDataValue(data.get("data"), "gitago.decapi.plugin.act.asc.desc")
    viewersname = TPClient.getActionDataValue(data.get("data"), "gitago.decapi.plugin.act.viewer.name")
    viewersname2 = TPClient.getActionDataValue(data.get("data"), "gitago.decapi.plugin.act.viewer.name2")
    count = TPClient.getActionDataValue(data.get("data"), "gitago.decapi.plugin.act.get.count")
    choice = TPClient.getActionDataValue(data.get("data"), "gitago.decapi.plugin.act.get.choice")
    choice2 = TPClient.getActionDataValue(data.get("data"), "gitago.decapi.plugin.act.get.choice2")
    choice3 = TPClient.getActionDataValue(data.get("data"), "gitago.decapi.plugin.act.get.choice3")
    randomchoice = TPClient.getActionDataValue(data.get("data"), "gitago.decapi.plugin.act.get.randomchoice")
    number = TPClient.getActionDataValue(data.get("data"), "gitago.decapi.plugin.act.number")
    if data['actionId'] == "gitago.decapi.plugin.act.get.game":
            url = ("https://decapi.me/twitch/game/" + viewersname2)
            r = requests.get(url)
            Game = r.text
            TPClient.stateUpdate("gitago.decapi.plugin.state.gametitle", Game)
    
    if data['actionId'] == "gitago.decapi.plugin.act.get.youtubevideo":
                if choice3 == "Youtube Video":
                    print(data)
                    url = ("https://decapi.me/youtube/" + "latest_video" +"?id=" + youtubeid)
                    r = requests.get(url)
                    urlcontent = r.text
                    #this is everything after the -
                    uploadurl = re.search(r'(?<= - ).*', urlcontent)
                    #this is everything before the - 
                    uploadtitle = re.search(r'.*(?= - )', urlcontent)
                    TPClient.stateUpdate("gitago.decapi.plugin.state.youtubevideourl", uploadurl.group(0))
                    TPClient.stateUpdate("gitago.decapi.plugin.state.youtubevideodescription", uploadtitle.group(0))
                    TPClient.stateUpdate("gitago.decapi.plugin.state.youtubevideofull", r.text)      

# Action 1 Stuff
    if data['actionId'] == "gitago.decapi.plugin.act.get.game1":
            if choice2 == "Follower(s)":
                if count == "" or count == "0":
                    if ascdesc == "Descending":
                        print("ok its 0 or empty")
                        url = ("https://decapi.me/twitch/" + "followers" +"?channel=" + viewersname2 + "&direction=desc")
                        r = requests.get(url)
                        TPClient.stateUpdate("gitago.decapi.plugin.state.recentchannelfollower", r.text)
                    if ascdesc == "Ascending":                     
                        url = ("https://decapi.me/twitch/" + "followers" +"?channel=" + viewersname2 + "&direction=asc")
                        r = requests.get(url)
                        TPClient.stateUpdate("gitago.decapi.plugin.state.recentchannelfollower", r.text)
                            
                else:
                    if ascdesc =="Descending":
                        url = ("https://decapi.me/twitch/" + "followers" +"?channel=" + viewersname2 +"&count=" + count + "&num&separator=%20-%20" + "&direction=desc")
                        r = requests.get(url)
                        TPClient.stateUpdate("gitago.decapi.plugin.state.recentchannelfollower", r.text)
                    if ascdesc =="Ascending":
                        url = ("https://decapi.me/twitch/" + "followers" +"?channel=" + viewersname2 +"&count=" + count + "&num&separator=%20-%20" + "&direction=asc")
                        r = requests.get(url)
                        TPClient.stateUpdate("gitago.decapi.plugin.state.recentchannelfollower", r.text)

            if choice2 == "Video(s)":
                if count == "" or count == "0":
                    url = ("https://decapi.me/twitch/" +"videos/" + viewersname2)
                    r = requests.get(url)
#                    TPClient.stateUpdate("gitago.decapi.plugin.state.recentchannelfollower", r.text)
                    print(url)
                else:
                    url = ("https://decapi.me/twitch/" +"videos/" + viewersname2 + "?limit=" + count +"&separator=%20-%20")
                    r = requests.get(url)
#                    TPClient.stateUpdate("gitago.decapi.plugin.state.recentchannelfollower", r.text)
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
                TPClient.stateUpdate("gitago.decapi.plugin.state.youtubevideourl", uploadurl.group(0))
                TPClient.stateUpdate("gitago.decapi.plugin.state.youtubevideodescription", uploadtitle.group(0))
                TPClient.stateUpdate("gitago.decapi.plugin.state.youtubevideofull", r.text) 
                print(uploadtitle.group(0))
                print(uploadurl.group(0))



# Action 2 Stuff
    if data['actionId'] == "gitago.decapi.plugin.act.get.game2":
        if choice == "Game/Category":
                url = ("https://decapi.me/twitch/" + "game" +"/" + viewersname)
                r = requests.get(url)
                Game = r.text
                print (Game)
                TPClient.stateUpdate("gitago.decapi.plugin.state.gametitle", Game)

        if choice == "Status":
            url = ("https://decapi.me/twitch/" + "status" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.decapi.plugin.state.channelstatus", r.text)
        
        if choice == "Avatar":
            url = ("https://decapi.me/twitch/" + "avatar" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.decapi.plugin.state.avatarurl", r.text)
        
        if choice == "Follower Count":
            url = ("https://decapi.me/twitch/" + "followcount" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.decapi.plugin.state.followerscount", r.text)

        if choice == "Highlights":
            url = ("https://decapi.me/twitch/" + "highlight" +"/" + viewersname)
            r = requests.get(url)
            stupidcheck = viewersname +" has no saved highlights."
            if r.text == stupidcheck:
                TPClient.stateUpdate("gitago.decapi.plugin.state.highlight", "No Highlights Available")    
            else:
                TPClient.stateUpdate("gitago.decapi.plugin.state.highlight", r.text)
        
        if choice == "Last Follower(s)":
            url = ("https://decapi.me/twitch/" + "followers" +"?channel=" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.decapi.plugin.state.recentchannelfollower", r.text)


        if choice == "Account Age":
            url = ("https://decapi.me/twitch/" + "accountage" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.decapi.plugin.state.accountage", r.text)

        if choice == "Follow Age":
            url = ("https://decapi.me/twitch/" + "followage" +"/" + twitchid + "/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.decapi.plugin.state.followage", r.text)


        if choice == "Random User":
            url = ("https://decapi.me/twitch/" + "random_user" +"/" + viewersname.lower())
            r = requests.get(url)
            TPClient.stateUpdate("gitago.decapi.plugin.state.randomuser", r.text)

        if choice == "Up-Time":
            url = ("https://decapi.me/twitch/" + "uptime" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.decapi.plugin.state.uptime", r.text)

        if choice == "Viewer Count":
            url = ("https://decapi.me/twitch/" + "viewercount" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.decapi.plugin.state.viewercount", r.text)

        if choice == "Total Views":
            url = ("https://decapi.me/twitch/" + "total_views" +"/" + viewersname)
            r = requests.get(url)
            TPClient.stateUpdate("gitago.decapi.plugin.state.totalviews", r.text)    

###########need to use regex to seperate this     #Its formatted like this...   TEC Season 2 Highlights  - https://www.twitch.tv/videos/876780091
        if choice == "Most Recent Upload":
            url = ("https://decapi.me/twitch/" + "upload" +"/" + viewersname)
            r = requests.get(url)
            urlcontent = r.text
            if r.text == viewersname + " has no uploaded videos.":
                TPClient.stateUpdate("gitago.decapi.plugin.state.uploadurl", r.text)
                TPClient.stateUpdate("gitago.decapi.plugin.state.uploadtitle", r.text)
                TPClient.stateUpdate("gitago.decapi.plugin.state.recentupload", r.text) 
            else:
                #this is everything after the -
                uploadurl = re.search(r'(?<= - ).*', urlcontent)
                #this is everything before the - 
                uploadtitle = re.search(r'.*(?= - )', urlcontent)
                TPClient.stateUpdate("gitago.decapi.plugin.state.uploadurl", uploadurl.group(0))
                TPClient.stateUpdate("gitago.decapi.plugin.state.uploadtitle", uploadtitle.group(0))
                TPClient.stateUpdate("gitago.decapi.plugin.state.recentupload", r.text)     
  

# Action 3 Stuff
    if data['actionId'] == "gitago.decapi.plugin.act.random":
        print(data)
        if randomchoice == "Random User":
            url = ("https://decapi.me/twitch/" + "random_user" +"/" + twitchid.lower())
            r = requests.get(url)
            TPClient.stateUpdate("gitago.decapi.plugin.state.randompick", r.text)


# Shutdown handler
@TPClient.on(TP.TYPES.onShutdown)
def onShutdown(data):
    print(data)


# Error handler
@TPClient.on(TP.TYPES.onError)
def onError(exc):
    print(exc)


#TPClient.connect()

