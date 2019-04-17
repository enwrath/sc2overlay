#!!!!!!! Käynnistä vasta kun SC2 on käynnistynyt kokonaan!!!!!!!!!!

#Luo vihunmmr.txt tiedoston missä vihun tiedot ja päivittää sitä x sekunnin välein
#Lisää luotu tiedosto obsiin sourceksi. Päivittyy taianomaisesti!
#Normitilanteissa ei pitäisi kaatua! (normitilanteita ei esim. AI vastaan pelaaminen, arcade, yms yms.)


#!!!!
#Salli lähiverkossa olevien koneiden käyttää client apia
#Blizzard launcherissa sc2 sivulta: Options-Game settings-additional command line arguments- "-clientapi 6220" (ilman lainausmerkkejä)
#!!!!

import urllib.request, json, time, sys

###Omat tiedot näihin
playername = "Enwrath" 
sc2ip = "localhost" #Sen koneen ip jolla pelaat, esim cmd promptissa ipconfig
updateInterval = 10 #Kuinka monen sekunnin välein tarkistetaan josko olisi uusi peli




enemyname = ""
enemyindex = 0
oldenemy = ""
enemyrace = ""

#TODO: katso ollaanko pelissä vai ei ja päivitä statusta.
with open("vihunmmr.txt", "w") as f: 
    f.write("Waiting for next opponent.")
    
while True:
    print("Tarkistetaan onko vihua...")
    sys.stdout.flush()
    try:
        with urllib.request.urlopen("http://"+sc2ip+":6220/ui") as url:
            data = json.loads(url.read().decode())
            if len(data['activeScreens']) > 0:
                with open("vihunmmr.txt", "w") as f: 
                    f.write("Fuzer idlaa valikoissa")
            else:
                with urllib.request.urlopen("http://"+sc2ip+":6220/game") as url:
                    data = json.loads(url.read().decode())
                    if len(data['players']) == 2: #1v1 peli
                        enemyname = data['players'][0]['name']
                        enemyindex = 0
                        if enemyname == playername:
                            enemyname = data['players'][1]['name']
                            enemyindex = 1
                        enemyrace = data['players'][enemyindex]['race'][0]

                if enemyname != oldenemy:
                    oldenemy = enemyname
                    #En löytäny apia millä saa mmr, tämä kelvatkoon
                    rurl = "&race=terran"
                    if enemyrace == "P": rurl = "&race=protoss"
                    elif enemyrace == "Z": rurl = "&race=zerg"
                    elif enemyrace == "R": rurl = "&race=random"
                    with urllib.request.urlopen("http://sc2unmasked.com/Search?q="+enemyname+"&page=1&server=eu&results=1"+rurl) as url:
                        mmr = url.read().decode().split('<td class="align-right">')[1].split('<')[0]
                        print(enemyname + " [" + mmr + "MMR] " + enemyrace)
                        with open("vihunmmr.txt", "w") as f: 
                            f.write(enemyname + " [" + mmr + "MMR] " + enemyrace)
    except:
        print("Virhe.")
    time.sleep(updateInterval)
