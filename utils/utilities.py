def clean_html_tags(text: str) -> str:
    """Utility function to remove HTML tags from the given text."""
    return text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")