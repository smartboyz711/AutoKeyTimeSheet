import mainAutoTimeSheet

# input for jira clock work
email_jira_clockwork = "XXXX49@postbox.in.th"
api_token = ""
starting_at_str = "18/03/2024"
ending_at_str = "30/03/2024"

# input user password aware
username_aware = "theedanai.p"
password_aware = ""

default_customer = "AIS"
default_project = "AIS-SFF"
default_role = "Developer"
default_task = "Coding"

folder_path = "input_timeSheet_jira_excel/"   

def main():
    
    mainAutoTimeSheet.main()
    
if __name__ == "__main__":
    main()
