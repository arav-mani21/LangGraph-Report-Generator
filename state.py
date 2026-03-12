import operator
from typing import TypedDict, Annotated

class ReportState(TypedDict):
    topic: str
    sub_topics: list
    completed_sections: Annotated[list, operator.add]
    final_report: str