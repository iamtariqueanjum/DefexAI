import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("MODEL", "gpt-4o-mini")


def analyze_code_diff(diff_text: str) -> str:
    """
    Use GPT to analyze a diff and provide concise review feedback.
    """
    prompt = f"""
    You are an experienced software engineer reviewing a GitHub pull request.
    Analyze this code diff and identify potential bugs, performance issues,
    or readability concerns. Suggest improvements concisely.

    Diff:
    {diff_text[:6000]}  # limiting for safety
    """

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content
