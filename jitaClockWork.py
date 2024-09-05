import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Union
import requests
from requests import Response
import defaultData
import logging
import pandas as pd
import glob


@dataclass
class jira_clockwork:
    author_display_name: str
    author_email_address: str
    started_dt: datetime
    time_spent: str
    time_spent_seconds: int
    project_key: str
    project_name: str
    parent_key: str
    parent_summary: str
    issue_key: str
    issue_type: str
    issue_summary: str
    comment: str

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items()}


def api_jira_clockwork(
    token: str, starting_at: datetime, ending_at: datetime, list_user_query: List[str]
) -> List[jira_clockwork]:
    jira_clockwork_url = "https://api.clockwork.report/v1/worklogs?expand=authors,issues,epics,emails,worklogs,comments"
    list_jira_clockwork: List[jira_clockwork] = []

    if not all([token, starting_at, ending_at, list_user_query]):
        return list_jira_clockwork

    headers_api: Dict[str, str] = {"Authorization": f"Token {token}"}

    criteria_data = {
        "starting_at": starting_at.strftime("%Y-%m-%d"),
        "ending_at": ending_at.strftime("%Y-%m-%d"),
        "user_query[]": list_user_query,
    }

    try:
        response: Response = requests.get(
            url=jira_clockwork_url,
            headers=headers_api,
            params=criteria_data,
            timeout=60,
        )
        response.raise_for_status()

        worklogs = response.json()
        if not worklogs:
            return list_jira_clockwork

        for data in worklogs:
            try:
                author_display_name = data["author"]["displayName"]
                author_email_address = data["author"]["emailAddress"]
                project_key = data["issue"]["fields"]["project"]["key"]
                project_name = data["issue"]["fields"]["project"]["name"].strip()
                parent_key = data["issue"]["fields"].get("parent", {}).get("key", "")
                parent_summary = (
                    data["issue"]["fields"]
                    .get("parent", {})
                    .get("fields", {})
                    .get("summary", "")
                    .strip()
                )
                issue_key = data["issue"]["key"]
                issue_type = data["issue"]["fields"]["issuetype"]["name"]
                issue_summary = data["issue"]["fields"]["summary"].strip()
                time_spent = data["timeSpent"]
                time_spent_seconds = data["timeSpentSeconds"]
                started_dt: datetime = (
                    datetime.fromisoformat(data["started"]).astimezone(
                        defaultData.thailand_tz
                    ).replace(tzinfo=None)
                    if "started" in data
                    else datetime.min
                )
                comment = data.get("comment", "").strip()

                jira_data = jira_clockwork(
                    author_display_name=author_display_name,
                    author_email_address=author_email_address,
                    started_dt=started_dt,
                    project_key=project_key,
                    project_name=project_name,
                    parent_key=parent_key,
                    parent_summary=parent_summary,
                    issue_key=issue_key,
                    issue_type=issue_type,
                    issue_summary=issue_summary,
                    comment=comment,
                    time_spent=time_spent,
                    time_spent_seconds=time_spent_seconds,
                )
                list_jira_clockwork.append(jira_data)

            except KeyError as e:
                logging.warning(f"Missing key in data: {e}")
                continue
            except Exception as e:
                logging.error(f"Error processing worklog data: {e}")
                continue

        list_jira_clockwork.sort(key=lambda x: (x.author_display_name, x.started_dt))

    except requests.RequestException as e:
        logging.error(f"api_jira_clockwork Request error: {e}")
    except Exception as e:
        logging.error(f"api_jira_clockwork Unexpected error: {e}")

    return list_jira_clockwork


async def api_jira_clockwork_async(
    token: str, starting_at: datetime, ending_at: datetime, list_user_query: List[str]
) -> List[jira_clockwork]:
    return await asyncio.to_thread(
        api_jira_clockwork, token, starting_at, ending_at, list_user_query
    )


async def api_jira_clockwork_async_all_token(
    list_token: List[str],
    starting_at: datetime,
    ending_at: datetime,
    list_user_query: List[str],
) -> List[jira_clockwork]:
    list_jira_clockwork: List[jira_clockwork] = []
    if list_token:
        tasks = [
            api_jira_clockwork_async(
                token=token,
                starting_at=starting_at,
                ending_at=ending_at,
                list_user_query=list_user_query,
            )
            for token in list_token
        ]
        results: List[
            Union[List[jira_clockwork], BaseException]
        ] = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                list_jira_clockwork.extend(result)
            else:
                logging.error(f"Error in one of the tasks: {result}")

    return list_jira_clockwork


def read_and_combine_excel_files(folder_path: str, prefix:str = 'worklogs_',sheet_name: str = 'Sheet1') -> pd.DataFrame:
    # Find all Excel files in the specified folder
    excel_files = glob.glob(folder_path + f"{prefix}.xlsx")

    # List to store DataFrames from each file
    dataframes = []

    # Read each Excel file and append the DataFrame to the list
    for file in excel_files:
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
            dataframes.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # Combine all DataFrames into one
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
    else:
        combined_df = pd.DataFrame()

    return combined_df.drop_duplicates(inplace=True)

def convert_dataframe_to_jira_clockwork(df: pd.DataFrame) -> List[jira_clockwork]:
    jira_objects: List[jira_clockwork] = []

    for _, row in df.iterrows():
        # Extract data from the DataFrame row and create a jira_clockwork instance
        jira_obj = jira_clockwork(
            author_display_name=row['Author'],  # Adjust column names as necessary
            author_email_address='',  
            started_dt= (
                    datetime.fromisoformat(row["Started at"]).astimezone(
                        defaultData.thailand_tz
                    ).replace(tzinfo=None)
                    if "Started at" in row
                    else datetime.min
                ),  # Convert to datetime
            time_spent=row['Time spent'],
            time_spent_seconds=int(row['Time Spent (seconds)']),
            project_key=row['Project Key'],  # Example placeholder column
            project_name=str(row['Project Name']).strip() if pd.notna(row['Project Name']) else '',  # Example placeholder column
            parent_key=row['Parent Key'] if pd.notna(row['Parent Key']) else '',
            parent_summary=str(row['Parent Summary']).strip() if pd.notna(row['Parent Summary']) else '',
            issue_key=row['Issue Key'],
            issue_type=row['Issue Type'],
            issue_summary=str(row['Issue Summary']).strip() if pd.notna(row['Issue Summary']) else '',
            comment=str(row['Comment']).strip() if pd.notna(row['Comment']) else ''  # Handle NaN values
        )
        jira_objects.append(jira_obj)

    return jira_objects