import logging
import os
from datetime import datetime
from logging import Logger
from typing import List

import numpy as np
import pandas as pd
from pandas import DataFrame

import defaultData as dd
import input_ReportAware as irt
import jitaClockWork as jcw
from jitaClockWork import jira_clockwork

# Setup logger
logging.basicConfig(level=logging.INFO)
logger: Logger = logging.getLogger(__name__)


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


def read_and_process_data(folder_path_jira: str) -> DataFrame:
    """Read and process Jira data."""
    jira_df: DataFrame = jcw.read_and_combine_excel_files(folder_path=folder_path_jira)
    list_jira_clockwork: List[jira_clockwork] = jcw.convert_dataframe_to_jira_clockwork(
        df=jira_df
    )
    df_ats_member: DataFrame = jcw.read_and_combine_excel_files(
        prefix="List ATS Member"
    )

    if not list_jira_clockwork or df_ats_member.empty:
        raise ValueError("No Jira clockwork data available.")

    df_jira_clockwork = DataFrame([x.as_dict() for x in list_jira_clockwork])
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
            "Room",
            "Role",
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
            "Project-Key",
            "Task Detail",
            "time_spent_hours",
            "time_leave",
            "time_activity",
            "time_ot",
            "Manday 8 Hrs.",
            "Charge AIS",
        ]
    ]
    
    df_jira_clockwork = df_jira_clockwork.sort_values(by=["author_display_name","started_dt"], ascending=True)

    return df_jira_clockwork


def create_pivot_table(df_jira_clockwork: DataFrame) -> DataFrame:
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
    df_pivot_table = DataFrame(df_pivot_table.to_records())
    df_pivot_table["total_hours"] = df_pivot_table.iloc[:, 5:].sum(axis=1)

    # Add grand total
    grand_total_row = {
        col: df_pivot_table[col].sum() for col in df_pivot_table.columns[5:]
    }
    grand_total_row["comment"] = "Grand Total"
    grand_total_row["total_hours"] = df_pivot_table["total_hours"].sum()
    grand_total_df = DataFrame(grand_total_row, index=[0])
    df_pivot_table_with_grand_total = pd.concat(
        [df_pivot_table, grand_total_df], ignore_index=True
    )

    return df_pivot_table_with_grand_total


def create_pivot_table_charge_ais(df_jira_clockwork: DataFrame) -> DataFrame:
    """Create a pivot table from the Jira clockwork DataFrame."""
    df_pivot_table = pd.pivot_table(
        df_jira_clockwork,
        values="Charge AIS",
        index=["Room", "Project-Key", "Task Detail"],
        columns=["author_display_name"],
        aggfunc="sum",
        fill_value=0,
    )

    # Flatten pivot table
    df_pivot_table = DataFrame(df_pivot_table.to_records())
    df_pivot_table["total_days"] = df_pivot_table.iloc[:, 3:].sum(axis=1)

    # Add grand total
    grand_total_row = {
        col: df_pivot_table[col].sum() for col in df_pivot_table.columns[3:]
    }
    grand_total_row["Task Detail"] = "Grand Total"
    grand_total_row["total_days"] = df_pivot_table["total_days"].sum()
    grand_total_df = DataFrame(grand_total_row, index=[0])
    df_pivot_table_with_grand_total = pd.concat(
        [df_pivot_table, grand_total_df], ignore_index=True
    )
    return df_pivot_table_with_grand_total


