#!/usr/bin/env python
# coding: utf-8

# In[4]:


from datetime import *
import numpy as np
import uuid


# In[5]:


#Persons, events and groups are stored in dictionarys and all have an unique id. They stand in the dictionary at the key of the unique id
#can I make a (sql) database out of python dictionaries?
events = {}
persons = {}
groups = {}


# In[2]:


class Person:
    def __init__(self, name):
        self.name = name
        self.id = str(uuid.uuid4())
        persons[self.id] = self
        self.termin_ids = []
        self.group_ids = []

    def create_event(self, name, cause=None, comment=None):
        Event(name, cause, comment)
        #question for further instructions with Termin
    def add_event(self, eventid): #we can only change an event if we now the prefs
        self.termin_ids.append(eventid)
        
    def create_group(self, name, persons):
        Group(name, persons)
    def add_group(self, group):
        self.group_ids.append(group)
    
    def clear_old(self, termine): #for slightly higher efficiency
        for termin_id in self.termin_ids:
            if events[termin_id].end < datetime.now():
                del events[termin_id]


# In[3]:


class Group:
    def __init__(name, persons=[Person]):
        self.name = name
        self.persons = persons
        self.id = str(uuid.uuid4())
        groups[self.id] = self


# In[4]:


class Event:
    def __init__(self, name, cause=None, comment=None):
        self.name = name
        self.cause = cause
        self.comment = comment
        self.id = str(uuid.uuid4())
        events[self.id] = self
        self.changeable = False
        
    def add_prefs(self, persons, duration=timedelta(hours=1, weekdays=[1,2,3,4,5,6,7], dstart, dend, Ustart, Uend, changeable=False):
        self.setupmode = 'prefs'
        self.prefs = Preferences(persons, duration, weekdays, dstart, dend, Ustart, Uend)
        self.changeable = changeable
    def find_time(self): #persons muss als liste weitergegeben werden, auch wenn es nur 1 Person gibt
        #check if prefs are given
        try:
            self.prefs
        except NameError:
            print("Initialize preferences before searching event")
            #link to add prefs?
            return
        
        #important variables for search
        global most, best_start, best_end, contributors
        most = 0
        
        #checking how many persons could come on which date
        #check every end of every event of every person
        for pers in self.prefs.persons:
            for terminid in pers.termin_ids: #Hier müssen noch alle Daten mut Ustart durchiteriert werden
                termin = events[terminid]
                terminend = termin.end
                self.check_datetime(terminend)
        #check starts of each day
        diff = self.prefs.dend - self.prefs.dstart
        day_count = diff.days
        for datum in (self.prefs.dstart + timedelta(days=n) for n in range(day_count)):
            start = datetime(year=datum.year, month=datum.month, day=datum.day, hour=self.prefs.Ustart.hour, minute=self.prefs.Ustart.minute)
            self.check_datetime(start)
        #check if now works fine
        self.check_datetime(datetime.now())
        
        #outputs the best datetime, if there is a possible solution
        try:
            print('Start of event: ' + best_start.strftime('%c') + '\n' + 'End of event: ' + best_end.strftime('%c') + '\n' + 'Number of participants who can take part: ' + str(most) + '\n' + 'participants who can take part: ' + str(contributors))
        except NameError:
            print('Es ist nicht möglich einen Termin mit der Dauer bei den Preferenzen festzulegen.')
            return
        
        #saves date if wanted
        save = 'a'
        while save not in 'nNjJ' or save == '':
            save = input('Soll der Termin gespeichert werden? (j/n):')
        if save in 'jJ':
            for person in prefs.persons:
                person.add_event(self.id)
    def check_datetime(self, pstart):
        global most, best_start, best_end, contributors
        ende = pstart + self.prefs.duration
        if pstart > datetime.now():
            if pstart.date().isoweekday() in self.prefs.weekdays and ende.date().isoweekday() in self.prefs.weekdays:
                if pstart.time() >= self.prefs.Ustart and ende.time() <= self.prefs.Uend:
                    contributors = self.prefs.persons
                    for person in self.prefs.persons:
                        for terminid in person.termin_ids:
                            termin = events[terminid]
                            if termin.end > pstart and termin.start < ende:
                                contributors.remove(person)
                                break
                    if len(contributors) > most:
                        most = len(contributors)
                        best_start = pstart
                        best_end = ende
    
    def manual_setup(self, persons, start, end):
        self.setupmode = 'manual'
        self.persons = persons
        self.start = start
        self.end = end
        for pers in persons:
            pers.add_event(self.id)


# In[6]:


class Preferences(Event): #should it be a subclass of Person?
    def __init__(self, persons, duration, weekdays, dstart, dend, Ustart, Uend):
        #weekdays as ints 1-7
        self.persons = persons #teilnehmenden personen
        self.duration = duration #dauer
        self.weekdays = weekdays #wochentage, an denen der Termin stattfinden können soll
        self.dstart = dstart #Startdatum für möglichen Termin
        self.dend = dend #Enddatum
        self.Ustart = Ustart #Startuhrzeit für möglichen Termin
        self.Uend = Uend #Enduhrzeit



