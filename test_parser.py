from query_parser import parse_query


questions = [
    "How's our pipeline looking for Mining this quarter?",
    "What's the Powerline pipeline?",
    "Show me the Renewables pipeline for Q2 2026",
    "How are our work orders doing?",
    "What's our billing situation?",
    "How's our pipeline looking for Mining this quarter?",
    "What's the Powerline pipeline?",
    "Show me the Renewables pipeline for Q2 2026",
    "How are our work orders doing?",
    "What's our billing situation?",
    "Which customers are the biggest risk?"
]



for question in questions:

    print("\nQuestion:")
    print(question)

    result = parse_query(question)

    print("Parsed:")
    print(result)
