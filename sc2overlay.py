#!!!!!!! Käynnistä vasta kun SC2 on käynnistynyt kokonaan!!!!!!!!!!

#Luo vihunmmr.txt tiedoston missä vihun tiedot ja päivittää sitä x sekunnin välein
#Lisää luotu tiedosto obsiin sourceksi. Päivittyy taianomaisesti!
#Normitilanteissa ei pitäisi kaatua! (normitilanteita ei esim. AI vastaan pelaaminen, arcade, yms yms.)


#!!!!
#Salli lähiverkossa olevien koneiden käyttää client apia
#Blizzard launcherissa sc2 sivulta: Options-Game settings-additional command line arguments- "-clientapi 6119" (ilman lainausmerkkejä)
#!!!!

import urllib.request, json, time, sys, shutil

#Things to move to settings file
playername = "Enwrath" 
sc2ip = "localhost" #Sen koneen ip jolla pelaat, esim cmd promptissa ipconfig
sc2port = 6220 #Change to default for default conf. Is it 6119?
updateInterval = 10 #Kuinka monen sekunnin välein tarkistetaan josko olisi uusi peli
betweengamesmsg = "Vuotetaan seuraavaa vihua"





#Non-setting variables
enemyname = ""
enemyindex = 0
oldenemy = ""
enemyrace = ""
playermmr = ""
enemymmr = ""
ingame = 0
playerrace = ""

def updateRaceImages():
    if playerrace == 'T':
        shutil.copyfile("overlayimages/terran.png", "playerrace.png")
    elif playerrace == 'P':
        shutil.copyfile("overlayimages/protoss.png", "playerrace.png")
    elif playerrace == 'Z':
        shutil.copyfile("overlayimages/protoss.png", "playerrace.png")
    else:
        shutil.copyfile("overlayimages/random.png", "playerrace.png")

    if enemyrace == 'T':
        shutil.copyfile("overlayimages/terran.png", "enemyrace.png")
    elif enemyrace == 'P':
        shutil.copyfile("overlayimages/protoss.png", "enemyrace.png")
    elif enemyrace == 'Z':
        shutil.copyfile("overlayimages/protoss.png", "enemyrace.png")
    else:
        shutil.copyfile("overlayimages/random.png", "enemyrace.png")

def emptyRaceImages():
    shutil.copyfile("overlayimages/empty.png", "playerrace.png")
    shutil.copyfile("overlayimages/empty.png", "enemyrace.png")

def updateOverlay():
    if ingame:
        with open("vihunmmr.txt", "w") as f:
            overlaytext = "{} [{}MMR] vs {} [{}] {}".format(playername, playermmr, enemyname, enemymmr, enemyrace)
            f.write(overlaytext)
        updateRaceImages()
            
    else:
        with open("vihunmmr.txt", "w") as f: 
            f.write(betweengamesmsg)
        emptyRaceImages()

def checkIngameStatus:
    try:
        with urllib.request.urlopen("http://"+sc2ip+":"+sc2port+"/ui") as url:
            data = json.loads(url.read().decode())
            if len(data['activeScreens']) > 0:
                ingame = False
            else:
                ingame = True
    except:
        print("SC2 is not running or cannot be connected to.")

def checkOpponent():
    try:
        with urllib.request.urlopen("http://"+sc2ip+":"+sc2port+"/game") as url:
            data = json.loads(url.read().decode())
            if len(data['players']) == 2: #1v1 game
                enemyname = data['players'][0]['name']
                enemyindex = 0
                playerrace = data['players'][1]['race'][0]
                if enemyname == playername:
                    enemyname = data['players'][1]['name']
                    enemyindex = 1
                    playerrace = data['players'][0]['race'][0]
                enemyrace = data['players'][enemyindex]['race'][0]
    except:
        print("Some error lol")

#Rumor has it that MMR might be added to client api soon(tm)
#Super elegant work-around before future is here
def getOpponentMMR():
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
            mmr = min(mmrs, key=lambda x:abs(x-playermmr))
    except:
        print("Error getting opponent mmr")

#TODO: Use Blizzard api since user can just input his own id.
def getOwnMMR():
    try:
        #User probably has an unique name, right?
        with urllib.request.urlopen("http://sc2unmasked.com/Search?q="+playername+"&page=1&server=eu&results=1") as url:
        playermmr = url.read().decode().split('<td class="align-right">')[1].split('<')[0]
    except:
        print("Error getting own mmr")

def updateData:
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
        time.sleep(updateInterval)

updateLoop()