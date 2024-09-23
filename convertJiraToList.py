from datetime import datetime, timedelta

import input_autoTimeSheet as iat
from dataFillClass import data_fill_jira
from jitaClockWork import jira_clockwork


def time_to_float(time_str: str) -> float:
    time_dt: datetime = datetime.strptime(time_str, "%H:%M")
    hour: int = time_dt.hour
    minute: int = time_dt.minute
    fraction: float = minute / 60
    result: float = round(number=hour + fraction, ndigits=4)
    return result


def seconds_to_timefloat(seconds: int) -> float:
    time_dt_str = str(object=timedelta(seconds=seconds))
    list_time_dt_str: list[str] = time_dt_str.split(sep=":")
    hour = int(list_time_dt_str[0])
    minute = int(list_time_dt_str[1])
    fraction: float = minute / 60
    result: float = round(number=hour + fraction, ndigits=4)
    return result


def determine_task(jitaclockwork: jira_clockwork) -> str:
    if (
        jitaclockwork.parent_summary.lower() == "all leaves"
        and jitaclockwork.issue_type == "Activity"
    ):
        return "Leave"
    elif (
        any(
            keyword in jitaclockwork.issue_summary.lower()
            for keyword in [
                "meeting",
                "scrum activity",
                "discussion",
                "ประชุม",
                "หารือ",
            ]
        )
        or jitaclockwork.issue_type == "Activity"
    ):
        return "Other"
    elif (
        "consult / support" in jitaclockwork.parent_summary.lower()
        or jitaclockwork.issue_summary.lower().startswith("support")
    ):
        return "Support"
    return iat.default_task


def determine_bill_type(jitaclockwork: jira_clockwork, task: str) -> str:
    if task == "Leave" or (
        jitaclockwork.issue_type == "Activity"
        and jitaclockwork.issue_summary == "ATS Activity"
    ):
        return "Non-Billable"
    elif jitaclockwork.comment.startswith("OT") and (
        jitaclockwork.issue_type == "Sub-task"
        or jitaclockwork.issue_type == "Management"
    ):
        return "Overtime"
    return "Regular"


def convert_jira_to_list(
    list_jitaclockwork: list[jira_clockwork],
) -> list[data_fill_jira]:
    data_fill_list: list[data_fill_jira] = []

    for jitaclockwork in list_jitaclockwork:
        hours: float = seconds_to_timefloat(seconds=jitaclockwork.time_spent_seconds)
        task: str = determine_task(jitaclockwork=jitaclockwork)
        bill_type: str = determine_bill_type(jitaclockwork=jitaclockwork, task=task)

        data_jira = data_fill_jira(
            customer=iat.default_customer,
            project=iat.default_project,
            role=iat.default_role,
            task=task,
            bill_type=bill_type,
            filldatetime=jitaclockwork.started_dt,
            hours=hours,
            status_message="",
            project_name=jitaclockwork.project_name,
            parent_summary=jitaclockwork.parent_summary,
            issue_Type=jitaclockwork.issue_type,
            issue_summary=jitaclockwork.issue_summary,
            comment=jitaclockwork.comment,
        )

        data_fill_list.append(data_jira)

    return data_fill_list
