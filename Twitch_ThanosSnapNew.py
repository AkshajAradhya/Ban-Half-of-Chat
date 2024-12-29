# Original Written by DougDoug and DDarknut
# Current iteration written by Me

# Hello! This file contains the main logic to process Twitch chat and convert it to game commands.
# The code is written in Python 3.X
# There are 2 other files needed to run this code:
    # TwitchPlays_KeyCodes.py contains the key codes and functions to press keys in-game. You should not modify this file.
    # TwitchPlays_Connection.py is the code that actually connects to Twitch. You should not modify this file.

# The source code primarily comes from:
    # Wituz's "Twitch Plays" tutorial: http://www.wituz.com/make-your-own-twitch-plays-stream.html
    # PythonProgramming's "Python Plays GTA V" tutorial: https://pythonprogramming.net/direct-input-game-python-plays-gta-v/
    # DDarknut's message queue and updates to the Twitch networking code

# Disclaimer: 
    # This code is NOT intended to be professionally optimized or organized.
    # We created a simple version that works well for livestreaming, and I'm sharing it for educational purposes.

##########################################################

TWITCH_CHANNEL = 'name here' # Replace this with your Twitch username. Must be all lowercase.    ###EDIT THIS LINE

##########################################################
import keyboard
import TwitchPlays_Connection
import pydirectinput
import random
import pyautogui
import time
import concurrent.futures
from pynput.keyboard import Key, Controller
from TwitchPlays_KeyCodes import *

##########################################################

# MESSAGE_RATE controls how fast we process incoming Twitch Chat messages. It's the number of seconds it will take to handle all messages in the queue.
# This is used because Twitch delivers messages in "batches", rather than one at a time. So we process the messages over MESSAGE_RATE duration, rather than processing the entire batch at once.
# A smaller number means we go through the message queue faster, but we will run out of messages faster and activity might "stagnate" while waiting for a new batch. 
# A higher number means we go through the queue slower, and messages are more evenly spread out, but delay from the viewers' perspective is higher.
# You can set this to 0 to disable the queue and handle all messages immediately. However, then the wait before another "batch" of messages is more noticeable.
MESSAGE_RATE = 0.5
# MAX_QUEUE_LENGTH limits the number of commands that will be processed in a given "batch" of messages. 
# e.g. if you get a batch of 50 messages, you can choose to only process the first 10 of them and ignore the others.
# This is helpful for games where too many inputs at once can actually hinder the gameplay.
# Setting to ~50 is good for total chaos, ~5-10 is good for 2D platformers
MAX_QUEUE_LENGTH = 50 
MAX_WORKERS = 100 # Maximum number of threads you can process at a time 


# global variables for this script    
listOfChatters = []
numOfChatters = 0
numOfModsBanned= 0
numOfVIPsBanned = 0
chattersBanned = 0;
chattersUnBanned = 0;
modsUnBanned = 0;
VIPsUnBanned = 0;
takeNames = True;       # All lines with takeNames are an April change
#List of mods in your chat. This is here so you can auto re-mod people post snap 
listOfMods = ['nightbot']; #add all mods here, so that they dont lose mod status      ****EDIT THIS LINE***

#List of VIPs in your chat. This is here so you can auto re-VIP people post snap 
listOfVIPs = ['name 2']; #add all VIPs here, so that they dont lose VIP status             ****EDIT THIS LINE***

#List of mods in your chat about to get banned
listOfModsBeingBanned = []; 

#List of VIPs in your chat about to get banned
listOfVIPsBeingBanned = []; 

peopleBanned = [];


last_time = time.time()
message_queue = []
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
active_tasks = []
pyautogui.FAILSAFE = False

##########################################################

# An optional count down before starting, so you have time to load up the game
countdown = 3
while countdown > 0:
    print(countdown)
    countdown -= 1
    time.sleep(1)

t = TwitchPlays_Connection.Twitch();
t.twitch_connect(TWITCH_CHANNEL);

