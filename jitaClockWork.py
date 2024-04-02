from dataclasses import asdict, dataclass
from datetime import datetime
import requests


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
    timeSpentSeconds: int
    statusMessage: str = ""
    
    def as_dict(self) -> dict :
        return {k : v for k, v in asdict(self).items()}

def api_jira_clockwork(token: str,
                       starting_at: datetime,
                       ending_at: datetime,
                       list_user_query: list[str]
                       ) -> list[Jira_Clockwork]:

    list_jira_Clockwork: list[Jira_Clockwork] = []
    jira_Clockwork_url = "https://api.clockwork.report/v1/worklogs?expand=authors,issues,epics,emails,worklogs,comments"

    if (token and starting_at and ending_at and len(list_user_query) > 0):
        headers_api = {
            "Authorization": token
        }
        criteria_data = {
            "starting_at": starting_at.strftime("%Y-%m-%d"),
            "ending_at": ending_at.strftime("%Y-%m-%d"),
            "user_query[]": list_user_query
        }
        try:
            response = requests.get(url=jira_Clockwork_url,
                                    headers=headers_api,
                                    data=criteria_data,
                                    timeout=30)

            if (response.status_code == 200):
                for data in response.json():
                    author_display_name = data["author"]["displayName"]
                    author_emailAddress = data["author"]["emailAddress"]
                    project_key = data["issue"]["fields"]["project"]["key"]
                    project_name = data["issue"]["fields"]["project"]["name"]
                    parent_key = data["issue"]["fields"]["parent"]["key"]
                    parent_summary = data["issue"]["fields"]["parent"]["fields"]["summary"]
                    issue_key = data["issue"]["key"]
                    issue_type = data["issue"]["fields"]["issuetype"]["name"]
                    issue_summary = data["issue"]["fields"]["summary"]
                    timeSpentSeconds = data["timeSpentSeconds"]
                    try:
                        started_dt = datetime.fromisoformat(
                            data["started"]).replace(tzinfo=None)
                    except Exception:
                        started_dt = datetime.now()
                    try:
                        comment = data["comment"]
                    except Exception:
                        comment = ""

                    jira_Clockwork = Jira_Clockwork(
                        author_display_name=author_display_name,
                        author_emailAddress=author_emailAddress,
                        started_dt=started_dt,
                        project_key=project_key,
                        project_name=project_name,
                        parent_key=parent_key,
                        parent_summary=parent_summary,
                        issue_key=issue_key,
                        issue_type=issue_type,
                        issue_summary=issue_summary,
                        comment=comment,
                        timeSpentSeconds=timeSpentSeconds,
                    )
                    list_jira_Clockwork.append(jira_Clockwork)
                list_jira_Clockwork = sorted(list_jira_Clockwork, key=lambda jira_Clockwork : (
                    jira_Clockwork.author_emailAddress, jira_Clockwork.started_dt))
        except Exception as e:
            print(f"Error api jira clockwork : {e}")

    return list_jira_Clockwork
