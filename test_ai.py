"""Quick AI service test harness.
Run: D:/CourseMate/.venv/Scripts/python.exe test_ai.py
"""
from ai_service import summarize, generate_template, extract_tags, answer_question, AIServiceError

TEST_NOTE = """
Introduction to Calculus: Understanding Derivatives

Key Concepts:
- Power Rule: For f(x) = x^n, the derivative f'(x) = nx^(n-1)
- Product Rule: (uv)' = u'v + uv'
- Quotient Rule: (u/v)' = (u'v - uv')/v^2
- Chain Rule: For composite functions f(g(x)), derivative is f'(g(x)) * g'(x)

Applications:
1. Optimization problems - finding maximum and minimum values
2. Motion analysis - calculating velocity and acceleration from position functions
3. Rate of change problems in physics and economics
""".strip()

PROMPT_STUDY = "Create a study template for learning calculus derivative rules with space for examples and practice problems"
PROMPT_PLANNER = "Create a weekly study planner template for managing calculus and physics coursework with daily time blocks"
QUESTION = "Based on the notes, what is the product rule formula for derivatives?"


def main():
    print("=== AI Service Smoke Test ===")
    print("Testing connection to http://localhost:11434\n")
    
    # Summarize
    try:
        summary = summarize(TEST_NOTE)
        if summary and summary.strip():
            print("\n[Summary]")
            print(summary[:500])
        else:
            print("\n[Summary] ⚠ Empty response (no model available?)")
    except AIServiceError as e:
        print("\n[Summary] ✗ Failed:", e)
    except Exception as e:
        print("\n[Summary] ✗ Unexpected error:", e)
    
    # Study template
    try:
        study_tpl = generate_template("study", PROMPT_STUDY)
        if study_tpl and study_tpl.strip():
            print("\n[Study Template]")
            print(study_tpl[:500])
        else:
            print("\n[Study Template] ⚠ Empty response (no model available?)")
    except AIServiceError as e:
        print("\n[Study Template] ✗ Failed:", e)
    except Exception as e:
        print("\n[Study Template] ✗ Unexpected error:", e)
    
    # Planner template
    try:
        planner_tpl = generate_template("planner", PROMPT_PLANNER)
        if planner_tpl and planner_tpl.strip():
            print("\n[Planner Template]")
            print(planner_tpl[:500])
        else:
            print("\n[Planner Template] ⚠ Empty response (no model available?)")
    except AIServiceError as e:
        print("\n[Planner Template] ✗ Failed:", e)
    except Exception as e:
        print("\n[Planner Template] ✗ Unexpected error:", e)
    
    # Extract tags
    try:
        tags = extract_tags(TEST_NOTE)
        if tags:
            print("\n[Extracted Tags]", tags)
        else:
            print("\n[Extracted Tags] ⚠ Empty list (no model available?)")
    except AIServiceError as e:
        print("\n[Extracted Tags] ✗ Failed:", e)
    except Exception as e:
        print("\n[Extracted Tags] ✗ Unexpected error:", e)
    
    # Q&A
    try:
        answer = answer_question(TEST_NOTE, QUESTION)
        if answer and answer.strip():
            print("\n[Answer]")
            print(answer[:500])
        else:
            print("\n[Answer] ⚠ Empty response (no model available?)")
    except AIServiceError as e:
        print("\n[Answer] ✗ Failed:", e)
    except Exception as e:
        print("\n[Answer] ✗ Unexpected error:", e)
    
    print("\n\n=== Test Complete ===")
    print("If all responses are empty, ensure:")
    print("1. Ollama is installed: https://ollama.com")
    print("2. At least one model is pulled: ollama pull llama3")
    print("3. Ollama service is running (usually auto-starts)")
    print("Then re-run this test.")

if __name__ == "__main__":
    main()
