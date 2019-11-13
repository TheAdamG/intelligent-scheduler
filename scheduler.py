import DTS, BAP, csv, DisplayTasksUI
from time import gmtime, strftime

tasksList = []
whitelistList = []
dayList = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
allTimes = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
            "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
categoriesHeuristic = {}


class Tasks(object):
    def __init__(self, name, priority, due_date, due_time, length, category):
        self.name = name
        self.priority = priority
        self.due_date = due_date
        self.due_time = due_time
        self.length = length
        current_date = strftime("%d %m %Y", gmtime())
        self.today = DTS.Date((current_date[0:2]), (current_date[3:5]), (current_date[6:]))
        current_time = strftime("%H %M", gmtime())
        self.now = DTS.Time((current_time[0:2]), (current_time[3:]))
        self.date_to_do = 0
        self.time_to_do = 0
        self.priorityIndex = 0
        self.category = category
        self.heuristic = 1

    def calculate_date(self, bap_type):
        # This first section calculates how many timeslots from when the task was created until when the task is due.
        difference = DTS.minutes_until(self.today, self.now, self.due_date, self.due_time)
        hours_until = int(difference / 60)
        diff_slots = hours_until
        """ This is where whitelisted slots are removed from the number of diff_slots"""
        days_difference = DTS.date_diff(self.today, self.due_date)
        days_dict = {"Sunday": [0, 0],
                     "Monday": [0, 0],
                     "Tuesday": [0, 0],
                     "Wednesday": [0, 0],
                     "Thursday": [0, 0],
                     "Friday": [0, 0],
                     "Saturday": [0, 0],
                     }
        # This section calculates how many of each day there are until due date

        if days_difference > 7:
            no_days = days_difference // 7
            for day_name in days_dict:
                days_dict[day_name][0] = no_days
        no_days = (days_difference % 7) + 1

        current_day_index = dayList.index(self.today.day_name)
        for i in range(current_day_index + 1, current_day_index + no_days - 1):
            if i >= 7:
                ind = i - 7
                days_dict[dayList[ind]][0] += 1
            else:
                days_dict[dayList[i]][0] += 1

        # This section creates the whitelist

        now_hours_to_mid, now_mins_to_mid = DTS.time_diff(self.now, DTS.Time("24", "00"))
        if self.today.string_d() != self.due_date.string_d():
            mid_hours_to_due, mid_mins_to_due = DTS.time_diff(DTS.Time("00", "00"), self.due_time)
        else:
            mid_hours_to_due, mid_mins_to_due = DTS.time_diff(self.now, self.due_time)

        for whitelistObject in whitelistList:
            days_dict[whitelistObject.whitelist_day_name][1] = len(whitelistObject.free_times)
            # This if statement subtracts the blacklisted times from the time it is set on that day to midnight
            if whitelistObject.whitelist_day_name == self.today.day_name and self.today.string_d() != self.due_date.string_d():
                for free_time in whitelistObject.free_times:
                    if int(self.now.string_h()) <= int(free_time.string_h()):
                        now_hours_to_mid -= 1
            if whitelistObject.whitelist_day_name == self.due_date.day_name:
                for free_time in whitelistObject.free_times:
                    # This if statement subtracts the blacklisted times up to the time it is due on the due date from midnight
                    if int(self.due_time.string_h()) >= int(
                            free_time.string_h()) and self.today.string_d() != self.due_date.string_d():
                        mid_hours_to_due -= 1

                    if int(self.due_time.string_h()) >= int(free_time.string_h()) and int(self.now.string_h()) <= int(
                            free_time.string_h()) and self.today.string_d() == self.due_date.string_d():
                        mid_hours_to_due -= 1

        # This section removes all the blacklisted timeslots from now until the due date
        for day in days_dict:
            diff_slots -= days_dict[day][0] * (24 - days_dict[day][1])
            if diff_slots < 0:
                diff_slots += days_dict[day][0] * (24 - days_dict[day][1])
        diff_slots += 1
        diff_slots -= now_hours_to_mid
        diff_slots -= mid_hours_to_due

        if diff_slots > 0:
            hour_number, self.priorityIndex = BAP.calculate_slot(self.priority, diff_slots, self.heuristic, bap_type)
        else:
            DisplayTasksUI.warningMessage("You have no room in your schedule!",
                                          self.name + " This task will be deleted")
            delete_task(self)
            return "Null"

        if hour_number == "Null":
            DisplayTasksUI.warningMessage("You have no room in your schedule!",
                                          self.name + " This task will be deleted")
            delete_task(self)
            return "Null"

        # print (hour_number)

        """ This is where the timeslot selected is calculated """
        current_day_index = dayList.index(self.today.day_name)
        days_to_add = 0  # This section calculates how many days to add
        loop = True
        while loop:
            while current_day_index < 7:
                hour_number -= (days_dict[dayList[current_day_index]][1])
                # print ((days_dict[dayList[current_day_index]][1]))
                if hour_number < 0:
                    hour_number += (days_dict[dayList[current_day_index]][1])
                    loop = False
                    break
                days_to_add += 1
                current_day_index += 1
            current_day_index -= 7
        self.date_to_do = self.today.add_days(days_to_add)

        free_times_on_day = []
        for whitelistObject in whitelistList:
            if self.date_to_do.day_name == whitelistObject.whitelist_day_name:
                if self.date_to_do.string_d() == self.today.string_d():
                    for free_time in whitelistObject.free_times:
                        if int(free_time.string_h()) > int(self.now.string_h()):
                            free_times_on_day.append(free_time)
                else:
                    free_times_on_day = whitelistObject.free_times
        self.time_to_do = free_times_on_day[hour_number]

        for taskObject in tasksList:
            if taskObject.date_to_do.string_d() == self.date_to_do.string_d() and taskObject.time_to_do.string_t() == self.time_to_do.string_t() and self != taskObject:
                if taskObject.priorityIndex >= self.priorityIndex:
                    if self.calculate_date(bap_type + 1) == "Null":
                        return "Null"
                else:
                    if taskObject.calculate_date(bap_type) == "Null":
                        return "Null"
                    else:
                        DisplayTasksUI.warningMessage("Rescheduled a task",
                                                      taskObject.name + " has been rescheduled.")

        """ """

    def update_to_do(self):
        current_date = strftime("%d %m %Y", gmtime())
        self.today = DTS.Date((current_date[0:2]), (current_date[3:5]), (current_date[6:]))
        current_time = strftime("%H %M", gmtime())
        self.now = DTS.Time((current_time[0:2]), (current_time[3:]))

        # This section will check if the deadline for a task has passed
        try:
            if DTS.date_time_comparison(self.today, self.now, self.due_date, self.due_time):
                DisplayTasksUI.warningMessage("A deadline has passed!",
                                              "The deadline for " + self.name + " has passed. This task will be deleted")
                self.update_heuristic(False)
                delete_task(self)
                return
        except:
            pass

        # This section wil check if the time to complete a task has passed
        if DTS.date_time_comparison(self.today, self.now, self.date_to_do, self.time_to_do):
            DisplayTasksUI.warningMessage("You missed the time to complete a task!",
                                          "You missed the time to do " + self.name + ". Recalculating..,")
            self.update_heuristic(False)
            self.calculate_date(0)
            return

        # This section checks if a blacklist was set over an existing time.
        for whitelistObject in whitelistList:
            new_list = [x.string_t() for x in whitelistObject.free_times]
            if self.time_to_do.string_t() not in new_list and self.date_to_do.day_name == whitelistObject.whitelist_day_name:
                try:
                    self.due_date
                    DisplayTasksUI.warningMessage("You set a blacklist over a task",
                                                  "I will try to recalculate " + self.name)
                    self.calculate_date(0)
                except:
                    pass

    def completed(self):
        self.update_heuristic(True)
        delete_task(self)

    def set_heuristic(self):
        if self.category in categoriesHeuristic:
            self.heuristic = categoriesHeuristic[self.category]
        else:
            categoriesHeuristic.update({self.category: 1})
        write_heuristic_file()

    def update_heuristic(self, completed):
        if completed:
            if categoriesHeuristic[self.category] > 0.1:
                categoriesHeuristic[self.category] -= 0.1
        else:
            if categoriesHeuristic[self.category] < 4.9:
                categoriesHeuristic[self.category] += 0.1
        write_heuristic_file()

    def print_task(self):
        print("-----------------------")
        print(self.name)
        print("Priority: " + str(self.priority))
        print("Due date: ", end="")
        self.due_date.print_d()
        print("Due time: ", end="")
        self.due_time.print_t()

        print("Complete on the: ", end="")
        self.date_to_do.print_d()
        print("At: ", end="")
        self.time_to_do.print_t()
        print(self.priorityIndex)
        print("-----------------------\n")


