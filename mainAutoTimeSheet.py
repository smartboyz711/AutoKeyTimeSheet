from datetime import datetime
import errno
import os
import defaultData
import pandas as pd
import convertJiraToList as cjtl
import jitaClockWork as jcw
from jitaClockWork import jira_clockwork
from dataFillClass import data_fill_jira
import keyTimeSheet as kt
from selenium.webdriver.chrome.webdriver import WebDriver
import input_autoTimeSheet as iat


def main():
    try:
        
        # input for jira clock work
        email_jira_clockwork = iat.email_jira_clockwork
        api_token = iat.api_token
        starting_at_str = iat.starting_at_str
        ending_at_str = iat.ending_at_str

        # input user password aware
        username_aware = iat.username_aware
        password_aware = iat.password_aware
                
        list_email_jira_clockwork : list[str] = []
        list_email_jira_clockwork.append(email_jira_clockwork)
        starting_at = datetime.strptime(
            starting_at_str, defaultData.df_string)
        ending_at = datetime.strptime(ending_at_str, defaultData.df_string)

        list_jira_clockwork: list[jira_clockwork] = jcw.api_jira_clockwork(
            token=api_token, starting_at=starting_at, ending_at=ending_at, list_user_query=list_email_jira_clockwork)
        
        if(len(list_jira_clockwork) > 0) :
            
            data_fill_list: list[data_fill_jira] = cjtl.convert_jira_to_list(list_jitaclockwork=list_jira_clockwork)
            driver: WebDriver = kt.get_driver()
            kt.login_time_entry(driver, username_aware, password_aware)
            data_fill_list = kt.main_filldatatask(driver, data_fill_list)
            
            df_data_fill = pd.DataFrame([x.as_dict() for x in data_fill_list])
            
            #gen report
            start_time = datetime.now()
            date_today = start_time.strftime("%d%m%Y_%H%M%S")
            filename_report = f"Aware_time_sheet_report_{date_today}"
            pathname = "Report"
            # Create Path
            try:
                os.makedirs(pathname)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    print(f"directory is exists use this directory /{pathname}")

            outputdir = "{}/{}".format(pathname, filename_report+".xlsx")
            df_data_fill.to_excel(excel_writer=outputdir, index=False)
            
            print("fill time Sheet Success you can check result ==> "+outputdir)
            driver.close()
        
    except Exception as e:
        print(f"An error occurred Cannot Key time sheet. : {e})")