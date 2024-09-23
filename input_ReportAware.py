import mainReportAware

# input for jira clock work
list_api_token : list[str] = [
    ""
    ] 
starting_at_str = "01/06/2024"
ending_at_str = "30/06/2024"

List_email : list[str] = [
    
    "xxxxxx49@postbox.in.th",
    "xxxxxx49@postbox.in.th"
    ]

folder_path_jira = "Report/Aug 2024/"  

def main():
    
    mainReportAware.main()
    
if __name__ == "__main__":
    main()