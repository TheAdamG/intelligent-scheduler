from tkinter import *
import scheduler, DisplayTasksUI, DTS


def createWhitelistWindow(tkinterRoot):
    # This creates the new window for the whitelist menu
    master = Toplevel()
    master.title("Create whitelist")
    # Initialise the colours in variables
    black = "black"
    white = "white"
    # Load the whitelist into memory and return it as a variable
    scheduler.read_whitelist_file()
    whitelistList = scheduler.return_whitelist_list()
    daysDict = {"Sunday": [[], []],
                "Monday": [[], []],
                "Tuesday": [[], []],
                "Wednesday": [[], []],
                "Thursday": [[], []],
                "Friday": [[], []],
                "Saturday": [[], []],
                }

    def setWhitelist(day, time):
        if daysDict[day][1][time]:
            daysDict[day][1][time] = False
            daysDict[day][0][time].configure(bg=black, fg=white)
        else:
            daysDict[day][1][time] = True
            daysDict[day][0][time].configure(bg=white, fg=black)

    def submit():
        newWhitelistList = []  # This is a list of all the whitelisted times on each day
        for day in daysDict:
            freeTimeList = []  # This is list of all the whitelisted times on a given day
            for time in range(24):
                # If the time is set to be whitelisted it will be added to the freeTimeList
                if daysDict[day][1][time] == True:
                    if time < 10:
                        timeString = "0" + str(time)
                    else:
                        timeString = str(time)
                    freeTimeList.append(DTS.Time(timeString, "00"))
            """Once all the free times for a given day have been added to the list, 
            that list gets appended to newWhitelistList        """
            newWhitelistList.append(scheduler.WhitelistTimes(day, freeTimeList))

        scheduler.update_whitelist_list(newWhitelistList)
        scheduler.check_tasks()
        DisplayTasksUI.UI(tkinterRoot)
        master.destroy()

    def cancel():
        master.destroy()

    timeRow = 0
    for day in daysDict:
        Label(master, text=day).grid(row=timeRow, column=0)  # This makes the left hand coloumn with the days
        for time in range(24):
            if time < 10:
                timeString = "0" + str(time) + ":00"
            else:
                timeString = str(time) + ":00"
            # This makes each button and labels it with the time of the day
            timeLabel = Button(master, text=timeString, bg=black, fg=white,
                               command=lambda first=day, second=time: setWhitelist(first, second))
            timeLabel.grid(row=timeRow, column=(time + 1))
            daysDict[day][0].append(timeLabel)
            daysDict[day][1].append(False)
        timeRow += 1

    for whitelistObject in whitelistList:
        for time in whitelistObject.free_times:
            daysDict[whitelistObject.whitelist_day_name][1][int(time.string_h())] = True
            daysDict[whitelistObject.whitelist_day_name][0][int(time.string_h())].configure(bg=white, fg=black)

    submitButton = Button(master, text="Submit", command=submit).grid(row=2, column=25)
    cancelButton = Button(master, text="Cancel", command=cancel).grid(row=4, column=25)

    master.mainloop()
