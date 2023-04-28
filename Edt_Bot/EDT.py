import requests
from datetime import datetime, date
import icalendar
import telebot

chan_id = <ID_telegram_channel>
API_TOKEN = <Telegram_token>
bot = telebot.TeleBot(API_TOKEN)

def parse(texte):
    retour = ''
    i = 0
    while i < len(texte):
        if texte[i] == "\\" and i < len(texte)-1 and texte[i+1] in ['n','u','U']:
            retour += texte[i]
        elif texte[i] == "\\" and i < len(texte)+1 and texte[i+1] in ['~']:
            retour += texte[i+1]
            i += 1
        elif i < len(texte)-2 and texte[i:i+2] in ['__']:
            retour += texte[i:i+2]
            i += 1
        elif texte[i] in ['_', '*', '[', ']', '(', ')', '`', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
            retour += '\\'+texte[i]
        else:
            retour += texte[i]
        i += 1
    return retour


class Élève:
    def __init__(self, Élève):
        self.nom = Élève[1]
        self.prenom = Élève[0]

    def toString(self):
        return "élève " + self.prenom + self.nom

class Time:
    def __init__(self, heure):
        self.heure = heure

    def toString(self):
        return (self.heure + (datetime.now() - datetime.utcnow())).strftime('%H:%M')

    def compac(self):
        return self.heure.strftime('%H%M')


class Cours:
    def __init__(self, prof, matiere, salle, dheure, fheure):
        self.prof = prof
        self.matiere = matiere
        self.salle = salle
        self.debut = Time(dheure)
        self.fin = Time(fheure)

    def before(self, autre):
        return self.debut.compac() < autre.debut.compac()

    def toString(self):
        return f"{self.matiere} en {','.join(self.salle)} avec {self.prof} de {self.debut.toString()} à {self.fin.toString()}"

    def toMD(self):
        return f"__{self.matiere}__\n\U0001f552{self.debut.toString()} - {self.fin.toString()}\n\U0001f468\u200d\U0001f3eb{self.prof}\n\U0001f4cd{', '.join(self.salle)}"

class Journée:
    def __init__(self):
        self.cours = []

    def addCours(self, cours):
        self.cours.append(cours)

    def sort(self):
        sortie = []
        for e in self.cours:
            i = 0
            while i < len(sortie) and sortie[i].before(e):
                i += 1
            sortie.insert(i, e)
        self.cours = sortie

    def toString(self):
        sortie = ""
        for e in self.cours:
            sortie += e.toString() + "\n"
        return sortie

    def toMD(self):
        sortie = ""
        for e in self.cours:
            sortie += e.toMD() + "\n\n"
        return sortie

class Cal:
    def __init__(self, cal):
        self.Élève = Élève(str(cal['X-WR-CALNAME']).split('-')[1].split()[-3::-1])
        self.ical = cal

    def findToday(self):
        ajd = date.today()
        journée = Journée()
        for event in self.ical.walk('VEVENT'):
            start = event.get('dtstart')
            try:
                if start.dt.date() == ajd:
                    cours = event.get("summary").split(' - ')
                    prof = cours[2].strip()
                    matiere = " ".join(cours[1].split()[1:])
                    salle = [line.split()[0] for line in event.get("location").split(',')]
                    dheure = event.get('dtstart').dt
                    fheure = event.get('dtend').dt

                    journée.addCours(Cours(prof, matiere, salle, dheure, fheure))
            except:
                pass


        journée.sort()
        return journée

    def dayToString(self):
        retour = f"Bonjour {self.Élève.prenom}, aujourd'hui tu as les cours suivants :\n"
        retour += self.findToday().toString()
        return retour

    def dayToMD(self):
        retour = f"Bonjour {self.Élève.prenom}, aujourd'hui tu as les cours suivants :\n\n"
        retour += self.findToday().toMD()
        return parse(retour)


url = <ICAL_URL>
response = requests.get(url)
calendrier = Cal(icalendar.Calendar.from_ical(response.text))
print(calendrier.dayToString())
bot.send_message(chan_id,calendrier.dayToMD(),parse_mode="MarkdownV2")
