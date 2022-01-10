import datetime
import json
from bs4 import BeautifulSoup
import requests


# Class that contains data of individual holidays
class Holiday:
    def __init__(self, name):
        # self.date cannot be set in init as a function call otherwise __dict__ cannot pick up property
        self.name = name

    def __repr__(self):
        return {self.name: str(self.date)}

    def __str__(self):
        # String output
        # Holiday output when printed.
        return f"{self.getName()} ({str(self.getDate())})"

    # Returns Holiday name
    def getName(self):
        return self.name

    # Returns Holiday date
    def getDate(self):
        return self.date

    # Checks if change attempt is of type datetime.date and sets it
    def setDate(self, dateinput):
        if not isinstance(dateinput, datetime.date):
            raise TypeError("Error:\nInvalid date. Please try again.")
        else:
            self.date = dateinput

    # Returns dictionary of Holiday data
    def toJson(self):
        return {"name": self.name, "date": str(self.date)}


# Class that contains a list of Holiday objects and functions to add/remove/modify/save data
class HolidayList:
    def __init__(self):
        self.innerHolidays = []

    def __repr__(self):
        return list(self.innerHolidays)

    # Checks if object being added is of type Holiday, if not already existing in the list, append and sort
    def addHoliday(self, holidayObj):
        if not isinstance(holidayObj, Holiday):
            raise TypeError("Object is not of type: Holiday")
        else:
            for item in self.getHolidays():
                if item.getName() == holidayObj.getName() and item.getDate() == holidayObj.getDate():
                    print(f"{holidayObj} already exists in the system.\n")
                    break
            else:
                self.innerHolidays.append(holidayObj)
                self.sortHolidays()
                return True
            return False

    # Goes through holiday list and finds holiday name and date combo then returns that object. If none, return none
    def findHoliday(self, holidayname, date=None):
        for holiday in self.getHolidays():
            if date is not None:
                if holiday.getName() == holidayname and holiday.getDate() == date:
                    return holiday
            else:
                if holiday.getName() == holidayname:
                    return holiday
        else:
            return None

    # Returns list containing Holiday objects
    def getHolidays(self):
        return self.innerHolidays

    # Finds holiday object matching given name and date and if exists, remove from list
    def removeHoliday(self, holidayname, holidaydate):
        holiday = self.findHoliday(holidayname, holidaydate)
        if holiday is not None:
            print(f"{holiday.getName()} has been removed from list.\n")
            self.innerHolidays.remove(holiday)
            return True
        else:
            return False

    # Read in given JSON file, fill holiday list with formatted Holiday objects from JSON
    def read_json(self, filelocation):
        with open(filelocation, "r") as holiday_file:
            file_json = json.load(holiday_file)

            for holiday in file_json["holidays"]:
                temp = Holiday(holiday["name"])
                temp.setDate(datetime.datetime.strptime(holiday["date"], '%Y-%m-%d').date())
                self.addHoliday(temp)

    # Create desired output for JSON and retrieve all holidays in JSON format. Write to desired output file location
    def save_to_json(self, filelocation):
        # Write out json file to selected file.
        dict_out = {"holidays": self.getAllHolidaysJSON()}

        with open(filelocation, "w") as outfile:
            try:
                json.dump(dict_out, outfile, indent=4)
                return True
            except TypeError:
                print("Unable to serialize objects. Something is broken...")
                return False

    # Web scrape holidays from timeanddate.com, format data and create Holiday objects and add to list
    def scrapeHolidays(self):
        def getHTML(url):
            try:
                response = requests.get(url)
                return response.text
            except requests.exceptions.ConnectionError:
                print("Bad connection. Check internet connection or URL used.")
                return None

        print("******************\nWeb Scrape Started\n******************\n")

        # Change XXXX to the year you want to use. Ex: Year 2022 would be...
        # https://www.timeanddate.com/calendar/print.html?year=2022&country=1&hol=33554809&df=1
        base_url = r'https://www.timeanddate.com/calendar/print.html?year=XXXX&country=1&hol=33554809&df=1'

        # allows for future use, takes current +/- 2 year range
        year = datetime.datetime.now().year
        year_range = list(range(year - 2, year + 3))

        # Go through calculated year range for previous 2, current, and future 2 years and get holidays for each.
        for year in year_range:
            html = getHTML(base_url.replace("XXXX", str(year)))  # URL can be manipulated to display different years
            if html is not None:
                soup = BeautifulSoup(html, 'html.parser')  # parse the webpage with html.parser from bs4
                table = soup.find('table', attrs={'class': 'cht lpad'})  # table class name found via inspect(Chrome)
                for item in table.find_all_next('tr'):
                    cells = item.find_all_next('td')
                    if cells[0].string is not None and cells[1].string is not None:
                        # cells[0] is date in format (Jan 1)
                        # cells[1] is name
                        temp = Holiday(cells[1].string)
                        temp.setDate(datetime.datetime.strptime(f"{cells[0].string} {str(year)}", "%b %d %Y").date())
                        self.addHoliday(temp)

        print("*******************\nWeb Scrape Complete\n*******************\n")

    # Return number of Holiday objects in the holiday list
    def numHolidays(self):
        return len(self.innerHolidays)

    # Return a list of holidays based on week number and year *Uses lambda
    def filter_holidays_by_week(self, year, week_number):
        holidays = list(filter(lambda holiday: holiday.getDate().isocalendar()[0] == int(year) and holiday.getDate().isocalendar()[1] == int(week_number), self.getHolidays()))
        return holidays

    # Prints out holidays from supplied list, if empty print statement
    def displayHolidaysInWeek(self, holidayList):
        if len(holidayList) > 0:
            for holiday in holidayList:
                print(holiday.__str__())
        else:
            print("There are no holidays in the system for the selected week.")

    # Runs get request on weatherapi-com.p.rapidapi.com/ with given date range and returns request
    def getAPIdata(self, year, weekNum):
        start = str(datetime.date.fromisocalendar(year, weekNum, 1))
        end = str(datetime.date.fromisocalendar(year, weekNum, 7))

        url = "https://weatherapi-com.p.rapidapi.com/history.json"

        querystring = {"q": "New York", "dt": start, "lang": "en", "end_dt": end}

        headers = {
            'x-rapidapi-host': "weatherapi-com.p.rapidapi.com",
            'x-rapidapi-key': "0956baa5cfmshd212347d210aff2p179c8bjsn3621ee88e1be"
        }

        return requests.get(url, headers=headers, params=querystring)

    # Handles API request and associates weather texts with matching dates of current weeks(week number) holidays
    def getWeather(self, year, weekNum):
        weather_dict = {}

        data = self.getAPIdata(year, weekNum)

        data_dict = data.json()

        for day_num in range(1, 8):
            try:
                weather_dict[str(datetime.date.fromisocalendar(year, weekNum, day_num))] = data_dict["forecast"]["forecastday"][day_num - 1]["day"]["condition"]["text"]
            except IndexError:
                weather_dict[str(datetime.date.fromisocalendar(year, weekNum, day_num))] = "No weather data"
        return weather_dict

    # Determines current week, obtains list of holidays in that week and asks user if weather should be included
    def viewCurrentWeek(self):
        year, week, day = datetime.date.today().isocalendar()
        current_weeks_holidays = self.filter_holidays_by_week(year, week)

        while True:
            show_weather = input("Would you like to see this week's weather? (New York) [y/n]: ")
            if show_weather in 'yn':
                break
            else:
                print("Bad input. Try again.")

        # If yes, use your getWeather function and display results
        if show_weather == "y":
            weather = self.getWeather(year, week)
            for holiday in current_weeks_holidays:
                print(f"{holiday.__str__()} - {weather[str(holiday.getDate())]}")
        else:
            for holiday in current_weeks_holidays:
                print(f"{holiday.__str__()}")

    # Sort HolidayList.innerHolidays by date
    def sortHolidays(self):
        self.innerHolidays.sort(key=lambda x: getattr(x, 'date'))

    # Returns a list containing each Holiday object in JSON format
    def getAllHolidaysJSON(self):
        ret = []
        for holiday in self.getHolidays():
            ret.append(holiday.toJson())
        return ret


