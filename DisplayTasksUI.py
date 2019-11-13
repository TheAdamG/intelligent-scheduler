from tkinter import *
from tkinter import messagebox
import CreateTaskUI,CreateWhitelistUI, DTS
from time import gmtime, strftime
import scheduler


CurrentDate = strftime("%d %m %Y", gmtime())
CurrentDate = (DTS.Date((CurrentDate[0:2]), (CurrentDate[3:5]), (CurrentDate[6:])))
NearestSunday = CurrentDate.nearest_sunday()
CurrentTime = strftime("%H %M" , gmtime())
CurrentTime = DTS.Time((CurrentTime[0:2]),(CurrentTime[3:]))
dateToday = [NearestSunday,CurrentDate]
timeNow = [CurrentTime]
timetableButtons = []

columnWidth = 10
currentDateTimeColour = "yellow"
backgroundColourSet = "white"
#backgroundColourSet = "#f888d1" #pink


def updateTasks(taskDisplayDict, root):

    def displayInfo(taskName, taskDateToDo, taskTimeToDo):
        masterD = Toplevel()
        masterD.title = taskName

        taskNameLabel = Label(masterD, text=taskName)
        taskNameLabel.grid(row=0, column=1)

        for taskObject in tasksList:
            if taskObject.date_to_do.string_d() == taskDateToDo and int(taskObject.time_to_do.string_h()) == taskTimeToDo:
                try:
                    taskDueDate = taskObject.dueDate.string_d()
                    taskDueTime = taskObject.dueTime.stringT()
                    taskDueDateLabel = Label(masterD, text="Due on: " + taskDueDate)
                    taskDueDateLabel.grid(row=1, column=1)
                    taskDueTimeLabel = Label(masterD, text="At: " + taskDueTime)
                    taskDueTimeLabel.grid(row=2, column=1)
                except:
                    pass
                break

        def completeDelete(task, completeCheck):
            masterD.destroy()
            if completeCheck:
                task.update_heuristic(True)
            scheduler.delete_task(task)
            UI(root)

        def update(task):
            masterD.destroy()
            CreateTaskUI.createTaskWindow(root, taskObject)

        taskDateToDoLabel = Label(masterD, text="Complete on: " + taskDateToDo)
        taskDateToDoLabel.grid(row=3, column=1)
        taskTimeToDoLabel = Label(masterD, text="At: " + str(taskTimeToDo) + ":00")
        taskTimeToDoLabel.grid(row=4, column=1)

        updateButton = Button(masterD, text="Update", command=lambda: update(taskObject))
        updateButton.grid(row=5, column=1)

        completeButton = Button(masterD, text="Complete", command=lambda completedBool = True: completeDelete(taskObject,completedBool))
        completeButton.grid(row=5, column=0)

        deleteButton = Button(masterD, text="Delete", command = lambda completedBool = False: completeDelete(taskObject, completedBool))
        deleteButton.grid(row=5, column=3)

        masterD.mainloop()

    for L in timetableButtons: #This deletes all the button widgets
        L.destroy()

    for i in range(0,24): #This section creates the Time labels down the left hand coloumn
        if i < 10:
            timeString = "0" + str(i) + ":00"
        else:
            timeString = str(i)+ ":00"

        timeLabel = Label(root, text=timeString, bg = backgroundColourSet)
        timeLabel.grid(row=i+4,column=0)

        if i == int(timeNow[0].string_h()): #This will set the current Time to be highlighted yellow
            timeLabel.configure(bg=currentDateTimeColour)


    displayColumn = 1
    displayRow = 2
    for day in taskDisplayDict: #This will iterate through each day in the dictionary

        """This section establishes the top labes that have the day of the week and dates of the week being looked at"""
        dayLabel = Label(root, text=day, bg = backgroundColourSet, width = columnWidth)
        dayLabel.grid(row=displayRow, column=displayColumn)
        dateLabel = Label(root, text=taskDisplayDict[day][0], bg = backgroundColourSet, width = columnWidth)
        dateLabel.grid(row=displayRow+1, column=displayColumn)
        if taskDisplayDict[day][0] == dateToday[1].string_d(): #This will set the current day and Date to have a yellow background
            dayLabel.configure(bg = currentDateTimeColour)
            dateLabel.configure(bg = currentDateTimeColour)

        """This section will create all the button widgets that makeup the cells of the main UI"""
        for timeSlot in taskDisplayDict[day][1]:
            """ This line will create the tkinter button object with the command to call the function display info, and pass in the needed variables."""
            L = Button(root, text=timeSlot, command = lambda taskName = timeSlot, taskDateToDo = taskDisplayDict[day][0], taskTimeToDo = displayRow-2 : displayInfo(taskName, taskDateToDo, taskTimeToDo))
            L.configure(bg = backgroundColourSet, relief = RIDGE, width = columnWidth, padx = 0, pady=0)

            if timeSlot == "Blacklist":
                L.configure(bg = "black",text= "",state= DISABLED ) #This will disable blacklisted buttons and make them black
            elif timeSlot == "":
                L.configure(state=DISABLED) #This will disable cells which do not contain a task
            L.grid(row=displayRow+2, column=displayColumn)
            timetableButtons.append(L)
            displayRow += 1
        displayRow = 2
        displayColumn += 1

