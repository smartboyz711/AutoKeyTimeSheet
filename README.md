# Auto ket Time Sheet Aware 

by Theedanai Poomilamnao 18/02/2024

Download python จาก https://www.python.org/ 

หลังจาก git clone run command ใน folder 

-> pip install -r requirements.txt 

เพื่อ install package ที่ต้องใช้ในการ Run Project นี้

# วิธีใช้งาน Script auto time sheet from jira

กรอกค่าต่อไปนี้ที่ไฟล์ input_autoTimeSheet.py และ run input_autoTimeSheet.py เพื่อรัน Script

email_jira_clockwork = "xxxx49@postbox.in.th" (Email @postbox.in.th)

api_token = "" (token จาก Jira)

starting_at_str = "18/03/2024" 

ending_at_str = "30/03/2024"

username_aware = 'thxxdxnxi.x' (Email user Aware)

password_aware = ''

# วิธีใช้งาน Script Export Time Sheet from jira

กรอกค่าต่อไปนี้ที่ไฟล์ input_ReportAware.py และ run input_ReportAware.py เพื่อรัน Script
 
api_token = "" (token จาก Jira)

starting_at_str = "01/03/2024"

ending_at_str = "30/03/2024"

Email user jira @postbox.in.th ที่จ้องการ export time sheet

List_email: list[str] = [
    "XXXX49@postbox.in.th",
    "XXXX49@postbox.in.th",
    "XXXX49@postbox.in.th"
] 