# Functionality and Handling Functions
# ------------------------------------
# Gets user input for action to take on main menu and returns int value
def get_main_menu_input():
    lower_bound = 1
    upper_bound = 5

    while True:
        number_input = input("What would you like to do? ")
        if number_input.isnumeric():
            if int(number_input) in range(lower_bound, upper_bound + 1):
                break
            else:
                print(f"Input was out of bounds {lower_bound} - {upper_bound}. Please retry")
        else:
            print("Input was not an integer, please input an integer.")
    print("")
    return int(number_input)


# Handles function calling based on user input from get_main_menu_input
def mainMenu(holiday_list, output_file_location, num_init_holidays):
    def addHoliday():
        print("Add a Holiday\n=================")

        temp_holiday_obj = Holiday(input("Holiday: "))
        while True:
            holiday_date = input("Date: ")
            try:
                dt_holiday_date = datetime.datetime.strptime(holiday_date, "%Y-%m-%d").date()
                break
            except ValueError:
                print("\nError:\nInvalid date. Please try again. Format: YYYY-MM-DD\n")

        temp_holiday_obj.setDate(dt_holiday_date)
        if holiday_list.addHoliday(temp_holiday_obj):
            print(f"\nSuccess:\n{temp_holiday_obj} has been added to the holiday list.\n")

    def removeHoliday():
        print("Remove a Holiday\n=================")

        tempHolidayName = input("Holiday: ")
        tempHolidayDate = input("Date: ")
        if holiday_list.removeHoliday(tempHolidayName, datetime.datetime.strptime(tempHolidayDate, "%Y-%m-%d").date()):
            print(f"Success:\n{tempHolidayName} has been removed from the holiday list.\n")
        else:
            print(f"Error:\n{tempHolidayName} not found.\n")

    def saveHolidayList():
        print("Saving Holiday List\n===================")
        if input("Are you sure you want to save your changes? [y/n]: ") == 'y':
            if holiday_list.save_to_json(output_file_location):
                print("\nSuccess:\nYour changes have been saved.")
            else:
                print("\nFailed:\nCheck your output file path.")
        else:
            print("\nCanceled:\nHoliday list file save canceled")

    def viewHolidays():
        print("View Holidays\n===============")
        # Get year
        while True:
            user_input_year = input("Which year?: ")
            if user_input_year.isnumeric() and len(user_input_year) == 4:
                break
            else:
                print("Bad input, try again.")
        # Get week number
        while True:
            user_input_weeknum = input("Which week? [1-52, Leave blank for the current week]: ")
            if len(str(user_input_weeknum)) == 0:
                user_input_weeknum = 0
                break
            elif user_input_weeknum.isnumeric():
                if int(user_input_weeknum) in range(1, 53):
                    break
                else:
                    print("Number not in range 1 to 52. Try again.")
            else:
                print("Bad input, try again.")

        print("")
        # Call current week or specific week
        if user_input_weeknum == 0:
            holiday_list.viewCurrentWeek()
        elif int(user_input_weeknum) in range(1, 53):
            holiday_list.displayHolidaysInWeek(list(holiday_list.filter_holidays_by_week(user_input_year, int(user_input_weeknum))))

    # Checks if there are changes made to the size in the num_holidays
    def keepRunning():
        print("Exit\n===========")

        if holiday_list.numHolidays() != num_holidays:
            print("There are unsaved changes. Your changes will be lost unless you save!")

        check = input("Are you sure you want to exit? [y/n]: ")
        if check == 'y':
            print("\nGoodbye!")
            return False
        else:
            return True

    # Main Menu Start
    num_holidays = num_init_holidays
    keep_running = True
    while keep_running:
        print('Holiday Menu\n================')
        print('1. Add a Holiday\n2. Remove a Holiday\n3. Save Holiday List\n4. View Holidays\n5. Exit\n')

        selection = get_main_menu_input()

        if selection == 1:
            addHoliday()
        elif selection == 2:
            removeHoliday()
        elif selection == 3:
            saveHolidayList()
            num_holidays = holiday_list.numHolidays()
        elif selection == 4:
            viewHolidays()
        elif selection == 5:
            keep_running = keepRunning()

        print("")

    # Main Menu End
