from datetime import datetime
import errno
import os
import defaultData
import pandas as pd
import jitaClockWork as jcw
from jitaClockWork import Jira_Clockwork

def main():
    try:

        # input for jira clock work
        api_token = ""
        starting_at_str = "18/03/2024"
        ending_at_str = "30/03/2024"

        List_email: list[str] = [
            "XXX@postbox.in.th",
            "XXX@postbox.in.th",
            "XXXX@postbox.in.th"
        ]

        starting_at = datetime.strptime(starting_at_str, defaultData.df_string)
        ending_at = datetime.strptime(ending_at_str, defaultData.df_string)

        list_jira_Clockwork: list[Jira_Clockwork] = jcw.api_jira_clockwork(
            token=api_token, starting_at=starting_at, ending_at=ending_at, list_user_query=List_email)

        df_jira_Clockwork = pd.DataFrame(
            [x.as_dict() for x in list_jira_Clockwork])
        
        #drop field statusMessage
        df_jira_Clockwork = df_jira_Clockwork.drop(columns=["statusMessage"])
        
        #new df summary
        df_summary = df_jira_Clockwork
        
        df_summary["started_dt"] = df_summary["started_dt"].dt.strftime(defaultData.df_string)
        
        #new field time_leave
        df_summary["time_leave"] = df_summary.loc[(df_summary["issue_type"] == "Activity") &
                                                  (df_summary["parent_summary"] == "All Leaves")]["timeSpentSeconds"] 
        
        #new field time_activity
        df_summary["time_activity"] =  df_summary.loc[(df_summary["issue_type"] == "Activity") &
                                                      (df_summary["parent_summary"] != "All Leaves")]["timeSpentSeconds"] 
        
        #new field time_ot
        df_summary["time_ot"] = df_summary.loc[(df_summary["issue_type"] == "Sub-task") & 
                                               (df_summary["comment"].str.startswith('OT'))]["timeSpentSeconds"]

        #gruop by result
        df_result = df_summary.groupby(["author_display_name", "author_emailAddress"], dropna=False)["timeSpentSeconds"].sum().reset_index(name="total_time")
        df_result["total_time_hours"] = df_result["total_time"] / 3600
        df_result["total_leave_time_hours"] = df_summary.groupby(["author_emailAddress"], dropna=False)["time_leave"].sum().reset_index(name="total_leave")["total_leave"] / 3600
        df_result["total_activity_time_hours"] = df_summary.groupby(["author_emailAddress"], dropna=False)["time_activity"].sum().reset_index(name="total_activity")["total_activity"] / 3600
        df_result["total_ot_time_hours"] = df_summary.groupby(["author_emailAddress"], dropna=False)["time_ot"].sum().reset_index(name="total_ot")["total_ot"] / 3600
        df_result["total_work_time_hours"] = df_result["total_time_hours"] - df_result["total_leave_time_hours"] - df_result["total_activity_time_hours"]
        
        # gen report
        start_time = datetime.now()
        date_today = start_time.strftime("%d%m%Y_%H%M%S")
        fileName_report = f"jira_summary_timeSheet_{starting_at.strftime(
            "%d%m%Y")}_to_{ending_at.strftime("%d%m%Y")}_by_{date_today}"
        pathName = "Report"
        outputdir = "{}/{}".format(pathName, fileName_report+".xlsx")
        # Create Path
        try:
            os.makedirs(pathName)
        except OSError as e:
            # If directory is exists use this directory
            if e.errno == errno.EEXIST:
                pass

        with pd.ExcelWriter(outputdir) as writer:
            df_summary.to_excel(writer, sheet_name="jira time sheet", index=False)
            df_result.to_excel(writer, sheet_name="summary time sheet", index=False)
            

    except Exception as e:
        print("An error occurred When gen report : "+str(e))


if __name__ == "__main__":
    main()
