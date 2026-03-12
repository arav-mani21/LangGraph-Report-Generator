from graph import graph

topic = "An Overview of the Rust Programming Language"
compiled_graph = graph.compile()
result = compiled_graph.invoke({"topic": topic})

with open('report.md', "w", encoding="utf-8") as md_file:
    md_file.write(result['final_report'])