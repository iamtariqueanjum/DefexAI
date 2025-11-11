import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

from app.core.utils.prompts import get_code_review_prompt

load_dotenv()
model = os.getenv("MODEL", "gpt-4o-mini")

logger = logging.getLogger(__name__)


def analyze_code_diff(diff_text: str) -> str:
    """
    Analyze a code diff using OpenAI and return a Markdown-formatted review.
    
    Args:
        diff_text: The code diff to analyze
        
    Returns:
        Markdown string containing the code review
        
    Raises:
        RuntimeError: If OPENAI_API_KEY is not set or API call fails
        ValueError: If the API response is empty
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
        
        # Validate response content
        if not content or not content.strip():
            logger.error("OpenAI returned empty response")
            raise ValueError("OpenAI API returned an empty response")
        
        logger.info(f"Code review completed. Received {len(content)} characters of Markdown review.")
        return content.strip()
        
    except ValueError as e:
        raise
    except Exception as e:
        logger.error(f"Error during code analysis: {e}", exc_info=True)
        raise RuntimeError(f"Failed to analyze code diff: {e}") from e

