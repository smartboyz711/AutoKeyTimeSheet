
from datetime import datetime, timedelta
from dataFillClass import Data_fill
from dataFillClass import Description
import input_autoTimeSheet as iat
from jitaClockWork import Jira_Clockwork


def time_to_float(time_str: str) -> float:
    time_dt = datetime.strptime(time_str, '%H:%M')
    hour = time_dt.hour
    minute = time_dt.minute
    fraction = minute / 60
    result = round(hour + fraction, 4)
    return result

def seconds_to_timeFloat(seconds: int) -> float:
    time_dt_str = str(timedelta(seconds=seconds))
    list_time_dt_str = time_dt_str.split(":")
    hour = int(list_time_dt_str[0])
    minute = int(list_time_dt_str[1])
    fraction = minute / 60
    result = round(hour + fraction, 4)
    return result

def convert_jira_to_list(list_jitaClockwork: list[Jira_Clockwork]) -> list[Data_fill]:
    data_fill_list: list[Data_fill] = []
    if (len(list_jitaClockwork) > 0):
        for jitaClockwork in list_jitaClockwork:
            hours = seconds_to_timeFloat(jitaClockwork.timeSpentSeconds)
            customer = iat.default_customer
            project = iat.default_project
            role = iat.default_role
            task = ""
            billType = ""

            # cal task
            if (jitaClockwork.parent_summary.lower() == "all leaves" 
                and jitaClockwork.issue_type == "Activity") :
                task = "Leave"
            elif ("meeting" in jitaClockwork.issue_summary.lower()
                  or "scrum activity" in jitaClockwork.issue_summary.lower()
                  or "discussion" in jitaClockwork.issue_summary.lower()
                  or "คุย" in jitaClockwork.issue_summary.lower()
                  or "หารือ" in jitaClockwork.issue_summary.lower()
                  or jitaClockwork.issue_type == "Activity"):
                task = "Other"
            elif ("consult / support" in jitaClockwork.parent_summary.lower()
                  or jitaClockwork.issue_summary.lower().startswith("support")):
                task = "Support"
            else:
                task = iat.default_task
            # cal billType
            if (task == "Leave" 
                or (jitaClockwork.issue_type == "Activity" and jitaClockwork.issue_summary == "ATS Activity")):
                billType = "Non-Billable"
            elif (jitaClockwork.comment.startswith("OT") and jitaClockwork.issue_type == "Sub-task"):
                billType = "Overtime"
            else:
                billType = "Regular"

            description = Description(
                parent_summary=jitaClockwork.parent_summary,
                issue_Type=jitaClockwork.issue_type,
                issue_summary=jitaClockwork.issue_summary,
                comment=jitaClockwork.comment,
                billType=billType
            )

            data_fill = Data_fill(
                customer=customer,
                project=project,
                role=role,
                task=task,
                billType=billType,
                filldatetime=jitaClockwork.started_dt,
                hours=hours,
                description=description
            )

            data_fill_list.append(data_fill)
    return data_fill_list