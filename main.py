import errno
import os

import pandas as pd
import convertFileToList as cftl
from dataFillClass import Data_fill
import keyTimeSheet as kt
from selenium.webdriver.chrome.webdriver import WebDriver


def print_header():
    print("================================================================================")
    print("Scirpt auto key time Sheet from jira excel file for newtimesheet.aware.co.th")
    print("Create By : theedanai Poomilamnao 04/02/2024")
    print("modify By : theedanai Poomilamnao 13/02/2024")
    print("================================================================================")
    print()


def print_line():
    print()
    print("================================================================================")
    print()


def main():
    print_header()
    try:
        # Input File Name
        while True:
            fileIn = input("Input excel File Name (FileName.xlsx) : ")
            # fileIn = "worklogs_2024-01-29_2024-02-05.xlsx"
            if (not (fileIn.endswith(".xlsx") or fileIn.endswith(".xls"))):
                print("FileName is not excel File Please try again.")
                print_line()
                continue
            try:
                file = pd.ExcelFile(fileIn)
            except Exception as e:
                print("Can't read excel file : "+str(e))
                print_line()
                continue
            print()

            username = input("Input Username : ")
            print()
            password = input("Input Password : ")

            data_fill_list: list[Data_fill] = cftl.convertFileToList(file)
            driver: WebDriver = kt.get_driver()
            kt.login_timeEntry(driver, username.strip(), password.strip())
            data_fill_list = kt.main_fillDataTask(driver, data_fill_list)

            df_data_fill = pd.DataFrame([x.as_dict() for x in data_fill_list])
            outputdir = ""
            fileName = fileIn.replace(".xlsx", "")
            fileName = fileName.replace(".xls", "")
            fileName_report = fileName+"_Report"
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

            print_line()
            print("fill time Sheet Success you can check result ==> "+outputdir)
            driver.close()
            break
    except Exception as e:
        print_line()
        print("An error occurred Cannot Key time sheet. : "+str(e))
    input("Press any key to exit...")


if __name__ == "__main__":
    main()
