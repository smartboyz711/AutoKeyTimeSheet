import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime
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
    timeSpent : str
    timeSpentSeconds: int
    
    def as_dict(self) -> dict :
        return {k : v for k, v in asdict(self).items()}

def api_jira_clockwork(token: str,
                        starting_at: datetime,
                        ending_at: datetime,
                        list_user_query: list[str]
                        ) -> list[Jira_Clockwork]:

    list_jira_Clockwork: list[Jira_Clockwork] = []
    jira_Clockwork_url = "https://api.clockwork.report/v1/worklogs?expand=authors,issues,epics,emails,worklogs,comments"

    if (token and starting_at and ending_at and list_user_query):
        headers_api: dict[str, str] = {
            "Authorization": f"Token {token}"
        }
        criteria_data = {
            "starting_at": starting_at.strftime("%Y-%m-%d"),
            "ending_at": ending_at.strftime("%Y-%m-%d"),
            "user_query[]": list_user_query
        }
        try:
            response: Response = requests.get(url=jira_Clockwork_url,
                                    headers=headers_api,
                                    data=criteria_data,
                                    timeout=60)

            if (response.status_code == 200 and len(response.json()) > 0):
                for data in response.json():
                    author_display_name: str = data["author"]["displayName"]
                    author_emailAddress: str = data["author"]["emailAddress"]
                    project_key: str = data["issue"]["fields"]["project"]["key"]
                    project_name: str = data["issue"]["fields"]["project"]["name"]
                    parent_key: str = data["issue"]["fields"]["parent"]["key"]
                    parent_summary: str = data["issue"]["fields"]["parent"]["fields"]["summary"]
                    issue_key: str = data["issue"]["key"]
                    issue_type: str = data["issue"]["fields"]["issuetype"]["name"]
                    issue_summary: str = data["issue"]["fields"]["summary"]
                    timeSpent: str = data["timeSpent"]
                    timeSpentSeconds: int = data["timeSpentSeconds"]
                    try:
                        started_dt : datetime = datetime.fromisoformat(
                            data["started"]).replace(tzinfo=None)
                    except Exception:
                        started_dt = datetime.min
                    try:
                        comment: str = data["comment"]
                    except Exception:
                        comment = ""

                    jira_Clockwork = Jira_Clockwork(
                        author_display_name=author_display_name,
                        author_emailAddress=author_emailAddress,
                        started_dt=started_dt,
                        project_key=project_key,
                        project_name=project_name.strip(),
                        parent_key=parent_key,
                        parent_summary=parent_summary.strip(),
                        issue_key=issue_key,
                        issue_type=issue_type,
                        issue_summary=issue_summary.strip(),
                        comment=comment.strip(),
                        timeSpent=timeSpent,
                        timeSpentSeconds=timeSpentSeconds,
                    )
                    list_jira_Clockwork.append(jira_Clockwork)
                list_jira_Clockwork = sorted(list_jira_Clockwork, key=lambda jira_Clockwork : (
                    jira_Clockwork.author_display_name, jira_Clockwork.started_dt))
        except Exception as e:
            print(f"Error api jira clockwork : {e}")

    return list_jira_Clockwork

async def api_jira_clockwork_async(token: str,
                        starting_at: datetime,
                        ending_at: datetime,
                        list_user_query: list[str]
                        ) -> list[Jira_Clockwork]:
    
    return await asyncio.to_thread(api_jira_clockwork,token,starting_at,ending_at,list_user_query)
    
async def api_jira_clockwork_async_all_token (list_token: list[str],
                                    starting_at: datetime,
                                    ending_at: datetime,
                                    list_user_query: list[str]
                                    ) -> list[Jira_Clockwork]:
    
    list_jira_Clockwork: list[Jira_Clockwork] = []
    if list_token:
        tasks = [api_jira_clockwork_async(
            token, starting_at, ending_at, list_user_query) for token in list_token]
        results: list[list[Jira_Clockwork]] = await asyncio.gather(*tasks)
        
        for result in results:
            list_jira_Clockwork.extend(result)
            
    return list_jira_Clockwork
    
