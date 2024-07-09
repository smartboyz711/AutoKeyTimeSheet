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

ไฟล์ Report auto time sheet อยู่ที่ folder Report/ ชื่อไฟล์ขึ้นต้นด้วย Aware_time_sheet_report_XXXX.xlsx

# วิธีใช้งาน Script Export Report time sheet from jira

กรอกค่าต่อไปนี้ที่ไฟล์ input_ReportAware.py และ run input_ReportAware.py เพื่อรัน Script
 
List_api_token = "" (token จาก Jira) รองรับหลาย token พร้อมกัน

starting_at_str = "01/03/2024"

ending_at_str = "30/03/2024"

Email user jira @postbox.in.th ที่ต้องการ export time sheet

List_email: list[str] = [
    "XXXX49@postbox.in.th",
    "XXXX49@postbox.in.th",
    "XXXX49@postbox.in.th"
] 

ไฟล์ Report jira time sheet อยู่ที่ folder Report/ ชื่อไฟล์ขึ้นต้นด้วย jira_summary_timeSheet_XXXX.xlsx
