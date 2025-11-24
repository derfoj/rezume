KNOWLEDGE_BASE_SCHEMA = {
    "type": "object",
    "required": [
        "name", "title", "summary", "email", "portfolio_url", "linkedin_url",
        "photo_path", "skills", "soft_skills", "experiences", "education", "languages"
    ],
    "properties": {
        "name": {"type": "string"},
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "portfolio_url": {"type": "string", "format": "uri"},
        "linkedin_url": {"type": "string", "format": "uri"},
        "photo_path": {"type": "string"},
        "skills": {
            "type": "array",
            "items": {"type": "string"}
        },
        "soft_skills": {
            "type": "array",
            "items": {"type": "string"}
        },
        "experiences": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "company", "period", "description"],
                "properties": {
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "period": {"type": "string"},
                    "description": {"type": "string"}
                }
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["institution", "degree", "period"],
                "properties": {
                    "institution": {"type": "string"},
                    "degree": {"type": "string"},
                    "period": {"type": "string"},
                    "mention": {"type": "string", "nullable": True}
                }
            }
        },
        "languages": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "level"],
                "properties": {
                    "name": {"type": "string"},
                    "level": {"type": "string"}
                }
            }
        }
    },
    "additionalProperties": False
}