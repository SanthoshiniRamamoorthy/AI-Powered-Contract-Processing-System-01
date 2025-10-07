# app/services/redactor.py

import re

def redact_pii(text: str) -> str:
    """
    Redact personally identifiable information from text.
    """
    if not text:
        return text
    
    # Redact email addresses
    text = re.sub(r'\S+@\S+', '[REDACTED_EMAIL]', text)
    
    # Redact common phone number formats
    text = re.sub(r'\+?\d[\d\s\-\(\)]{7,}\d', '[REDACTED_PHONE]', text)
    
    # Redact SSN/ID format (XXX-XX-XXXX)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_ID]', text)
    
    # Redact credit card numbers (basic pattern)
    text = re.sub(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b', '[REDACTED_CARD]', text)
    
    return text