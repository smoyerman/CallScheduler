from enum import Enum
import numpy as np
import calendar
import random
import jinja2
import os

# Services
class Service(Enum):
    TRAUMA = 1
    HPB_TRANSPLANT = 2
    VASCULAR = 3
    COLORECTAL = 4
    BREAST = 5
    GS_GOLD = 6
    GS_BLUE = 7
    GS_ORANGE = 8


# Types of resident
class Type(Enum):
    JUNIOR = 1
    SENIOR = 2


# Resident Class
class Resident():

    def __init__(self, service, year, no):
        self.resNo = no
        self.noCallDays = 0
        self.callDays = []
        self.service = service
        self.year = year
        self.type = Type.JUNIOR
        self.PTO = []  # Dyanmically filled
        if year >= 3:
            self.type = Type.SENIOR


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)

class Scheduler():

    def __init__(self, year, month):
        self.residents = []
        c = calendar.Calendar(calendar.SUNDAY)
        self.calendar = np.array(c.monthdayscalendar(2017,7))
        self.daysInMonth = np.max(self.calendar)
        self.callAssignments = dict()
        for d in range(1, self.daysInMonth+1):
            self.callAssignments[d] = []
        self.hasSenior = np.zeros(self.daysInMonth+1)

    # Add a resident to the residents array in the Scheduler object
    def addResident(self, res):
        self.residents.append(res)

    # Unravel all the reaidents into tracking arrays, this will help parse and debug
    def unRavelResidents(self):
        self.Services = []
        self.CallCounts = []
        self.Years = []
        self.Types = []
        for res in self.residents:
            self.Services.append(res.service)
            self.Years.append(res.year)
            self.Types.append(res.type)
            self.CallCounts.append(res.noCallDays)
        self.Services = np.array(self.Services)
        self.CallCounts = np.array(self.CallCounts)
        self.Years = np.array(self.Years)
        self.Types = np.array(self.Types)

    # Get the indices of the trauma seniors
    def getTraumaSeniors(self):
        self.TS = np.where((self.Services == Service.TRAUMA) & (self.Types == Type.SENIOR))[0]

    # Assign the senior(s) on Trauma to the call schedule
    def assignTraumaSeniors(self):
        if len(self.TS) == 1:
            for i in self.calendar[:,0]:
                if i > 0:
                    self.addCallDay(i,self.TS[0])
                    self.hasSenior[i] = 1
        elif len(self.TS) == 2:
            ctr = 0
            for i in self.calendar[:,0]:
                if i > 0:
                    self.addCallDay(i, self.TS[ctr % len(self.TS)])
                    self.hasSenior[i] = 1
                    ctr += 1
                if i-1 > 0:
                    self.addCallDay(i-1, self.TS[ctr % len(self.TS)])
                    self.hasSenior[i] = 1
                    if len(self.TS) > 2:
                        ctr += 1

    # Adding a call day to a person's schedule - track everywhere
    def addCallDay(self, day, resident):
        self.callAssignments[day].append(self.residents[resident])
        self.residents[resident].noCallDays += 1
        self.residents[resident].callDays.append(day)
        self.CallCounts[resident] += 1

    # Quick print of call schedule to the command line
    def printCallSchedule(self):
        for key, item in self.callAssignments.items():
            for res in item:
                print(str(key) + ":\t" + str((res.resNo, res.service.name, res.year)))

    # Function to place seniors in remaining days, giving preference to older
    def placeSeniors(self):
        self.Seniors = np.where(self.Types == Type.SENIOR)[0]
        noSrsInPool = np.sum(self.Types == Type.SENIOR)
        noCallDaysRemaining = np.sum(self.hasSenior == 0)
        daysPerSenior = noCallDaysRemaining / float(noSrsInPool)
        random.shuffle(self.Seniors)
        j = 0
        for i in range(1,self.daysInMonth+1):
            if not self.hasSenior[i]:
                # assign next senior here
                if self.CallCounts[self.Seniors[j]] <= daysPerSenior:
                        if self.checkRules(self.Seniors[j], i):
                            self.addCallDay(i,self.Seniors[j])
                            self.hasSenior[i] = 1
                j += 1
                if j == len(self.Seniors):
                    random.shuffle(self.Seniors)
                    j = j % len(self.Seniors)

    # Check all the rules to see if a person can be put on this day
    def checkRules(self, sr, day):
        if self.check48hours and self.checkBacktoBackWeekends and self.checkPTO:
            return True
        else:
            return False

    # Check if on consecutive weekends, return True if everything is ok, return False if putting 2 weekends in a row
    def checkBacktoBackWeekends(self, sr, day):
        if (day in self.calendar[:,0]):
            if day - 7 > 0:
                if (sr in self.callAssignments[day-7]) or (sr in self.callAssignments[day-8]) or (sr in self.callAssignments[day-9]):
                    return False
        elif (day in self.calendar[:,6]):
            if day - 6 > 0:
                if (sr in self.callAssignments[day-6]) or (sr in self.callAssignments[day-7]) or (sr in self.callAssignments[day-8]):
                    return False
        elif (day in self.calendar[:,5]):
            if day - 5 > 0:
                if (sr in self.callAssignments[day-5]) or (sr in self.callAssignments[day-6]) or (sr in self.callAssignments[day-7]):
                    return False
        return True

    # Check if giving them their PTO - can add this in later, easy
    def checkPTO(self):
        return True

    # Check if there's at least 48 hours between calls
    def check48hours(self, sr, day):
        if day >= 2:
            if (sr in self.callAssignments[day-1]):
                return False
        if day >= 3:
            if (sr in self.callAssignments[day-2]):
                return False
        return True

    def returnResidents(self):
        resSchedule = dict()
        for key, item in self.callAssignments.items():
            resSchedule[key] = [res.service.name + ": PGY" + str(res.year) for res in item]
        return resSchedule

    # Function to render readable call schedule
    def renderCallSchedule(self):
        templateLoader = jinja2.FileSystemLoader( searchpath="/" )
        templateEnv = jinja2.Environment( loader=templateLoader )
        TEMPLATE_FILE = "/Users/smoyerma/Documents/Call Scheduler/html/calendar.html"
        template = templateEnv.get_template( TEMPLATE_FILE )
        resSchedule = self.returnResidents()
        templateVars = { "month" : self.calendar,
                         "schedule" : resSchedule }
        result = template.render( templateVars )
        Html_file = open("html/output.html","w")
        Html_file.write(result)
        Html_file.close()
