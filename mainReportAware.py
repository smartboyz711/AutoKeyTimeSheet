from datetime import datetime
import os
from typing import List
import logging
import numpy as np
import pandas as pd
import jitaClockWork as jcw
from jitaClockWork import jira_clockwork
import input_ReportAware as irt
import defaultData as dd

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def path_name_report(starting_at: datetime, ending_at: datetime) -> str:
    starting_at_str: str = starting_at.strftime("%b %Y")
    ending_at_str: str = ending_at.strftime("%b %Y")
    pathname = f"Report/{starting_at_str} - {ending_at_str}"
    if starting_at_str == ending_at_str:
        pathname: str = f"Report/{starting_at_str}"
    return pathname


def calculate_charge_ais(row):
    if row["time_activity"] > 0 or row["time_leave"] > 0:
        return 0
    elif row["time_ot"] > 0:
        return row["Manday 8 Hrs."] * 2
    else:
        return row["Manday 8 Hrs."]  # Default Manday 8 Hrs


def read_and_process_data(folder_path_jira: str) -> pd.DataFrame:
    """Read and process Jira data."""
    jira_df: pd.DataFrame = jcw.read_and_combine_excel_files(
        folder_path=folder_path_jira
    )
    list_jira_clockwork: List[jira_clockwork] = jcw.convert_dataframe_to_jira_clockwork(
        df=jira_df
    )
    df_ats_member: pd.DataFrame = jcw.read_and_combine_excel_files(
        prefix="List ATS Member"
    )

    if not list_jira_clockwork or df_ats_member.empty:
        raise ValueError("No Jira clockwork data available.")

    df_jira_clockwork = pd.DataFrame([x.as_dict() for x in list_jira_clockwork])
    df_jira_clockwork = df_jira_clockwork.drop_duplicates()

    # Merge with ATS members data
    df_jira_clockwork = pd.merge(
        df_jira_clockwork,
        df_ats_member,
        on="author_display_name",
        how="left",
        validate="many_to_many",
    )

    df_jira_clockwork["started_dt"] = df_jira_clockwork["started_dt"].dt.strftime(
        dd.df_string
    )
    df_jira_clockwork["time_spent_hours"] = (
        df_jira_clockwork["time_spent_seconds"] / 3600
    )

    # Add new fields based on conditions
    df_jira_clockwork["time_leave"] = df_jira_clockwork.loc[
        (df_jira_clockwork["parent_summary"] == "All Leaves")
        & (df_jira_clockwork["issue_type"] == "Activity")
    ]["time_spent_hours"]

    df_jira_clockwork["time_activity"] = df_jira_clockwork.loc[
        (df_jira_clockwork["parent_summary"] == "All Activity")
        & (df_jira_clockwork["issue_type"] == "Activity")
        & (df_jira_clockwork["issue_summary"] == "ATS Activity")
    ]["time_spent_hours"]

    df_jira_clockwork["time_ot"] = df_jira_clockwork.loc[
        (df_jira_clockwork["issue_type"].isin(["Sub-task", "Management"]))
        & (df_jira_clockwork["comment"].str.startswith("OT"))
    ]["time_spent_hours"]

    # Add additional columns
    df_jira_clockwork["Project-Key"] = (
        df_jira_clockwork["project_key"] + "-" + df_jira_clockwork["project_name"]
    )
    df_jira_clockwork["Task Detail"] = np.where(
        df_jira_clockwork["comment"].isna() | (df_jira_clockwork["comment"] == ""),
        df_jira_clockwork["issue_summary"],
        df_jira_clockwork["comment"],
    )

    df_jira_clockwork["Manday 8 Hrs."] = df_jira_clockwork["time_spent_hours"] / 8

    df_jira_clockwork["Charge AIS"] = df_jira_clockwork.apply(
        calculate_charge_ais, axis=1
    )

    df_jira_clockwork = df_jira_clockwork[
        [
            "author_display_name",
            "started_dt",
            "time_spent",
            "time_spent_seconds",
            "project_key",
            "project_name",
            "parent_key",
            "parent_summary",
            "issue_key",
            "issue_type",
            "issue_summary",
            "comment",
            "time_spent_hours",
            "time_leave",
            "time_activity",
            "time_ot",
            "Room",
            "Role",
            "Project-Key",
            "Task Detail",
            "Manday 8 Hrs.",
            "Charge AIS",
        ]
    ]

    return df_jira_clockwork


