CONFIG = {
    # Anthropic api key
    "ANTHROPIC_API_KEY": "your_anthropic_api_key",

    # Scraper settings
    "NUM_SEARCH_RESULTS": 3,
    "SELENIUM_TIMEOUT": 10,  # in seconds

    # File paths
    "DEBUG_DIR": "debug",
    "REPORTS_DIR": "reports",

    # Report generator settings
    "AI_MODEL": "claude-3-haiku-20240307",

    # Logging
    "LOG_LEVEL": "INFO",
    "LOG_FORMAT": "%(asctime)s - %(levelname)s - %(message)s",

    # Other settings
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 2,  # in seconds
}