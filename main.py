from datetime import datetime
import errno
import os
import defaultData
import pandas as pd
import convertJiraToList as cjtl
import jitaClockWork as jcw
from jitaClockWork import Jira_Clockwork
from dataFillClass import Data_fill
import keyTimeSheet as kt
from selenium.webdriver.chrome.webdriver import WebDriver


def main():
    try:
        while True:
            # input for jira clock work
            email_jira_clockwork = ""
            api_token = ""
            starting_at_str = "18/03/2024"
            ending_at_str = "30/03/2024"

            # input user password aware
            username_aware = ""
            password_aware = ""

            starting_at = datetime.strptime(
                starting_at_str, defaultData.df_string)
            ending_at = datetime.strptime(ending_at_str, defaultData.df_string)

            list_jira_Clockwork: list[Jira_Clockwork] = jcw.api_jira_clockwork(
                token=api_token, starting_at=starting_at, ending_at=ending_at, user_query=email_jira_clockwork)
            data_fill_list: list[Data_fill] = cjtl.convert_jira_to_list(list_jira_Clockwork)

            driver: WebDriver = kt.get_driver()
            kt.login_timeEntry(driver, username_aware, password_aware)
            data_fill_list = kt.main_fillDataTask(driver, data_fill_list)
            df_data_fill = pd.DataFrame([x.as_dict() for x in data_fill_list])
            
            #gen report
            start_time = datetime.now()
            date_today = start_time.strftime("%d%m%Y_%H%M%S")
            outputdir = ""
            fileName_report = f"Aware_time_sheet_report_{date_today}"
            pathName = "Report"
            # Create Path
            try:
                os.makedirs(pathName)
            except OSError as e:
                # If directory is exists use this directory
                if e.errno == errno.EEXIST:
                    pass

            outputdir = "{}/{}".format(pathName, fileName_report+".xlsx")
            df_data_fill.to_excel(excel_writer=outputdir, index=False)
            
            print("fill time Sheet Success you can check result ==> "+outputdir)
            driver.close()
            break
    except Exception as e:
        print("An error occurred Cannot Key time sheet. : "+str(e))

if __name__ == "__main__":
    main()
