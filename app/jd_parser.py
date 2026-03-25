"""Job Description parser: extracts structured data from JD text."""

from app.models import JobDescription


def parse_jd_text(jd_text: str) -> JobDescription:
    """Create a JobDescription object from raw text. 
    
    The LLM will do deeper semantic parsing; this provides the raw container.
    """
    return JobDescription(raw_text=jd_text.strip())
