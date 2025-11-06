from typing import Dict, List, Any


def format_review_result(review_result: Dict[str, Any]) -> str:
    """
    Format a review result dictionary into a readable markdown comment string.
    
    Args:
        review_result: Dictionary containing review results with keys:
            - "issues": List of issue dictionaries
            - "truncated": Boolean indicating if diff was truncated
    
    Returns:
        Formatted markdown string ready to be posted as a GitHub comment
    """
    issues = review_result.get("issues", [])
    
    if not issues:
        return "## Code Review Results\n\n✅ No issues found!"
    
    comment_lines = ["## Code Review Results\n"]
    
    for issue in issues:
        issue_type = issue.get("type", "other")
        description = issue.get("description", "")
        line_numbers = issue.get("line_numbers", [])
        suggested_fix = issue.get("suggested_fix", "")
        
        comment_lines.append(f"### {issue_type.upper()}")
        
        if line_numbers:
            comment_lines.append(f"**Lines:** {', '.join(map(str, line_numbers))}")
        
        comment_lines.append(f"**Issue:** {description}")
        
        if suggested_fix:
            comment_lines.append(f"**Suggestion:** {suggested_fix}")
        
        comment_lines.append("")
    
    if review_result.get("truncated"):
        comment_lines.append("_Note: Diff was truncated due to size limits._")
    
    return "\n".join(comment_lines)