class ManualTasks(Tasks):
    def __init__(self, name, date_to_do, time_to_do, length, category):
        self.name = name
        self.date_to_do = date_to_do
        self.time_to_do = time_to_do
        self.length = length
        self.category = category
        self.heuristic = 1
        self.priorityIndex = 2

    def calculate_date(self, bap_type):
        delete_task(self)
        return "Null"

    def check_existing(self, bap_type):
        for taskObject in tasksList:
            if taskObject.date_to_do.string_d() == self.date_to_do.string_d() and taskObject.time_to_do.string_t() == self.time_to_do.string_t() and self != taskObject:
                if taskObject.priorityIndex >= self.priorityIndex:
                    if self.calculate_date(bap_type + 1) == "Null":
                        DisplayTasksUI.warningMessage("This task cannot be created!",
                                                      "A manual task already exists in this time slot.")
                        return "Null"
                else:
                    if taskObject.calculate_date(bap_type) == "Null":
                        return "Null"
                    else:
                        DisplayTasksUI.warningMessage("Rescheduled a task",
                                                      taskObject.name + " has been rescheduled.")


class WhitelistTimes(object):
    def __init__(self, whitelist_day_name, free_times):
        self.whitelist_day_name = whitelist_day_name
        self.free_times = free_times


class CustomValidationError(Exception):  # This class will set the error message as the value
    def __init__(self, value):
        self.value = value


