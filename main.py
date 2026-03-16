import os
import operator
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END

load_dotenv()

# --- State ---

class ReportState(TypedDict):
    topic: str
    sub_topics: list
    completed_sections: Annotated[list, operator.add]
    final_report: str

# --- LLM ---

llm = ChatAnthropic(
    model=os.getenv('ANTHROPIC_MODEL')
)

# --- Structured output schemas ---

class PlannerOutput(BaseModel):
    subtopics: list[str]

class WriterOutput(BaseModel):
    section_text: str

# --- Nodes ---

def planner_node(state: ReportState) -> dict:
    topic = state["topic"]
    structured_llm = llm.with_structured_output(PlannerOutput)

    prompt = f"""
        Break down the topic mentioned below into a list of the 5-8 sub-topics.
        Order these sub-topics in a manner that a report with these sub-topics would flow coherently.
        The names of each sub-topic should be no more than 10 words and descriptive enough that it doesn't have conceptual overlap with other sub-topics
        \n\n{topic}
    """

    response = structured_llm.invoke(prompt)
    return {"sub_topics": response.subtopics}

def writer_node(state: dict) -> dict:
    structured_llm = llm.with_structured_output(WriterOutput)

    sub_topic = state["sub_topic"]
    topic = state["topic"]

    prompt = f"""
        Provide an explanation of the topic mentioned below.
        This explanation will be apart of a larger report about {topic}.
        Keep your explanation between 300 and 500 words.
        Do not include the sub-topic title in your output.
        \n\n{sub_topic}
    """

    response = structured_llm.invoke(prompt)
    return {"completed_sections": [response.section_text]}

def assemble_report_node(state: ReportState) -> dict:
    final_report = f"# {state['topic']}\n\n"
    for i in range(len(state["sub_topics"])):
        final_report += f"## {state['sub_topics'][i]}\n{state['completed_sections'][i]}\n"
    return {"final_report": final_report}

# --- Graph ---

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

# --- Entry point ---

if __name__ == "__main__":
    topic = "An Overview of the Rust Programming Language"
    compiled_graph = graph.compile()
    result = compiled_graph.invoke({"topic": topic})

    with open('report.md', "w", encoding="utf-8") as md_file:
        md_file.write(result['final_report'])
