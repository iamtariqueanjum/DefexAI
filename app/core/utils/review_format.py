from typing import Dict, Any


def format_review_result(review_result: Dict[str, Any]) -> str:
    """
    Format a review result dictionary into a readable markdown comment string.
    
    Args:
        review_result: Dictionary containing review results with keys:
            - "review": Markdown string containing the AI-generated review
            - "truncated": Boolean indicating if diff was truncated
    
    Returns:
        Formatted markdown string ready to be posted as a GitHub comment
    """
    review_markdown = review_result.get("review", "")
    truncated = review_result.get("truncated", False)
    
    if not review_markdown or not review_markdown.strip():
        return "## Code Review Results\n\n✅ No issues found!"
    
    # Start with the AI-generated review
    comment_lines = [review_markdown.strip()]
    
    # Add truncation note if applicable
    if truncated:
        comment_lines.append("")
        comment_lines.append("---")
        comment_lines.append("_Note: Diff was truncated due to size limits._")
    
    return "\n\n".join(comment_lines)

