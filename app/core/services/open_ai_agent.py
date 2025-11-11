import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

from app.core.utils.prompts import get_code_review_prompt

load_dotenv()
model = os.getenv("MODEL", "gpt-4o-mini")

logger = logging.getLogger(__name__)


def analyze_code_diff(diff_text: str) -> list:
    """
    Analyze a code diff using OpenAI and return a list of issues.
    
    Args:
        diff_text: The code diff to analyze
        
    Returns:
        List of issues found in the code diff
        
    Raises:
        RuntimeError: If OPENAI_API_KEY is not set
        ValueError: If the API response cannot be parsed
    """
    prompt = get_code_review_prompt(diff_text)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Set the environment variable or configure a secret.")

    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        content = response.choices[0].message.content
        ai_agent_response = json.loads(content)
        issues = ai_agent_response.get("issues", [])
        logger.info(f"Code review completed. Found {len(issues)} issues.")
        return issues
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response from OpenAI: {e}")
        logger.error(f"Response content: {content[:500]}")
        raise ValueError(f"Invalid JSON response from OpenAI: {e}")
    except Exception as e:
        logger.error(f"Error during code analysis: {e}", exc_info=True)
        raise

