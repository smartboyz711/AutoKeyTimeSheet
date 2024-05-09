# Default data Aware Time sheet
from dataclasses import dataclass
from datetime import datetime
import defaultData

@dataclass()
class Description:
    
    parent_summary: str
    issue_Type: str
    issue_summary: str
    comment: str
    billType: str

    def description_str(self) -> str:
        if(self.billType == "Overtime") :
            return self.comment
        else :
            return f"{self.parent_summary}\n- {self.issue_Type} : {self.issue_summary}\n- Comment : {self.comment}"
@dataclass()
class Data_fill:

    customer: str
    project: str
    role: str
    task: str
    billType: str
    filldatetime: datetime
    hours: float
    description: Description
    statusMessage: str = ""

    def get_id_billtype(self) -> str:
        if (self.billType == "Regular"):
            return "cphContent_rdoPopBillType_0"  # Regular
        elif (self.billType == "Overtime"):
            return "cphContent_rdoPopBillType_1"  # Overtime
        elif (self.billType == "Non-Billable"):
            return "cphContent_rdoPopBillType_2"  # Non-Billable
        elif (self.billType == "Overtime Nonbill"):
            return "cphContent_rdoPopBillType_3"  # Overtime Nonbill
        else:
            return "cphContent_rdoPopBillType_0"  # Regular

    def as_dict(self) -> dict:
        return {
            "Datetime": self.filldatetime.strftime(defaultData.df_string),
            "Customer": self.customer,
            "Project": self.project,
            "Role": self.role,
            "Task": self.task,
            "BillType": self.billType,
            "Description": str(self.description),
            "Hours": self.hours,
            "StatusMessage": self.statusMessage
        }
