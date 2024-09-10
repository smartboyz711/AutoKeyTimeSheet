from datetime import datetime
import os
from typing import List

import defaultData
import pandas as pd
import jitaClockWork as jcw
from jitaClockWork import jira_clockwork
import input_ReportAware as irt


def path_name_report(starting_at: datetime, ending_at: datetime) -> str:
    starting_at_str: str = starting_at.strftime("%b %Y")
    ending_at_str: str = ending_at.strftime("%b %Y")
    pathname = f"Report/{starting_at_str} - {ending_at_str}"
    if starting_at_str == ending_at_str:
        pathname: str = f"Report/{starting_at_str}"
    return pathname


def main():
    try:
        start_time: datetime = datetime.now()

        starting_at: datetime = datetime.strptime(irt.starting_at_str, "%d/%m/%Y")
        ending_at: datetime = datetime.strptime(irt.ending_at_str, "%d/%m/%Y")

        jira_df: pd.DataFrame = jcw.read_and_combine_excel_files(
            folder_path=irt.folder_path
        )
        list_jira_clockwork: List[jira_clockwork] = (
            jcw.convert_dataframe_to_jira_clockwork(df=jira_df)
        )

        if list_jira_clockwork:
            df_jira_clockwork = pd.DataFrame([x.as_dict() for x in list_jira_clockwork])

            df_jira_clockwork = df_jira_clockwork.drop_duplicates()

            df_jira_clockwork["started_dt"] = df_jira_clockwork[
                "started_dt"
            ].dt.strftime(defaultData.df_string)

            # new field timeSpentHours
            df_jira_clockwork["time_spent_hours"] = (
                df_jira_clockwork["time_spent_seconds"] / 3600
            )

            # new field time_leave
            df_jira_clockwork["time_leave"] = df_jira_clockwork.loc[
                (df_jira_clockwork["issue_type"] == "Activity")
                & (df_jira_clockwork["parent_summary"] == "All Leaves")
            ]["time_spent_seconds"]

            # new field time_activity
            df_jira_clockwork["time_activity"] = df_jira_clockwork.loc[
                (df_jira_clockwork["issue_type"] == "Activity")
                & (df_jira_clockwork["issue_summary"] == "ATS Activity")
            ]["time_spent_seconds"]

            # new field time_ot
            df_jira_clockwork["time_ot"] = df_jira_clockwork.loc[
                (
                    (df_jira_clockwork["issue_type"] == "Sub-task")
                    | (df_jira_clockwork["issue_type"] == "Management")
                )
                & (df_jira_clockwork["comment"].str.startswith("OT"))
            ]["time_spent_seconds"]

            # sort dataframe
            df_jira_clockwork = df_jira_clockwork.sort_values(
                by=["author_display_name", "started_dt"]
            )

            # pivot table
            df_pivot_table = pd.pivot_table(
                df_jira_clockwork,
                values="time_spent_hours",
                index=[
                    "project_key",
                    "project_name",
                    "parent_summary",
                    "issue_summary",
                    "comment",
                ],
                columns=["author_display_name"],
                aggfunc="sum",
                fill_value=0,
            )

            df_pivot_table = pd.DataFrame(df_pivot_table.to_records())
            user_columns: pd.Index[str] = df_pivot_table.columns[5:]
            df_pivot_table["total_hours"] = df_pivot_table[user_columns].sum(axis=1)

            # grand total
            grand_total_row = {col: df_pivot_table[col].sum() for col in user_columns}
            grand_total_row["comment"] = "Grand Total"
            grand_total_row["total_hours"] = df_pivot_table["total_hours"].sum()

            grand_total_df = pd.DataFrame(grand_total_row, index=[0])
            df_pivot_table_with_grand_total = pd.concat(
                [df_pivot_table, grand_total_df], ignore_index=True
            )

            # group by result
            df_summary = (
                df_jira_clockwork.groupby(["author_display_name"], dropna=False)[
                    "time_spent_seconds"
                ]
                .sum()
                .reset_index(name="total_time")
            )
            df_summary["total_time_hours"] = df_summary["total_time"] / 3600
            df_summary["total_leave_time_hours"] = (
                df_jira_clockwork.groupby(["author_display_name"], dropna=False)[
                    "time_leave"
                ]
                .sum()
                .reset_index(name="total_leave")["total_leave"]
                / 3600
            )
            df_summary["total_activity_time_hours"] = (
                df_jira_clockwork.groupby(["author_display_name"], dropna=False)[
                    "time_activity"
                ]
                .sum()
                .reset_index(name="total_activity")["total_activity"]
                / 3600
            )
            df_summary["overtime_hour"] = (
                df_jira_clockwork.groupby(["author_display_name"], dropna=False)[
                    "time_ot"
                ]
                .sum()
                .reset_index(name="total_ot")["total_ot"]
                / 3600
            )
            df_summary["overtime_day"] = df_summary["overtime_hour"] / 8
            df_summary["ais_sff_hour"] = (
                df_summary["total_time_hours"]
                - df_summary["total_leave_time_hours"]
                - df_summary["total_activity_time_hours"]
                - df_summary["overtime_hour"]
            )
            df_summary["ais_sff_day"] = df_summary["ais_sff_hour"] / 8
            df_summary["non_billable_hour"] = (
                df_summary["total_leave_time_hours"]
                + df_summary["total_activity_time_hours"]
            )
            df_summary["non_billable_day"] = df_summary["non_billable_hour"] / 8
            df_summary["summary_billable_day"] = (
                df_summary["ais_sff_day"] + df_summary["overtime_day"]
            )
            df_summary["working_days"] = (
                df_summary["total_time_hours"] - df_summary["overtime_hour"]
            ) / 8

            # Set order of columns
            df_summary = df_summary[
                [
                    "author_display_name",
                    "ais_sff_hour",
                    "ais_sff_day",
                    "overtime_hour",
                    "overtime_day",
                    "non_billable_hour",
                    "non_billable_day",
                    "summary_billable_day",
                    "working_days",
                ]
            ]

            user_columns: pd.Index[str] = df_summary.columns[1:]
            grand_total_row_summary = {
                col: df_summary[col].sum() for col in user_columns
            }
            grand_total_row_summary["author_display_name"] = "Grand Total"
            grand_total_row_summary_df = pd.DataFrame(
                grand_total_row_summary, index=[0]
            )
            df_summary = pd.concat(
                [df_summary, grand_total_row_summary_df], ignore_index=True
            )

            date_today = start_time.strftime("%d%m%Y_%H%M%S")
            filename_report = f"jira_summary_timeSheet_{starting_at.strftime("%d%m%Y")}_to_{ending_at.strftime("%d%m%Y")}_by_{date_today}"
            pathname = path_name_report(starting_at, ending_at)
            outputdir = f"{pathname}/{filename_report}.xlsx"
            # Create Path

            os.makedirs(pathname, exist_ok=True)

            with pd.ExcelWriter(outputdir) as writer:
                df_jira_clockwork.to_excel(
                    writer, sheet_name="jira time sheet", index=False
                )
                df_pivot_table_with_grand_total.to_excel(
                    writer, sheet_name="pivot time sheet", index=False
                )
                df_summary.to_excel(
                    writer, sheet_name="summary time sheet", index=False
                )

            print(
                f"result : Success in {datetime.now() - start_time} for Report : {outputdir}"
            )

    except Exception as e:
        print(f"An error occurred When gen report : {e.args}")