def UI(tkinterRoot):
    tasksList[:] = scheduler.read_object_file()
    whitelistList = scheduler.read_whitelist_file()
    display = {
        "Sunday": [[], []],
        "Monday": [[], []],
        "Tuesday": [[], []],
        "Wednesday": [[], []],
        "Thursday": [[], []],
        "Friday": [[], []],
        "Saturday": [[], []],
    }
    weekDay = dateToday[0]

    for day in display:
        for i in range(0, 24):
            for task in tasksList:
                if task.date_to_do.string_d() == weekDay.string_d() and int(task.time_to_do.string_h()) == i:
                    display[day][1].append(task.name)
                    break
            else:
                display[day][1].append("Blacklist")
        display[day][0] = weekDay.string_d()
        weekDay = weekDay.add_days(1)

    for whitelist in whitelistList:
        for i in whitelist.free_times:
            if display[whitelist.whitelist_day_name][1][int(i.string_h())] == "Blacklist":
                display[whitelist.whitelist_day_name][1][int(i.string_h())] = ""

    updateTasks(display, tkinterRoot)


def warningMessage(title,message):

    messagebox.showwarning(title,message)


def displayTask():

    root = Tk()
    root.title("Auto-Scheduler")
    root.configure(bg = backgroundColourSet)

    def callCreateTaskUI():
        CreateTaskUI.createTaskWindow(root)
    def callCreateWhitelistUI():
        CreateWhitelistUI.createWhitelistWindow(root)
    def goBack():
        dateToday[0] = dateToday[0].sub_days(7)
        UI(root)
    def goForward():
        dateToday[0] = dateToday[0].add_days(7)
        UI(root)

    def runCheckTasks():
        scheduler.check_tasks()
        root.after(900000, runCheckTasks)

    UI(root)

    createTaskButton = Button(text="+", command=callCreateTaskUI, bg =backgroundColourSet).grid(row = 0, column = 0)
    Label(text="New task", bg = backgroundColourSet, width = columnWidth).grid(row=0, column = 1)
    createWhitelistButton = Button(root, text="[]", bg = backgroundColourSet, command=callCreateWhitelistUI).grid(row = 0, column = 2,)
    Label(text="Blacklist times", bg=backgroundColourSet, width = columnWidth).grid(row=0, column = 3, columnspan = 1)

    backWeek = Button(root, text="<", command=goBack, bg =backgroundColourSet).grid(row=2, column=0, padx=5)
    forwardWeek = Button(root, text=">", command=goForward, bg=backgroundColourSet).grid(row=2, column=8, padx=5)

    separator = Frame(height=2, width = 64, bd=1, relief=RIDGE)
    separator.grid(row = 1, column = 0, columnspan = 9, padx=0, pady=5,  sticky=W+E)

    runCheckTasks()
    root.mainloop()


tasksList = scheduler.read_object_file()



