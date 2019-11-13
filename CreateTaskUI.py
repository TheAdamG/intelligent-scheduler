from tkinter import *
import DisplayTasksUI, scheduler, DTS
from time import gmtime, strftime


def createTaskWindow(tkinterRoot, taskObject=None):
    master = Toplevel()  # This create a new window
    master.title("Create a task")

    taskNameLabel = Label(master, text="Task Name:").grid(row=0, column=0)
    taskNameEntry = Entry(master)
    taskNameEntry.grid(row=0, column=1)

    autoList = []  # This is the list for inputs that are needed for tasks that will be auto-scheduled
    manualList = []  # This is the list for inputs that are needed for tasks that will be manually scheduled

    def setAuto(check):

        """This function will create all the inputs needed for both types of tasks and then delete the ones
        that are not currently needed, allowing for certain input fields to be toggled on or off."""

        dueDateLabel = Label(master, text="Due date:")
        dueDateLabel.grid(row=2, column=0)
        autoList.append(dueDateLabel)
        dueDateEntry = Entry(master)
        dueDateEntry.grid(row=2, column=1)
        autoList.append(dueDateEntry)

        dueTimeLabel = Label(master, text="Due time:")
        dueTimeLabel.grid(row=3, column=0)
        autoList.append(dueTimeLabel)
        dueTimeEntry = Entry(master)
        dueTimeEntry.grid(row=3, column=1)
        autoList.append(dueTimeEntry)

        priorityLabel = Label(master, text="Priority: ")
        priorityLabel.grid(row=5, column=0)
        autoList.append(priorityLabel)
        priorityScale = Scale(master, from_=1, to=10, orient=HORIZONTAL)
        priorityScale.grid(row=5, column=1)
        autoList.append(priorityScale)

        dateToDoLabel = Label(master, text="Date to do: ")
        dateToDoLabel.grid(row=2, column=0)
        manualList.append(dateToDoLabel)
        dateToDoEntry = Entry(master)
        dateToDoEntry.grid(row=2, column=1)
        manualList.append(dateToDoEntry)

        timeToDoLabel = Label(master, text="Time to do:")
        timeToDoLabel.grid(row=3, column=0)
        manualList.append(timeToDoLabel)
        timeToDoEntry = Entry(master)
        timeToDoEntry.grid(row=3, column=1)
        manualList.append(timeToDoEntry)

        if check.get() == 1:
            for i in manualList:  # This will destroy all the manual task inputs so the user can input auto-scheduled tasks
                i.destroy()
            manualList[:] = []

        else:
            for i in autoList:  # This will destroy all the auto-schedule task inputs
                i.destroy()
            autoList[:] = []

    autoScheduleLabel = Label(master, text="Auto-Schedule task:").grid(row=1, column=0)
    check = IntVar()
    autoScheduleCheck = Checkbutton(master, variable=check, onvalue=1, offvalue=0, command=lambda: setAuto(check))
    autoScheduleCheck.grid(row=1, column=1)

    setAuto(check)

    taskLengthLabel = Label(master, text="Task length:").grid(row=4, column=0)
    taskLengthEntry = Entry(master)
    taskLengthEntry.grid(row=4, column=1)

    categoryLabel = Label(master, text="Category:").grid(row=6, column=0)
    categoryEntry = Entry(master)
    categoryEntry.grid(row=6, column=1)

    """This section will check if the user is inputting a new task 
    or updating an old one. If they are updating an old one, it will 
    fill in the fields with the information that already exists"""
    deleteOld = False
    if taskObject != None:
        taskNameEntry.insert(0, taskObject.name)
        # This will check whether they are updating an auto-scheduled task or not
        try:
            autoScheduleCheck.invoke()
            autoList[1].insert(0, taskObject.due_date.string_d())
            autoList[3].insert(0, taskObject.due_time.string_t())
            autoList[5].set(taskObject.priority)
        except:
            autoScheduleCheck.invoke()
            manualList[1].insert(0, taskObject.date_to_do.string_d())
            manualList[3].insert(0, taskObject.time_to_do.string_t())

        taskLengthEntry.insert(0, taskObject.length.string_t())

        categoryEntry.insert(0, taskObject.category)
        """If they are updating an existing task, the program will 
        create new instance of that task and delete the previous 
        version of it"""
        deleteOld = True

    def submit():

        if deleteOld:
            scheduler.delete_task(taskObject)
        scheduler.read_object_file()
        scheduler.read_whitelist_file()
        scheduler.read_heuristic_file()

        task_name = taskNameEntry.get()
        task_length = taskLengthEntry.get()
        category = categoryEntry.get()

        if check.get() == 1:
            due_date = autoList[1].get()
            due_time = autoList[3].get()
            priority = autoList[5].get()
            valid, error = scheduler.create_task(task_name, priority, due_date, due_time, task_length, category)
        else:
            date_to_do = manualList[1].get()
            time_to_do = manualList[3].get()
            valid, error = scheduler.create_manual_task(task_name, date_to_do, time_to_do, task_length, category)

        if valid:
            scheduler.write_object_file()
            scheduler.write_heuristic_file()
            DisplayTasksUI.UI(tkinterRoot)
            master.destroy()
        else:
            DisplayTasksUI.warningMessage(valid, error)

    def cancel():
        master.destroy()

    submitButton = Button(master, text="Submit", command=submit).grid(row=7, column=0)
    cancelButton = Button(master, text="Cancel", command=cancel).grid(row=7, column=1)

    master.mainloop()

# createTaskWindow()
