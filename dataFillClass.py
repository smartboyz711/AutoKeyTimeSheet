# Default data Aware Time sheet
from dataclasses import dataclass
from datetime import datetime
import defaultData


@dataclass()
class data_fill:
    customer: str
    project: str
    role: str
    task: str
    bill_type: str
    filldatetime: datetime
    hours: float
    status_message: str

    def get_id_billtype(self) -> str:
        if self.bill_type == "Regular":
            return "cphContent_rdoPopBillType_0"  # Regular
        elif self.bill_type == "Overtime":
            return "cphContent_rdoPopBillType_1"  # Overtime
        elif self.bill_type == "Non-Billable":
            return "cphContent_rdoPopBillType_2"  # Non-Billable
        elif self.bill_type == "Overtime Nonbill":
            return "cphContent_rdoPopBillType_3"  # Overtime Nonbill
        else:
            return "cphContent_rdoPopBillType_0"  # Regular


@dataclass()
class data_fill_jira(data_fill):
    project_key: str
    project_name: str
    parent_summary: str
    issue_Type: str
    issue_summary: str
    comment: str

    def description_str(self) -> str:
        task_detail: str = self.comment or self.issue_summary
        return f"Project: {self.project_key}-{self.project_name}\nTask Detail: {task_detail}"

    def as_dict(self) -> dict:
        return {
            "Datetime": self.filldatetime.strftime(format=defaultData.df_string),
            "Customer": self.customer,
            "Project": self.project,
            "Role": self.role,
            "Task": self.task,
            "BillType": self.bill_type,
            "Description": self.description_str(),
            "Hours": self.hours,
            "StatusMessage": self.status_message,
        }
