#!!!!!!! Käynnistä vasta kun SC2 on käynnistynyt kokonaan!!!!!!!!!!

#Luo vihunmmr.txt tiedoston missä vihun tiedot ja päivittää sitä x sekunnin välein
#Lisää luotu tiedosto obsiin sourceksi. Päivittyy taianomaisesti!
#Normitilanteissa ei pitäisi kaatua! (normitilanteita ei esim. AI vastaan pelaaminen, arcade, yms yms.)


#!!!!
#Salli lähiverkossa olevien koneiden käyttää client apia
#Blizzard launcherissa sc2 sivulta: Options-Game settings-additional command line arguments- "-clientapi 6119" (ilman lainausmerkkejä)
#!!!!

#See settings.py for user settings.

import urllib.request, json, time, sys, shutil
import settings as conf


#Non-setting variables
enemyname = ""
oldenemy = ""
enemyrace = ""
playermmr = ""
enemymmr = ""
ingame = False
playerrace = ""

def updateRaceImages():
    if playerrace == "T":
        shutil.copyfile("overlayimages/terran.png", "playerrace.png")
    elif playerrace == "P":
        shutil.copyfile("overlayimages/protoss.png", "playerrace.png")
    elif playerrace == "Z":
        shutil.copyfile("overlayimages/zerg.png", "playerrace.png")
    else:
        shutil.copyfile("overlayimages/random.png", "playerrace.png")

    if enemyrace == "T":
        shutil.copyfile("overlayimages/terran.png", "enemyrace.png")
    elif enemyrace == "P":
        shutil.copyfile("overlayimages/protoss.png", "enemyrace.png")
    elif enemyrace == "Z":
        shutil.copyfile("overlayimages/zerg.png", "enemyrace.png")
    else:
        shutil.copyfile("overlayimages/random.png", "enemyrace.png")

def emptyRaceImages():
    shutil.copyfile("overlayimages/empty.png", "playerrace.png")
    shutil.copyfile("overlayimages/empty.png", "enemyrace.png")

def updateOverlay():
    if ingame:
        with open("vihunmmr.txt", "w") as f:
            ename = enemyname[0:12].center(12)
            pname = conf.playername[0:12].center(12)
            overlaytext = "{} [{}MMR] vs {} [{}]".format(pname, playermmr, ename, enemymmr)
            f.write(overlaytext)
        updateRaceImages()
            
    else:
        with open("vihunmmr.txt", "w") as f: 
            f.write(conf.betweengamesmsg)
        emptyRaceImages()

def checkIngameStatus():
    global ingame
    try:
        with urllib.request.urlopen("http://{}:{}/ui".format(conf.sc2ip, conf.sc2port)) as url:
            data = json.loads(url.read().decode())
            if len(data['activeScreens']) > 0:
                ingame = False
            else:
                ingame = True
    except:
        print("SC2 is not running or cannot be connected to.")

def checkOpponent():
    global enemyrace, enemyname, playerrace
    try:
        with urllib.request.urlopen("http://{}:{}/game".format(conf.sc2ip, conf.sc2port)) as url:
            data = json.loads(url.read().decode())
            if len(data['players']) == 2: #1v1 game
                enemyname = data['players'][0]['name']
                enemyindex = 0
                playerrace = data['players'][1]['race'][0]
                if enemyname == conf.playername:
                    enemyname = data['players'][1]['name']
                    enemyindex = 1
                    playerrace = data['players'][0]['race'][0]
                enemyrace = data['players'][enemyindex]['race'][0]
    except:
        print("Some error lol")

#Rumor has it that MMR might be added to client api soon(tm)
#Super elegant work-around before future is here
def getOpponentMMR():
    global enemymmr
    try:
        rurl = "&race=terran"
        if enemyrace == "P": rurl = "&race=protoss"
        elif enemyrace == "Z": rurl = "&race=zerg"
        elif enemyrace == "R": rurl = "&race=random"
        with urllib.request.urlopen("http://sc2unmasked.com/Search?q="+enemyname+"&page=1&server=eu&results=25"+rurl) as url:
            d = url.read().decode()
            mmrs = []
            mmrcandidates = d.count('</td><td class="align-right win-ratio')
            data = d.split('</td><td class="align-right win-ratio')
            data.pop()
            for m in data:
                mmrs.append(int(m.split('<td class="align-right">')[-1]))

            #Choose mmr closest to player mmr
            enemymmr = min(mmrs, key=lambda x:abs(x-playermmr))
    except Exception as e:
        print("Error getting opponent mmr")
        print(str(e))

#TODO: Use Blizzard api since user can just input his own id.
def getOwnMMR():
    global playermmr
    try:
        #User probably has an unique name, right?
        with urllib.request.urlopen("http://sc2unmasked.com/Search?q="+conf.playername+"&page=1&server=eu&results=1") as url:
            playermmr = int(url.read().decode().split('<td class="align-right">')[1].split('<')[0])
    except:
        print("Error getting own mmr")

def updateData():
    global oldenemy
    checkIngameStatus()
    if ingame:
        checkOpponent()
    if oldenemy != enemyname:
        oldenemy = enemyname
        #New game has started.
        #Or if we find same player twice in a row sc2unmasked probably hasn't updated yet so no need to update mmr
        getOwnMMR()
        getOpponentMMR()
        
    updateOverlay()

def updateLoop():
    while True:
        updateData()
        time.sleep(conf.updateInterval)

updateLoop()