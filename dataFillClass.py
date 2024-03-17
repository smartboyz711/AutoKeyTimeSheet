# Default data Aware Time sheet
from datetime import datetime
import defaultData

class Description:
    def __init__(self, parent_key: str,
                 parent_summary: str,
                 issue_Type: str,
                 issue_summary: str,
                 comment: str):

        self.parent_key = parent_key
        self.parent_summary = parent_summary
        self.issue_Type = issue_Type
        self.issue_summary = issue_summary
        self.comment = comment

    def __str__(self) -> str:
        return f"{self.parent_summary}\n- Sub task : {self.issue_summary}\n- Comment : {self.comment}"


class Data_fill:

    def __init__(self, customer: str,
                 project: str,
                 role: str,
                 task: str,
                 billType: str,
                 filldatetime: datetime,
                 hours: float,
                 description: Description,
                 statusMessage: str):

        self.customer = customer
        self.project = project
        self.role = role
        self.task = task
        self.billType = billType
        self.filldatetime = filldatetime
        self.hours = hours
        self.description = description
        self.statusMessage = statusMessage

    def get_id_billtype(self) -> str :
        if (self.billType == "Regular"):
            return "cphContent_rdoPopBillType_0"  # Regular
        elif (self.billType == "Overtime"):
            return "cphContent_rdoPopBillType_1"  # Overtime
        elif (self.billType == "Non-Billable"):
            return "cphContent_rdoPopBillType_2"  # Non-Billable
        elif (self.billType == "Overtime Nonbill"):
            return "cphContent_rdoPopBillType_3"  # Overtime Nonbill
        else :
            return "cphContent_rdoPopBillType_0"  # Regular

    def as_dict(self) :
        return {
            "Datetime": self.filldatetime.strftime(defaultData.df_string),
            "Customer": self.customer,
            "Project": self.project,
            "Role": self.role,
            "Task": self.task,
            "BillType": self.billType,
            "Description": self.description.__str__(),
            "Hours": self.hours,
            "StatusMessage": self.statusMessage
        }