def read_object_file():
    tasksList[:] = []
    for row in csv.reader(open("taskFile.csv", "r")):
        if row[0] != "":

            date_to_do_split = row[5].split("/")
            date_to_do_r = DTS.Date((date_to_do_split[0]), (date_to_do_split[1]), (date_to_do_split[2]))

            time_to_do_split = row[6].split(":")
            time_to_do_r = DTS.Time((time_to_do_split[0]), (time_to_do_split[1]))

            length_split = row[4].split(":")
            length_r = DTS.Time((length_split[0]), (length_split[1]))

            if row[2] != "Null":
                due_date_split = row[2].split("/")
                due_date_r = DTS.Date((due_date_split[0]), (due_date_split[1]), (due_date_split[2]))
                due_time_split = row[3].split(":")
                due_time_r = DTS.Time((due_time_split[0]), (due_time_split[1]))

                new_task = Tasks(row[0], int(row[1]), due_date_r, due_time_r, length_r, row[8])
                new_task.time_to_do = time_to_do_r
                new_task.date_to_do = date_to_do_r
            else:
                new_task = ManualTasks(row[0], date_to_do_r, time_to_do_r, length_r, row[8])

            new_task.set_heuristic()

            new_task.priorityIndex = float(row[7])
            tasksList.append(new_task)

            new_task.update_to_do()

    return tasksList


def write_object_file():
    task_file = open("taskFile.csv", "w")
    for n in tasksList:
        try:
            task_file.write(n.name + "," + str(
                n.priority) + "," + n.due_date.string_d() + "," + n.due_time.string_t() + "," + n.length.string_t() + "," + n.date_to_do.string_d() + "," + n.time_to_do.string_t() + "," + str(
                n.priorityIndex) + "," + n.category + '\n')
        except:
            task_file.write(
                n.name + "," + "Null" + "," + "Null" + "," + "Null" + "," + n.length.string_t() + "," + n.date_to_do.string_d() + "," + n.time_to_do.string_t() + "," + str(
                    n.priorityIndex) + "," + n.category + '\n')