def create_pivot_table(df_jira_clockwork: pd.DataFrame) -> pd.DataFrame:
    """Create a pivot table from the Jira clockwork DataFrame."""
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

    # Flatten pivot table
    df_pivot_table = pd.DataFrame(df_pivot_table.to_records())
    df_pivot_table["total_hours"] = df_pivot_table.iloc[:, 5:].sum(axis=1)

    # Add grand total
    grand_total_row = {
        col: df_pivot_table[col].sum() for col in df_pivot_table.columns[5:]
    }
    grand_total_row["comment"] = "Grand Total"
    grand_total_row["total_hours"] = df_pivot_table["total_hours"].sum()
    grand_total_df = pd.DataFrame(grand_total_row, index=[0])
    df_pivot_table_with_grand_total = pd.concat(
        [df_pivot_table, grand_total_df], ignore_index=True
    )

    return df_pivot_table_with_grand_total


def create_summary_table(df_jira_clockwork: pd.DataFrame) -> pd.DataFrame:
    """Create summary table for time spent."""
    df_summary = (
        df_jira_clockwork.groupby("author_display_name", dropna=False)[
            "time_spent_hours"
        ]
        .sum()
        .reset_index(name="total_time_hours")
    )

    df_summary["total_leave_time_hours"] = (
        df_jira_clockwork.groupby("author_display_name", dropna=False)["time_leave"]
        .sum()
        .reset_index(name="total_leave")["total_leave"]
    )
    df_summary["total_activity_time_hours"] = (
        df_jira_clockwork.groupby("author_display_name", dropna=False)["time_activity"]
        .sum()
        .reset_index(name="total_activity")["total_activity"]
    )
    df_summary["overtime_hour"] = (
        df_jira_clockwork.groupby("author_display_name", dropna=False)["time_ot"]
        .sum()
        .reset_index(name="total_ot")["total_ot"]
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
        df_summary["total_leave_time_hours"] + df_summary["total_activity_time_hours"]
    )
    df_summary["non_billable_day"] = df_summary["non_billable_hour"] / 8
    df_summary["summary_billable_day"] = (
        df_summary["ais_sff_day"] + df_summary["overtime_day"]
    )
    df_summary["working_days"] = (
        df_summary["total_time_hours"] - df_summary["overtime_hour"]
    ) / 8

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

    # Add grand total row
    grand_total_row = {col: df_summary[col].sum() for col in df_summary.columns[1:]}
    grand_total_row["author_display_name"] = "Grand Total"
    grand_total_df = pd.DataFrame(grand_total_row, index=[0])
    df_summary = pd.concat([df_summary, grand_total_df], ignore_index=True)

    return df_summary


def save_to_excel(
    df_jira_clockwork: pd.DataFrame,
    df_pivot_table: pd.DataFrame,
    df_summary: pd.DataFrame,
    starting_at: datetime,
    ending_at: datetime,
):
    """Save processed DataFrames to an Excel file."""
    date_today = datetime.now().strftime("%d%m%Y_%H%M%S")
    filename_report = f"jira_summary_timeSheet_{starting_at.strftime('%d%m%Y')}_to_{ending_at.strftime('%d%m%Y')}_by_{date_today}"
    pathname = irt.folder_path_jira
    outputdir = f"{pathname}/{filename_report}.xlsx"

    # Ensure directory exists
    os.makedirs(pathname, exist_ok=True)

    with pd.ExcelWriter(outputdir) as writer:
        df_jira_clockwork.to_excel(writer, sheet_name="jira time sheet", index=False)
        df_pivot_table.to_excel(writer, sheet_name="pivot time sheet", index=False)
        df_summary.to_excel(writer, sheet_name="summary time sheet", index=False)

    logger.info(f"Report saved successfully to {outputdir}")


def main():
    try:
        # Start timer
        start_time = datetime.now()

        # Parse input dates
        starting_at = datetime.strptime(irt.starting_at_str, "%d/%m/%Y")
        ending_at = datetime.strptime(irt.ending_at_str, "%d/%m/%Y")

        # Process data
        df_jira_clockwork = read_and_process_data(irt.folder_path_jira)

        # Create reports
        df_pivot_table = create_pivot_table(df_jira_clockwork)
        df_summary = create_summary_table(df_jira_clockwork)

        # Save results to Excel
        save_to_excel(
            df_jira_clockwork, df_pivot_table, df_summary, starting_at, ending_at
        )

        # Log completion
        logger.info(f"Completed successfully in {datetime.now() - start_time}")

    except Exception as e:
        logger.error(f"An error occurred during report generation: {e}", exc_info=True)
