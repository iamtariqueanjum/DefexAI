import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
model = os.getenv("MODEL", "gpt-4o-mini")


def analyze_code_diff(diff_text: str) -> str:
    """
    Use GPT to analyze a diff and provide concise review feedback.
    """
    # TODO FUNKY prompt move to constants/file
    prompt = f"""
    You are an experienced software engineer reviewing a GitHub pull request.
    Analyze this code diff and identify:
    - Potential bugs
    - Performance issues
    - Readability concerns
    - Security vulnerabilities
    - Suggestions for improvement
    - Best practices adherence
    - Any other relevant issues

    Suggest concise improvements following PEP-8 and general software engineering best practices.

    Return your answer strictly as valid JSON (no markdown, no backticks, no extra text).

    Sample output format:
    {{
      "issues": [
        {{
          "type": "bug|performance|readability|security|style|other",
          "description": "Description of the issue",
          "line_numbers": [12, 13],
          "suggested_fix": "Suggested fix description"
        }},
        {{
            "type": "performance",
            "description": "Inefficient use of list comprehension",
            "line_numbers": [45],
            "suggested_fix": "Consider using a generator expression to reduce memory usage."
        }}
        ]
    }}
    Diff: ```{diff_text}```  
    """

    # Ensure an API key is configured. Create the client lazily so missing
    # credentials produce a clear error rather than failing with an opaque
    # exception at import time.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Set the environment variable or configure a secret.")

    client = OpenAI(api_key=api_key)

    # TODO FUNKY exception handling and retries
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    content = response.choices[0].message.content
    ai_agent_response = json.loads(content)
    return ai_agent_response.get("issues", [])