def create_task(task_name, priority, task_due_date, task_due_time, task_length, category):
    current_date = strftime("%d %m %Y", gmtime())
    current_date = DTS.Date((current_date[0:2]), (current_date[3:5]), (current_date[6:]))
    current_time = strftime("%H %M", gmtime())
    current_time = DTS.Time((current_time[0:2]), (current_time[3:]))
    # For reference the base dates are:
    # base_date = DTS.Date("00", "00", "0000")
    # base_time = DTS.Time("00", "00")

    try:
        feb = DTS.check_leap(int(task_due_date[6:]))
        list_of_months = [31, feb, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        # Checks if the month is valid
        if int(task_due_date[3:5]) > 12 or int(task_due_date[3:5]) < 1:
            raise CustomValidationError("Please ensure you have entered a month less than or equal to 12")
        # Checks if the day is valid
        if int(task_due_date[0:2]) > list_of_months[int(task_due_date[3:5]) - 1] or int(task_due_date[0:2]) < 1:
            raise CustomValidationError("Please ensure you have entered a date that exists")
        # This will create the date object
        task_due_date = DTS.Date((task_due_date[0:2]), (task_due_date[3:5]), (task_due_date[6:]))
        # If the date is set before the current time, an error is raised
        if not DTS.date_validation(task_due_date, current_date):
            raise CustomValidationError("Please do not set the due date before the current date")

    except CustomValidationError as error:  # Custom error is called
        return False, error.value

    except:  # The error for the date being entered wrongly is called
        return False, "Please enter the due date as DD/MM/YYYY"

    try:
        if int(task_due_time[0:2]) > 23 or int(task_due_time[0:2]) < 0 or int(task_due_time[3:]) > 59 or int(
                task_due_time[3:]) < 0:
            raise CustomValidationError("Please ensure you have entered a time between 00:00 and 23:59")
        task_due_time = DTS.Time((task_due_time[0:2]), (task_due_time[3:]))
        if not DTS.date_time_comparison(task_due_date, task_due_time, current_date, current_time):
            raise CustomValidationError("Please do not set the due time before the current time")
    except CustomValidationError as error:
        return False, error.value
    except:
        return False, "Please enter the due time as hh/mm"

    try:
        task_length = DTS.Time((task_length[0:2]), (task_length[3:]))
    except:
        return False, "Please enter the task length as hh/mm"

    new_task = Tasks(task_name, priority, task_due_date, task_due_time, task_length, category)
    new_task.set_heuristic()
    tasksList.append(new_task)
    if new_task.calculate_date(0) != "Null":
        DisplayTasksUI.warningMessage("Task created successfully!", (
            new_task.name + " has been created. Complete it on " + new_task.date_to_do.string_d() + " at " + new_task.time_to_do.string_t()))
    return True, "No error"


def create_manual_task(task_name, task_date_to_do, task_time_to_do, task_length, category):
    current_date = strftime("%d %m %Y", gmtime())
    current_date = DTS.Date((current_date[0:2]), (current_date[3:5]), (current_date[6:]))
    current_time = strftime("%H %M", gmtime())
    current_time = DTS.Time((current_time[0:2]), (current_time[3:]))
    # For reference the base dates are
    # base_date = DTS.Date("00", "00", "0000")
    # base_time = DTS.Time("00", "00")

    try:
        feb = DTS.check_leap(int(task_date_to_do[6:]))
        list_of_months = [31, feb, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        if int(task_date_to_do[3:5]) > 12 or int(task_date_to_do[3:5]) < 1:  # Checks if the month is valid
            raise CustomValidationError("Please ensure you have entered a month less than or equal to 12")

        if int(task_date_to_do[0:2]) > list_of_months[int(task_date_to_do[3:5]) - 1] or int(
                task_date_to_do[0:2]) < 1:  # Checks if the day is valid
            raise CustomValidationError("Please ensure you have entered a date that exists")

        task_date_to_do = DTS.Date((task_date_to_do[0:2]), (task_date_to_do[3:5]),
                                   (task_date_to_do[6:]))  # This will create the date object
        if not DTS.date_validation(task_date_to_do,
                                   current_date):  # If the date is set before the current time, an error is raised
            raise CustomValidationError("Please do not set the date to do before the current date")

    except CustomValidationError as error:  # Custom error is called
        return False, error.value

    except:
        return (
            False,
            "Please enter the date to do as DD/MM/YYYY")  # The error for the date being entered wrongly is called

    try:
        if int(task_time_to_do[0:2]) > 23 or int(task_time_to_do[0:2]) < 0 or int(task_time_to_do[3:]) > 59 or int(
                task_time_to_do[3:]) < 0:
            raise CustomValidationError("Please ensure you have entered a time between 00:00 and 23:59")

        task_time_to_do = DTS.Time((task_time_to_do[0:2]), (task_time_to_do[3:]))

        if not DTS.date_time_comparison(task_date_to_do, task_time_to_do, current_date, current_time):
            raise CustomValidationError("Please do not set the time to do before the current time")

    except CustomValidationError as error:
        return False, error.value
    except:
        return False, "Please enter the time to do as hh/mm"

    try:
        task_length = DTS.Time((task_length[0:2]), (task_length[3:]))
    except:
        return False, "Please enter the task length as hh/mm"

    new_task = ManualTasks(task_name, task_date_to_do, task_time_to_do, task_length, category)
    new_task.set_heuristic()
    tasksList.append(new_task)
    new_task.check_existing(0)
    return True, "No error"


def delete_task(task_to_delete):
    tasksList.remove(task_to_delete)
    write_object_file()


def read_whitelist_file():
    whitelistList[:] = []
    whitelist_file = open("whitelist.txt", "r")
    for line in whitelist_file:
        line = line.split(",")
        if len(line[1:]) >= 1 and ":" in line[1]:
            free_time_list = []
            for free_time in line[1:]:
                free_time = free_time.split(":")
                free_time_list.append(DTS.Time(free_time[0], free_time[1]))
            new_whitelist = WhitelistTimes(line[0], free_time_list)
            whitelistList.append(new_whitelist)
        else:
            new_whitelist = WhitelistTimes(line[0], [])

    return whitelistList


def write_whitelist_file():
    whitelist_file = open("whitelist.txt", "w")
    for whitelistObject in whitelistList:
        whitelisted_times = []
        for times in whitelistObject.free_times:
            whitelisted_times.append(times.string_t())
        whitelist_file.write(whitelistObject.whitelist_day_name + "," + ",".join(whitelisted_times) + "\n")


def return_task_list():
    return tasksList


def return_whitelist_list():
    return whitelistList


def update_whitelist_list(new_list):
    whitelistList[:] = new_list
    write_whitelist_file()


def read_heuristic_file():
    for row in csv.reader(open("heuristicValues.csv", "r")):
        if row[0] != "":
            categoriesHeuristic.update({row[0]: float(row[1])})


def write_heuristic_file():
    heuristic_file = open("heuristicValues.csv", "w")
    for category in categoriesHeuristic:
        heuristic_file.write(category + "," + str(categoriesHeuristic[category]) + "\n")


def check_tasks():
    for task in tasksList:
        task.update_to_do()


def default_whitelist_file():
    whitelist_file = open("whitelist.txt", "w")

    for day in dayList:
        whitelist_file.write(day + "," + ",".join(allTimes) + "\n")


def default_object_file():
    open("taskFile.csv", "w")


def display_tasks():
    print("\n----------- ALL TASKS -----------\n")

    for i in tasksList:
        i.print_task()

    print("\n---------------------------------\n")