# ------------------------------------


def main(holidays_file_path, output_file_path):
    def startUp():
        # Load JSON file via HolidayList read_json function
        holiday_list.read_json(holidays_file_path)

        # Scrape additional holidays using HolidayList scrapeHolidays function
        holiday_list.scrapeHolidays()

        # Print start up statement
        print("Holiday Management\n=================")
        print(f"There are {holiday_list.numHolidays()} holidays stored in the system.\n")

    # Initialize HolidayList Object
    holiday_list = HolidayList()

    # Run startUp (Steps 2 & 3 plus statement)
    startUp()

    # Store initial number of holidays in holiday_list
    num_initial_holidays = holiday_list.numHolidays()

    # Run main menu that runs while loop for user to actively work on calendar until done
    mainMenu(holiday_list, output_file_path, num_initial_holidays)

    # * After exit, program ends here * #

# ------------------------------------------------------------------------------ #
# User Start Here - Change input file and output file directories as you please.
# Be sure that json input is in this structure:
# {
#  "holidays" : [
#      {
#          "name": "Holiday Name",
#          "date": "2022-01-01"
#      },
#      ...
# }


if __name__ == "__main__":
    input_holiday_file = 'holidays.json'
    output_holiday_file = "holidays_output.json"

    main(input_holiday_file, output_holiday_file)
