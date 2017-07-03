import Config
import numpy as np
import os
import jinja2

# Hard-coded peeps for July right now - make a loader function for grabbing from excel or webbpage
July = [
    # First
    (Config.Service.GS_GOLD, 1),
    (Config.Service.TRAUMA, 1),
    (Config.Service.GS_BLUE, 1),
    (Config.Service.COLORECTAL, 1),
    (Config.Service.BREAST, 1),
    (Config.Service.GS_ORANGE, 1),
    # Second
    (Config.Service.HPB_TRANSPLANT, 2),
    # Third
    (Config.Service.TRAUMA, 3),
    (Config.Service.GS_GOLD, 3),
    (Config.Service.GS_BLUE, 3),
    # Fourth
    (Config.Service.HPB_TRANSPLANT, 4),
    (Config.Service.VASCULAR, 4),
    (Config.Service.COLORECTAL, 4),
    # Fifth
    (Config.Service.GS_GOLD, 5),
    (Config.Service.GS_BLUE, 5),
    (Config.Service.GS_ORANGE, 5),
    #(Config.Service.TRAUMA, 5),
]

# Dynamically create calendar
year = 2017
month = 7
s = Config.Scheduler(year, month)

# Arrange residents in a meaningful way
for i, j in enumerate(July):
    s.addResident(Config.Resident(j[0],j[1],i))
s.unRavelResidents()

# Put seniors on Trauma
s.getTraumaSeniors()
s.assignTraumaSeniors()

# Place the seniors everywhere
s.placeSeniors()

s.printCallSchedule()

"""import numpy as np
import pandas as pd

# This wil be configured based on some web UI or excel doc or both
noRes = 19
services = [Config.Service.GS_GOLD, Config.Service.TRAUMA, Config.Service.GS_BLUE, Config.Service.COLORECTAL, Config.Service.BREAST, Config.Service.GS_ORANGE,np.nan,Config.Service.HPB_TRANSPLANT,np.nan,Config.Service.TRAUMA,np.nan,Config.Service.GS_GOLD,Config.Service.GS_BLUE,Config.Service.HPB_TRANSPLANT,Config.Service.VASCULAR,Config.Service.COLORECTAL,Config.Service.GS_GOLD,Config.Service.GS_BLUE,Config.Service.GS_ORANGE]
years = np.array([1,1,1,1,1,1,2,2,2,3,3,3,3,4,4,4,5,5,5])

types = np.array([Config.Type.SENIOR]*noRes)
types[years < 3] = Config.Type.JUNIOR

d = {'Service' : pd.Series(services, index=range(noRes)),
     'Year' : pd.Series(years, index=range(noRes)),
     'NoDays' : pd.Series(np.zeros(noRes), index=range(noRes)),
     'Type' : pd.Series(types, index=range(noRes))}

df = pd.DataFrame(d)

# How many seniors on Trauma
TraumaSrs = df[(df['Type'] == Config.Type.SENIOR) & (df['Service'] == Config.Service.TRAUMA)]

if len(TraumaSrs) == 1:
    for i in arrDays[:,0]:
        if i > 0:
            callAssignments[i].append(TraumaSrs.index[0])
            df[TraumaSrs]["NoDays"] += 1
"""
