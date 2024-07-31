import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List
import requests
from requests import Response


@dataclass
class Jira_Clockwork:

    author_display_name: str
    author_emailAddress: str
    started_dt: datetime
    project_key: str
    project_name: str
    parent_key: str
    parent_summary: str
    issue_key: str
    issue_type: str
    issue_summary: str
    comment: str
    timeSpent: str
    timeSpentSeconds: int

    def as_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items()}


def api_jira_clockwork(
    token: str, starting_at: datetime, ending_at: datetime, list_user_query: List[str]
) -> List[Jira_Clockwork]:

    jira_clockwork_url = "https://api.clockwork.report/v1/worklogs?expand=authors,issues,epics,emails,worklogs,comments"
    list_jira_clockwork: List[Jira_Clockwork] = []

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
                started_dt = (
                    datetime.fromisoformat(data["started"]).replace(tzinfo=None)
                    if "started" in data
                    else datetime.min
                )
                comment = data.get("comment", "").strip()

                jira_clockwork = Jira_Clockwork(
                    author_display_name=author_display_name,
                    author_emailAddress=author_email_address,
                    started_dt=started_dt,
                    project_key=project_key,
                    project_name=project_name,
                    parent_key=parent_key,
                    parent_summary=parent_summary,
                    issue_key=issue_key,
                    issue_type=issue_type,
                    issue_summary=issue_summary,
                    comment=comment,
                    timeSpent=time_spent,
                    timeSpentSeconds=time_spent_seconds,
                )
                list_jira_clockwork.append(jira_clockwork)

            except KeyError as e:
                print(f"Missing key in data: {e}")
                continue
            except Exception as e:
                print(f"Error processing worklog data: {e}")
                continue

        list_jira_clockwork.sort(key=lambda x: (x.author_display_name, x.started_dt))

    except requests.RequestException as e:
        print(f"api_jira_clockwork Request error: {e}")
    except Exception as e:
        print(f"api_jira_clockwork Unexpected error: {e}")

    return list_jira_clockwork


async def api_jira_clockwork_async(
    token: str, starting_at: datetime, ending_at: datetime, list_user_query: list[str]
) -> list[Jira_Clockwork]:

    return await asyncio.to_thread(
        api_jira_clockwork, token, starting_at, ending_at, list_user_query
    )


async def api_jira_clockwork_async_all_token(
    list_token: list[str],
    starting_at: datetime,
    ending_at: datetime,
    list_user_query: list[str],
) -> list[Jira_Clockwork]:

    list_jira_Clockwork: list[Jira_Clockwork] = []
    if list_token:
        tasks = [
            api_jira_clockwork_async(token, starting_at, ending_at, list_user_query)
            for token in list_token
        ]
        results: list[list[Jira_Clockwork]] = await asyncio.gather(*tasks)

        for result in results:
            list_jira_Clockwork.extend(result)

    return list_jira_Clockwork
