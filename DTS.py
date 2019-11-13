# Class For Time. This class is immutable. Once it has been defined, the objects attributes do not change


class Time(object):
    def __init__(self, hour, minute):
        self.hour = int(hour)
        self.minute = int(minute)  # Hour and Minute attributes
        self.hourString = hour.rstrip('\n')
        self.minuteString = minute.rstrip('\n')

    def add_hours(self, hours_in):
        hours_out = self.hour + hours_in
        add_day = 0
        if hours_out > 24:
            hours_out -= 24
            add_day = 1
        if hours_out < 10:
            hours_out = "0" + str(hours_out)
        return Time(str(hours_out), str("00")), add_day

    def string_t(self):
        return self.hourString + ":" + self.minuteString

    def string_h(self):
        return self.hourString

    def print_t(self):
        print(self.hourString + ":" + self.minuteString)  # Print Time function


def time_diff(time_one, time_two):
    # calculate the difference between Times and save that as an object
    return int(time_two.hour - time_one.hour), int(time_two.minute - time_one.minute)


def check_leap(year):
    if year % 4 != 0:
        return 28
    elif year % 100 != 0:
        return 29
    elif year % 400 != 0:
        return 28
    else:
        return 29


# This module will calculate how many days it has been since January First of the earlier year for any Date inputted.
def date_diff(date_one, date_two):
    results = []
    for DateIn in [date_one, date_two]:
        year_diff = DateIn.year - date_one.year
        # (This is more efficient than in prototype 1 as it loops relative to how many years have passed since the
        # lower year only and works for years pre-2016)
        year_add = 0
        check_year = DateIn.year
        while year_diff > 0:
            check_year = check_year - 1
            if check_leap(check_year) == 28:
                year_add += 365
            else:
                year_add += 366
            year_diff -= 1
        feb = check_leap(DateIn.year)
        list_of_months = [31, feb, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        total = 0
        for i in range(0, DateIn.month - 1):
            total = total + list_of_months[i]
        total = total + DateIn.day + year_add
        results.append(total)
    return results[1] - results[0]
    # Two of these values are then subtracted from each other to calculate how many days it has been between two Dates/


class Date(object):
    def __init__(self, day, month, year):
        # Class For Dates #Day, Month and Year attributes. This class is immutable.
        #  Once it has been defined, the objects attributes do not change
        self.day = int(day)
        self.month = int(month)
        self.year = int(year)
        self.day_string = str(day).rstrip('\n')
        self.month_string = str(month).rstrip('\n')
        self.year_string = str(year).rstrip('\n')
        # Calculate and set the day of the week for the given Date
        day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        day = self.day
        month = self.month - 2
        year_end = int(self.year_string[2:5])
        year_start = int(str(self.year_string)[0:2])
        if month <= 0:
            month = month + 12
            year_end = year_end - 1
        f = day + (((13 * month) - 1) // 5) + year_end + year_end // 4 + year_start // 4 - 2 * year_start
        self.weekCalc = f // 7
        self.day_name = day_list[f % 7]

    def add_days(self, days_in):
        new_day = self.day
        new_month = self.month
        new_year = self.year
        new_day += days_in
        while True:
            feb = check_leap(new_year)
            list_of_months = [31, feb, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if new_day > list_of_months[(new_month - 1)]:
                new_day -= list_of_months[(new_month - 1)]
                new_month += 1
                if new_month > 12:
                    new_month -= 12
                    new_year += 1
            else:
                if new_day < 10:
                    new_day = "0" + str(new_day)
                if new_month < 10:
                    new_month = "0" + str(new_month)
                return (Date(str(new_day), str(new_month), str(new_year)))
                break

        return Date(str(new_day), str(new_month), str(new_year))

    def sub_days(self, days_in):
        new_day = self.day
        new_month = self.month
        new_year = self.year
        new_day -= days_in

        while True:
            feb = check_leap(new_year)
            list_of_months = [31, feb, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if new_day <= 0:
                if new_month - 2 < 0:
                    new_month += 12
                    new_year -= 1
                new_day += list_of_months[(new_month - 2)]
                new_month -= 1

            else:
                if new_day < 10:
                    new_day = "0" + str(new_day)
                if new_month < 10:
                    new_month = "0" + str(new_month)
                return Date(str(new_day), str(new_month), str(new_year))
                break

        return Date(str(new_day), str(new_month), str(new_year))

    def nearest_sunday(self):
        day_list = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        if self.day_name != "Sunday":
            return self.sub_days(day_list.index(self.day_name))
        else:
            return self

    def string_d(self):
        return self.day_string + "/" + self.month_string + "/" + self.year_string

    def print_d(self):
        print(self.day_name, end=" ")
        print(self.day_string + "/" + self.month_string + "/" + self.year_string)  # Print Date function


def minutes_until(date_one, time_one, date_two, time_two):
    days = date_diff(date_one, date_two)
    total_hours = days * 24
    hours, minutes = time_diff(time_one, time_two)
    total_hours += hours
    total_minutes = (total_hours * 60) + minutes
    return total_minutes


def date_time_comparison(date_one, time_one, date_two, time_two):
    if date_one.year > date_two.year:
        return True
    elif date_one.year == date_two.year and date_one.month > date_two.month:
        return True
    elif date_one.year == date_two.year and date_one.month == date_two.month and date_one.day > date_two.day:
        return True
    elif date_one.year == date_two.year and date_one.month == date_two.month and date_one.day == date_two.day and time_one.hour > time_two.hour:
        return True
    else:
        return False


def date_validation(date_one, date_two):
    if date_one.string_d() == date_two.string_d():
        return True
    if date_one.year > date_two.year:
        return True
    elif date_one.year == date_two.year and date_one.month > date_two.month:
        return True
    elif date_one.year == date_two.year and date_one.month == date_two.month and date_one.day > date_two.day:
        return True
    else:
        return False