def create_summary_table(df_jira_clockwork: DataFrame) -> DataFrame:
    """Create summary table for time spent."""
    df_summary = (
        df_jira_clockwork.groupby(
            ["author_display_name", "Room", "Role"], dropna=False
        )["time_spent_hours"]
        .sum()
        .reset_index(name="total_time_hours")
    )

    df_summary["total_leave_time_hours"] = (
        df_jira_clockwork.groupby(
            ["author_display_name", "Room", "Role"], dropna=False
        )["time_leave"]
        .sum()
        .reset_index(name="total_leave")["total_leave"]
    )
    df_summary["total_activity_time_hours"] = (
        df_jira_clockwork.groupby(
            ["author_display_name", "Room", "Role"], dropna=False
        )["time_activity"]
        .sum()
        .reset_index(name="total_activity")["total_activity"]
    )

    df_summary["overtime_hour"] = (
        df_jira_clockwork.groupby(
            ["author_display_name", "Room", "Role"], dropna=False
        )["time_ot"]
        .sum()
        .reset_index(name="total_ot")["total_ot"]
    )

    df_summary["total_charge_ais"] = (
        df_jira_clockwork.groupby(
            ["author_display_name", "Room", "Role"], dropna=False
        )["Charge AIS"]
        .sum()
        .reset_index(name="total_charge_ais")["total_charge_ais"]
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
            "Room",
            "Role",
            "ais_sff_hour",
            "ais_sff_day",
            "overtime_hour",
            "overtime_day",
            "non_billable_hour",
            "non_billable_day",
            "summary_billable_day",
            "working_days",
            "total_charge_ais"
        ]
    ].sort_values(["Room", "Role"])

    # Add grand total row
    grand_total_row = {col: df_summary[col].sum() for col in df_summary.columns[3:]}
    grand_total_row["Role"] = "Grand Total"
    grand_total_df = DataFrame(grand_total_row, index=[0])
    df_summary = pd.concat([df_summary, grand_total_df], ignore_index=True)

    return df_summary


def save_to_excel(
    df_jira_clockwork: DataFrame,
    df_pivot_table: DataFrame,
    df_pivot_charge_ais: DataFrame,
    df_summary: DataFrame,
    starting_at: datetime,
    ending_at: datetime,
    folder_path_jita: str = "",
):
    """Save processed DataFrames to an Excel file."""
    date_today = datetime.now().strftime("%d%m%Y_%H%M%S")
    filename_report = f"jira_summary_timeSheet_{starting_at.strftime('%d%m%Y')}_to_{ending_at.strftime('%d%m%Y')}_by_{date_today}"
    pathname = folder_path_jita
    outputdir = f"{pathname}/{filename_report}.xlsx"

    # Ensure directory exists
    os.makedirs(pathname, exist_ok=True)

    with pd.ExcelWriter(outputdir) as writer:
        df_jira_clockwork.to_excel(writer, sheet_name="jira time sheet", index=False)
        df_pivot_table.to_excel(writer, sheet_name="pivot time sheet", index=False)
        df_pivot_charge_ais.to_excel(writer, sheet_name="pivot charge ais", index=False)
        df_summary.to_excel(writer, sheet_name="summary time sheet", index=False)

    logger.info(f"Report saved successfully to {outputdir}")


def main():
    try:
        # Start timer
        start_time: datetime = datetime.now()

        # Parse input dates
        starting_at: datetime = datetime.strptime(irt.starting_at_str, "%d/%m/%Y")
        ending_at: datetime = datetime.strptime(irt.ending_at_str, "%d/%m/%Y")

        # Process data
        df_jira_clockwork: DataFrame = read_and_process_data(
            folder_path_jira=irt.folder_path_jira
        )

        # Create reports
        df_pivot_table: DataFrame = create_pivot_table(df_jira_clockwork)
        df_pivot_charge_ais: DataFrame = create_pivot_table_charge_ais(
            df_jira_clockwork
        )
        df_summary: DataFrame = create_summary_table(df_jira_clockwork)

        # Save results to Excel
        save_to_excel(
            df_jira_clockwork=df_jira_clockwork,
            df_pivot_table=df_pivot_table,
            df_pivot_charge_ais=df_pivot_charge_ais,
            df_summary=df_summary,
            starting_at=starting_at,
            ending_at=ending_at,
            folder_path_jita=irt.folder_path_jira,
        )

        # Log completion
        logger.info(f"Completed successfully in {datetime.now() - start_time}")

    except Exception as e:
        logger.error(f"An error occurred during report generation: {e}", exc_info=True)
