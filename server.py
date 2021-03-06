from bottle import route, run
import sqlite3
import math
import re

class Distance:
    def __init__(self, string):
        data = re.split(":", string)
        self.latitude = float(data[0])
        self.longitude = float(data[1])
        pass

    def distance(self, other):
        return math.fabs(self.latitude - other.latitude) + math.fabs(self.longitude - other.longitude)
    pass

@route("/danger/<user>")
def danger(user):
    database = sqlite3.connect('bdd.db')
    cursor = database.cursor()
    userdata = cursor.execute("SELECT Users.id, Geolocalizations.latitude, Geolocalizations.longitude FROM Users INNER JOIN Geolocalizations ON Geolocalizations.id = Users.Geolocalizations_id").fetchone()
    userpos = Distance(str(userdata[1])+":"+str(userdata[2]))
    events = cursor.execute("SELECT Events.id, Events.date, Events.name, Geolocalizations.latitude as latitude, Geolocalizations.longitude as longitude FROM Events INNER JOIN Geolocalizations ON Geolocalizations.id = Events.Geolocalizations_id").fetchall()
    results = []
    for event in events:
        #calcul de la distance entre l'emplacement de l'user et l'event
        eventpos = Distance(str(event[3]) + ":" +str(event[4]))
        if userpos.distance(eventpos) < 1.30:
            warns = cursor.execute("SELECT Warns.id, Warns.Events_id FROM Warns WHERE Warns.Users_id = "+user).fetchall()
            found = False
            for warn in warns:
                if event[0] == warn[1]:
                    found = True
                    break
            if found == False:
                results.append(event)
    database.close()
    return dict(events = results)

@route("/response/<user>/<value>")
def response(user, value):
    database = sqlite3.connect('bdd.db')
    cursor = database.cursor()
    request = "UPDATE Users SET "
    if value == "wounded":
        request = request + "is_wounded"
    elif value == "danger":
        request = request + "is_in_danger"
    request = request + " = '1' WHERE Users.id = '"+user+"'"
    print request
    cursor.execute(request)
    database.commit()
    database.close()
    return dict(state = "ok")

@route("/victims")
def victims():
    database = sqlite3.connect('bdd.db')
    cursor = database.cursor()
    users  = cursor.execute("SELECT Users.is_in_danger, Users.is_wounded, Geolocalizations.latitude, Geolocalizations.longitude FROM Users INNER JOIN Geolocalizations ON Geolocalizations.id  = Users.Geolocalizations_id WHERE Users.is_wounded = '1' OR Users.is_in_danger = '1' ").fetchall()
    results = []
    for user in users:
        results.append(dict(is_in_danger = user[0], is_wounded = user[1], latitude = user[2], longitude = user[3]))
    return dict(results = results)

run(host='localhost', port=8080, reloader = True)