def handle_message(message):
    try:
        msg = message['message'].lower()
        username = message['username'].lower()

        global listOfMods;
        global listOfVIPs;             
        global listOfChatters;
        global listOfModsBeingBanned;
        global listOfVIPsBeingBanned;
        global numOfChatters;
        global numOfModsBanned;
        global numOfVIPsBanned;
        global chattersBanned;
        global chattersUnBanned;
        global modsUnBanned;
        global VIPsUnBanned;
        global takeNames;
        global peopleBanned;
        keyboard = Controller()

        # lets you view who is sending each message, set displayMessage to true if you want to see this
        displayMessage = False;
        if displayMessage == True:
            print("Got the message: [" + msg + "] from user [" + username + "]")

        ###################################
        # Code Section for saving names to a list
        ###################################

        #checks if username has been chatting and adds their name to the list
        def tally():
            global listOfMods;
            global listOfVIPs;             
            global listOfChatters;
            global listOfModsBeingBanned;
            global listOfVIPsBeingBanned;
            global numOfChatters;
            global numOfModsBanned;
            global numOfVIPsBanned;
            global chattersBanned;
            global chattersUnBanned;
            global modsUnBanned;
            global VIPsUnBanned;
            global takeNames;
            global peopleBanned;
            if username not in listOfChatters:
                if takeNames == True:
                    listOfChatters.append(username);
                    print("Good luck " + username)                  # *** EDIT THIS LINE ***
                    numOfChatters = numOfChatters + 1
                    print(numOfChatters)                            # *** EDIT THIS LINE ***
            else:
                print(numOfChatters)                            # *** EDIT THIS LINE ***
        
        ###################################
        # Code Section for comparing list of chatters to list of vips and mods
        ###################################

        def names():
            global listOfMods;
            global listOfVIPs;             
            global listOfChatters;
            global listOfModsBeingBanned;
            global listOfVIPsBeingBanned;
            global numOfChatters;
            global numOfModsBanned;
            global numOfVIPsBanned;
            global chattersBanned;
            global chattersUnBanned;
            global modsUnBanned;
            global VIPsUnBanned;
            global takeNames;
            global peopleBanned;
            def matchElements(list_a, list_b):
                match = []
                for i in list_a:
                    if i in list_b:
                        match.append(i)
                return match
       
            match = matchElements(listOfMods, listOfChatters)
            listOfModsBeingBanned = match;
            numOfModsBanned = len(match)
            #print("Mods Getting Banned: ", listOfModsBeingBanned, numOfModsBanned)

            match = matchElements(listOfVIPs, listOfChatters)
            listOfVIPsBeingBanned = match;
            numOfVIPsBanned = len(match)
            #print("VIPs Getting Banned: ", listOfVIPsBeingBanned, numOfVIPsBanned)

        ###################################
        # Code Section for Snap
        ####################################

        tally()
        if msg == "snap" and username == TWITCH_CHANNEL:         # *** EDIT THIS LINE ***
            takeNames = False;
            print("I am Inevitable")
            #tally()
            names()

            numberOfPeopleGettingBanned = 0
            numberOfPeopleGettingBanned = int(numOfChatters/2)
            peopleBanned = random.sample(listOfChatters, numberOfPeopleGettingBanned)
            print(peopleBanned)

            def matchElements(list_a, list_b):
                match = []
                for i in list_a:
                    if i in list_b:
                        match.append(i)
                return match

            match = matchElements(listOfVIPs, peopleBanned)
            vipSnapped = match
            numvipSnapped = len(vipSnapped)
            print("VIPs Getting Banned: ", vipSnapped, numvipSnapped)

            match = matchElements(listOfMods, peopleBanned)
            modSnapped = match
            #peopleBanned.remove(modSnapped)
            numModSnapped = len(modSnapped)
            print("Mods That would be banned: ", modSnapped, numModSnapped)

           # code to ban everyone
            while chattersBanned < numberOfPeopleGettingBanned:
                time.sleep(1)
                text = "/ban " + peopleBanned[chattersBanned-1]
                keyboard.type(text)
                HoldAndReleaseKey(ENTER, 0.1)
                chattersBanned = chattersBanned + 1;

           # code to unban everyone    
            time.sleep(60) ###how long the ban lasts
            while chattersUnBanned < numberOfPeopleGettingBanned:
                text = "/unban " + peopleBanned[chattersUnBanned-1]
                keyboard.type(text)
                HoldAndReleaseKey(ENTER, 0.1)
                chattersUnBanned = chattersUnBanned + 1;
            # re-mod
            time.sleep(10) ###delay between unbans and remods to ensure remod occurs
            while modsUnBanned < numModSnapped:
                reinstate = "/mod " + modSnapped[modsUnBanned-1]
                keyboard.type(reinstate)
                HoldAndReleaseKey(ENTER, 0.1)
                modsUnBanned = modsUnBanned + 1;
           # re-vip
            time.sleep(10) ###delay between unbans and remods to ensure revip occurs
            while VIPsUnBanned < numvipSnapped:
                reinstate = "/vip " + vipSnapped[VIPsUnBanned-1]
                keyboard.type(reinstate)
                HoldAndReleaseKey(ENTER, 0.1)
                VIPsUnBanned = VIPsUnBanned + 1;      

        ####################################
        ####################################

    except Exception as e:
        print("Encountered exception: " + str(e))


while True:

    active_tasks = [t for t in active_tasks if not t.done()]

    #Check for new messages
    new_messages = t.twitch_receive_messages();
    if new_messages:
        message_queue += new_messages; # New messages are added to the back of the queue
        message_queue = message_queue[-MAX_QUEUE_LENGTH:] # Shorten the queue to only the most recent X messages

    messages_to_handle = []
    if not message_queue:
        # No messages in the queue
        last_time = time.time()
    else:
        # Determine how many messages we should handle now
        r = 1 if MESSAGE_RATE == 0 else (time.time() - last_time) / MESSAGE_RATE
        n = int(r * len(message_queue))
        if n > 0:
            # Pop the messages we want off the front of the queue
            messages_to_handle = message_queue[0:n]
            del message_queue[0:n]
            last_time = time.time();

    # If user presses Shift+Backspace, automatically end the program
    if keyboard.is_pressed('shift+backspace'):
        exit()

    if not messages_to_handle:
        continue
    else:
        for message in messages_to_handle:
            if len(active_tasks) <= MAX_WORKERS:
                active_tasks.append(thread_pool.submit(handle_message, message))
            else:
                print(f'WARNING: active tasks ({len(active_tasks)}) exceeds number of workers ({MAX_WORKERS}). ({len(message_queue)} messages in the queue)')
