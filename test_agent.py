from bi_agent import answer_question


questions = [
    "How's our pipeline looking for Mining this quarter?",
    "What's the Powerline pipeline?",
    "How are our work orders doing?",
    "What's our billing situation?"
]


for question in questions:

    print("\n" + "=" * 60)
    print("QUESTION:")
    print(question)

    answer = answer_question(question)

    print("\nANSWER:")
    print(answer)