
from datetime import datetime
from pandas import ExcelFile
import pandas as pd
from dataFillClass import Data_fill
from dataFillClass import Description
import defaultData


def time_to_float(time_str: str) -> float:
    # parse the time string into a datetime object
    time_dt = datetime.strptime(time_str, '%H:%M')
    # get the hour and minute values
    hour = time_dt.hour
    minute = time_dt.minute
    # divide the minute by 60 to get the fractional part
    fraction = minute / 60
    # add the hour and the fraction to get the float value
    result = round(hour + fraction, 4)
    return result


def convertFileToList(file: ExcelFile) -> list[Data_fill]:
    data_fill_list: list[Data_fill] = []
    for sheetname in file.sheet_names:
        datasheet = file.parse(sheetname)
        datasheet.columns = datasheet.columns.str.strip()
        datasheet.columns = datasheet.columns.str.replace(' ', '_')
        for tp_datasheet in datasheet.itertuples(index=False):
            customer = defaultData.default_customer
            project = defaultData.default_project
            role = defaultData.default_role
            task = ""
            billType = ""
            parent_key = ""
            parent_summary = ""
            issue_Type = ""
            issue_summary = ""
            comment = ""
            filldatetime: datetime = datetime.now()
            hours: float = 1
            message = []
            for column in datasheet.columns:
                match column:
                    case "Parent_Key":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            parent_key = str(
                                getattr(tp_datasheet, column)).strip()
                        else:
                            parent_key = ""
                            message.append("Parent Key is required field.")
                    case "Parent_Summary":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            parent_summary = str(
                                getattr(tp_datasheet, column)).strip()
                        else:
                            parent_summary = ""
                            message.append("Parent Summary is required field.")
                    case "Issue_Type":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            issue_Type = str(
                                getattr(tp_datasheet, column)).strip()
                        else:
                            issue_Type = ""
                            message.append("Issue Type is required field.")
                    case "Issue_Summary":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            issue_summary = str(
                                getattr(tp_datasheet, column)).strip()
                        else:
                            issue_summary = ""
                            message.append("Issue Summary is required field.")
                    case "Comment":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            comment = str(
                                getattr(tp_datasheet, column)).strip()
                    case "Started_at":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            try:
                                started_at_str = getattr(tp_datasheet, column)
                                filldatetime = datetime.fromisoformat(
                                    started_at_str).replace(tzinfo=None)
                            except Exception as e:
                                message.append(
                                    f"Can't Convert datetime (Started at) Please enter in iso format : {e}")
                        else:
                            message.append("Started at is required field.")
                    case "Time_spent":
                        if (not pd.isnull(getattr(tp_datasheet, column))):
                            try:
                                hours = time_to_float(
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
            
            if ("all leaves" in parent_summary.lower()):
                task = "Leave"
            elif ("meeting" in issue_summary.lower()
                or "scrum activity" in issue_summary.lower()
                or "discussion" in issue_summary.lower()
                or "คุย" in issue_summary.lower()
                or (parent_summary == "Meeting not related to software development" 
                    and comment == "Internal ATS Activity")):
                task = "Other"
            elif ("consult / support" in parent_summary.lower()
                or issue_summary.lower().startswith("support")):
                task = "Support"
            else:
                task = defaultData.default_task

            if (task == "Leave" 
                or (parent_summary == "Meeting not related to software development" 
                    and comment == "Internal ATS Activity")) : 
                billType = "Non-Billable"
            elif (comment.startswith("OT")) :
                billType = "Overtime"
            else:
                billType = "Regular"

            description = Description (
                parent_key=parent_key,
                parent_summary=parent_summary,
                issue_Type=issue_Type,
                issue_summary=issue_summary,
                comment=comment
            )

            data_fill = Data_fill (
                customer=customer,
                project=project,
                role=role,
                task=task,
                billType=billType,
                filldatetime=filldatetime,
                hours=hours,
                description=description,
                statusMessage=statusMessage
            )

            data_fill_list.append(data_fill)
    return data_fill_list
