import asyncio
from datetime import datetime
import errno
import os

import defaultData
import pandas as pd
import jitaClockWork as jcw
from jitaClockWork import Jira_Clockwork
import input_ReportAware as irt

def main():
    try:

        # input for jira clock work
        starting_at_str = irt.starting_at_str
        ending_at_str = irt.ending_at_str
        List_email = irt.List_email
        list_api_token = irt.list_api_token

        # begin #
        starting_at = datetime.strptime(starting_at_str, defaultData.df_string)
        ending_at = datetime.strptime(ending_at_str, defaultData.df_string)

        list_jira_Clockwork : list[Jira_Clockwork] = []
        
        if(list_api_token) :
            
            list_jira_Clockwork = asyncio.run(jcw.api_jira_clockwork_async_all_token(
                list_api_token, starting_at, ending_at, List_email))
            
        if(list_jira_Clockwork) :

            df_jira_Clockwork = pd.DataFrame([x.as_dict() for x in list_jira_Clockwork])
            
            df_jira_Clockwork = df_jira_Clockwork.drop_duplicates()
            
            df_jira_Clockwork["started_dt"] = df_jira_Clockwork["started_dt"].dt.strftime(defaultData.df_string)
            
            #new field timeSpentHours
            df_jira_Clockwork["timeSpentHours"] = df_jira_Clockwork["timeSpentSeconds"] / 3600
            
            #new field time_leave
            df_jira_Clockwork["time_leave"] = df_jira_Clockwork.loc[(df_jira_Clockwork["issue_type"] == "Activity") &
                                                    (df_jira_Clockwork["parent_summary"] == "All Leaves")]["timeSpentSeconds"] 
            
            #new field time_activity
            df_jira_Clockwork["time_activity"] =  df_jira_Clockwork.loc[(df_jira_Clockwork["issue_type"] == "Activity") &
                                                        (df_jira_Clockwork["issue_summary"] == "ATS Activity")]["timeSpentSeconds"]
            
            #new field time_ot
            df_jira_Clockwork["time_ot"] = df_jira_Clockwork.loc[(df_jira_Clockwork["issue_type"] == "Sub-task") & 
                                                (df_jira_Clockwork["comment"].str.startswith('OT'))]["timeSpentSeconds"]
            
            df_jira_Clockwork = df_jira_Clockwork.sort_values(by=['author_display_name', 'started_dt'])
            
            #pivot table
            df_pivot_table = pd.pivot_table(df_jira_Clockwork, values="timeSpentHours", 
                                            index=['project_name','parent_summary','issue_summary','comment'],
                                            columns=['author_display_name'], aggfunc="sum", fill_value=0)
            
            df_pivot_table = pd.DataFrame(df_pivot_table.to_records())
            user_columns  = df_pivot_table.columns[4:] 
            df_pivot_table["total_hours"] = df_pivot_table[user_columns].sum(axis=1)
            
            #grand total
            grand_total_row = {col: df_pivot_table[col].sum() for col in user_columns}
            grand_total_row['project_name'] = ''
            grand_total_row['parent_summary'] = ''
            grand_total_row['issue_summary'] = ''
            grand_total_row['comment'] = "Grand Total"
            grand_total_row['total_hours'] = df_pivot_table["total_hours"].sum()
            
            grand_total_df = pd.DataFrame(grand_total_row, index=[0])
            df_pivot_table_with_grand_total = pd.concat([df_pivot_table, grand_total_df], ignore_index=True)
            
            #group by result
            df_summary = df_jira_Clockwork.groupby(["author_display_name", "author_emailAddress"], dropna=False)["timeSpentSeconds"].sum().reset_index(name="total_time")
            df_summary["total_time_hours"] = df_summary["total_time"] / 3600
            df_summary["total_leave_time_hours"] = df_jira_Clockwork.groupby(["author_display_name", "author_emailAddress"], dropna=False)["time_leave"].sum().reset_index(name="total_leave")["total_leave"] / 3600
            df_summary["total_activity_time_hours"] = df_jira_Clockwork.groupby(["author_display_name", "author_emailAddress"], dropna=False)["time_activity"].sum().reset_index(name="total_activity")["total_activity"] / 3600
            df_summary["overtime_hour"] = df_jira_Clockwork.groupby(["author_display_name", "author_emailAddress"], dropna=False)["time_ot"].sum().reset_index(name="total_ot")["total_ot"] / 3600
            df_summary["overtime_day"] = df_summary["overtime_hour"] / 8
            df_summary["ais_sff_hour"] = df_summary["total_time_hours"] - df_summary["total_leave_time_hours"] - df_summary["total_activity_time_hours"] - df_summary["overtime_hour"]
            df_summary["ais_sff_day"] = df_summary["ais_sff_hour"] / 8
            df_summary["non_billable_hour"] = df_summary["total_leave_time_hours"] + df_summary["total_activity_time_hours"]
            df_summary["non_billable_day"] = df_summary["non_billable_hour"] / 8
            df_summary["summary_billable_day"] = df_summary["ais_sff_day"] + df_summary["overtime_day"]
            df_summary["working_days"] = (df_summary["total_time_hours"] - df_summary["overtime_hour"]) / 8
            
            #Set order of columns
            df_summary = df_summary[["author_display_name","author_emailAddress","ais_sff_hour","ais_sff_day","overtime_hour",
                                    "overtime_day","non_billable_hour","non_billable_day","summary_billable_day","working_days"]]
            
            # gen report
            start_time = datetime.now()
            date_today = start_time.strftime("%d%m%Y_%H%M%S")
            fileName_report = f"jira_summary_timeSheet_{starting_at.strftime("%d%m%Y")}_to_{ending_at.strftime("%d%m%Y")}_by_{date_today}"
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
                df_jira_Clockwork.to_excel(writer, sheet_name="jira time sheet", index=False)
                df_pivot_table_with_grand_total.to_excel(writer, sheet_name="pivot time sheet", index=False)
                df_summary.to_excel(writer, sheet_name="summary time sheet", index=False)
            
            print(f"result : Success in {datetime.now() - start_time} for Report : {outputdir}")

    except Exception as e:
        print("An error occurred When gen report : "+str(object=e))

