from langgraph.types import Send
from langgraph.graph import StateGraph, START, END
from state import ReportState
from nodes import planner_node, writer_node, assemble_report_node

def fan_out_to_writers(state: ReportState) -> list[Send]:
    return [
        Send("writer", {"sub_topic": topic, "topic": state["topic"]})
        for topic in state["sub_topics"]
    ]

graph = StateGraph(ReportState)

graph.add_node("planner", planner_node)
graph.add_node("writer", writer_node)
graph.add_node("assemble_report", assemble_report_node)

graph.add_edge(START, "planner")
graph.add_edge("writer", "assemble_report")
graph.add_edge("assemble_report", END)

graph.add_conditional_edges("planner", fan_out_to_writers)