import Config
import numpy as np
import os

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
s.renderCallSchedule()
