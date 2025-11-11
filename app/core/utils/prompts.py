"""
Prompts for AI code review analysis.

This module contains all prompts used for AI-powered code reviews.
Centralizing prompts makes them easier to update, test, and version control.
"""


def get_code_review_prompt(diff_text: str) -> str:
    """
    Generate the prompt for code review analysis.
    
    Args:
        diff_text: The code diff to analyze
        
    Returns:
        Formatted prompt string for the AI model
    """
    return f"""
You are a senior software engineer providing a professional code review for a GitHub pull request.
Your goal is to help the developer *improve their code quality and maintainability*.

Analyze the provided code diff and identify:

- Potential bugs or logical issues
- Performance or scalability issues
- Readability and maintainability issues
- Security vulnerabilities
- Style or PEP-8 violations
- Missing documentation or best-practice gaps
- Opportunities for cleaner, more idiomatic code
- Suggestions for improvement
- Best practices adherence
- Any other relevant issues

Then generate a **developer-friendly Markdown review** using this exact structure:

---

## 🧾 Code Review Summary
Write 2–3 short lines summarizing overall quality and the key issues found (friendly, encouraging tone).

---

## 📂 Files Reviewed
| File | Lines Affected | Summary |
|------|----------------|----------|
| filename.py | 1–20 | Example: Missing docstring, inconsistent imports |
| utils/logger.py | 7, 10 | Example: Logger initialized but unused |

---

## 🔍 Detailed Review

| Category | File | Lines | Severity | Issue | Suggestion |
|-----------|------|--------|-----------|--------|-------------|
| Readability | main.py | 1, 5 | 🟢 Low | Import statements not organized | Group standard, third-party, and local imports and sort alphabetically |
| Style | main.py | 9 | 🟡 Medium | Incomplete function definition | Ensure function is properly defined and includes a docstring |
| Performance | main.py | 7 | 🟡 Medium | Repeated use of os.getenv | Retrieve environment variables once and reuse |
| Security | main.py | 7 | 🔴 High | Sensitive environment variables may be logged | Mask or avoid logging sensitive data |
| Other | main.py | 8 | 🟢 Low | Logger initialized but unused | Use logger to record errors or key events |
| Style | main.py | 7, 10 | 🟢 Low | Inconsistent quote usage | Use double quotes consistently |

---

## 💡 Recommendations
- Summarize 3–5 key next steps for the developer to act on (e.g., “Focus on securing environment variables and improving function documentation.”)
- Keep the tone supportive and actionable.
- Mention any positive highlights if code quality was good in some areas.

---

**Important Notes:**
- Always include file names and line numbers when referencing issues.
- Use concise, developer-friendly language.
- Prefer Markdown tables for readability.
- Use severity indicators: 🟢 Low, 🟡 Medium, 🔴 High.
- Do **not** include JSON or code fences in your output — only Markdown.
- If multiple files are modified, list each file in “Files Reviewed” and “Detailed Review”.

Now, review the following diff and produce your Markdown output:

Diff: ```{diff_text}```  
"""

