import os
from state import ReportState
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic

load_dotenv()

llm = ChatAnthropic(
    model=os.getenv('ANTHROPIC_MODEL')
)

class PlannerOutput(BaseModel):
    subtopics: list[str]

class WriterOutput(BaseModel):
    section_text: str

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