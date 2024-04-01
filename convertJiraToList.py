
from datetime import datetime, timedelta
from pandas import ExcelFile
import pandas as pd
from dataFillClass import Data_fill
from dataFillClass import Description
import defaultData
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
            customer = defaultData.default_customer
            project = defaultData.default_project
            role = defaultData.default_role
            task = ""
            billType = ""

            # cal task
            if ("all leaves" in jitaClockwork.parent_summary.lower()):
                task = "Leave"
            elif ("meeting" in jitaClockwork.issue_summary.lower()
                  or "scrum activity" in jitaClockwork.issue_summary.lower()
                  or "discussion" in jitaClockwork.issue_summary.lower()
                  or "คุย" in jitaClockwork.issue_summary.lower()):
                task = "Other"
            elif ("consult / support" in jitaClockwork.parent_summary.lower()
                  or jitaClockwork.issue_summary.lower().startswith("support")):
                task = "Support"
            else:
                task = defaultData.default_task
            # cal billType
            if (task == "Leave" or jitaClockwork.issue_type == "Activity"):
                billType = "Non-Billable"
            elif (jitaClockwork.comment.startswith("OT") and jitaClockwork.issue_type == "Sub-task"):
                billType = "Overtime"
            else:
                billType = "Regular"

            description = Description(
                parent_summary=jitaClockwork.parent_summary,
                issue_Type=jitaClockwork.issue_type,
                issue_summary=jitaClockwork.issue_summary,
                comment=jitaClockwork.comment
            )

            data_fill = Data_fill(
                customer=customer,
                project=project,
                role=role,
                task=task,
                billType=billType,
                filldatetime=jitaClockwork.started_dt,
                hours=hours,
                description=description,
                statusMessage=jitaClockwork.statusMessage
            )

            data_fill_list.append(data_fill)
    return data_fill_list

def convert_excel_to_list(file: ExcelFile) -> list[Data_fill]:
    data_fill_list: list[Data_fill] = []
    list_jitaClockwork: list[Jira_Clockwork] = []
    for sheetname in file.sheet_names:
        datasheet = file.parse(sheetname)
        datasheet.columns = datasheet.columns.str.strip()
        datasheet.columns = datasheet.columns.str.lower()
        datasheet.columns = datasheet.columns.str.replace(" ", "_")
        datasheet.columns = datasheet.columns.str.replace("(", "")
        datasheet.columns = datasheet.columns.str.replace(")", "")
        for tp_datasheet in datasheet.itertuples(index=False):
            parent_summary = ""
            issue_type = ""
            issue_summary = ""
            comment = ""
            started_at = datetime.now()
            timeSpentSeconds = 0
            message = []
            for column in datasheet.columns:
                match column:
                    case "parent_summary":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            parent_summary = str(
                                getattr(tp_datasheet, column)).strip()
                        else:
                            parent_summary = ""
                            message.append("Parent Summary is required field.")
                    case "issue_type":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            issue_type = str(
                                getattr(tp_datasheet, column)).strip()
                        else:
                            issue_type = ""
                            message.append("Issue Type is required field.")
                    case "issue_summary":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            issue_summary = str(
                                getattr(tp_datasheet, column)).strip()
                        else:
                            issue_summary = ""
                            message.append("Issue Summary is required field.")
                    case "comment":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            comment = str(
                                getattr(tp_datasheet, column)).strip()
                    case "started_at":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            try:
                                started_at_str = getattr(tp_datasheet, column)
                                started_at = datetime.fromisoformat(
                                    started_at_str).replace(tzinfo=None)
                            except Exception as e:
                                message.append(
                                    f"Can't Convert datetime (Started at) Please enter in iso format : {e}")
                        else:
                            message.append("Started at is required field.")
                    case "time_spent_seconds":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            try:
                                timeSpentSeconds = int(
                                    getattr(tp_datasheet, column))
                            except Exception as e:
                                message.append(
                                    f"Can't Convert time for (Time spent) field : {e}")
                        else:
                            message.append("Time spent is required field.")

            if (len(message) > 0):
                statusMessage = ", ".join(message)
            else:
                statusMessage = ""

            jira_Clockwork = Jira_Clockwork(
                author_display_name=getattr(tp_datasheet, "author"),
                author_emailAddress="",
                started_dt=started_at,
                project_key=getattr(tp_datasheet, "project_key"),
                project_name=getattr(tp_datasheet, "project_name"),
                parent_key=getattr(tp_datasheet, "parent_key"),
                parent_summary=parent_summary,
                issue_key=getattr(tp_datasheet, "issue_key"),
                issue_type=issue_type,
                issue_summary=issue_summary,
                comment=comment,
                timeSpentSeconds=timeSpentSeconds,
                statusMessage=statusMessage
            )

            list_jitaClockwork.append(jira_Clockwork)
    data_fill_list = convert_jira_to_list(list_jitaClockwork)
    return data_fill_list
