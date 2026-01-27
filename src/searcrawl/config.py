# -*- coding: utf-8 -*-
"""
Configuration Module - Loads configuration from environment variables

This module loads configuration from environment variables and provides
default values when environment variables are not set.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
load_dotenv()
logger.info("Loading environment variable configuration")

# SearXNG Configuration
SEARXNG_HOST = os.getenv("SEARXNG_HOST", "localhost")
SEARXNG_PORT = int(os.getenv("SEARXNG_PORT", "8080"))
SEARXNG_BASE_PATH = os.getenv("SEARXNG_BASE_PATH", "/search")
SEARXNG_API_BASE = f"http://{SEARXNG_HOST}:{SEARXNG_PORT}{SEARXNG_BASE_PATH}"

# API Service Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "3000"))

# Reader Service Configuration
READER_ENABLED = os.getenv("READER_ENABLED", "false").lower() == "true"
READER_URL = os.getenv("READER_URL", "http://reader:3000")
READER_API_KEY = os.getenv("READER_API_KEY", "")

# Crawler Configuration
DEFAULT_SEARCH_LIMIT = int(os.getenv("DEFAULT_SEARCH_LIMIT", "10"))
CONTENT_FILTER_THRESHOLD = float(os.getenv("CONTENT_FILTER_THRESHOLD", "0.6"))
WORD_COUNT_THRESHOLD = int(os.getenv("WORD_COUNT_THRESHOLD", "10"))
CRAWLER_POOL_SIZE = int(os.getenv("CRAWLER_POOL_SIZE", "4"))

# Cache Configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))

# Search Engine Configuration
DISABLED_ENGINES = os.getenv(
    "DISABLED_ENGINES",
    "wikipedia__general,currency__general,wikidata__general,duckduckgo__general,"
    "google__general,lingva__general,qwant__general,startpage__general,"
    "dictzone__general,mymemory translated__general,brave__general"
)
ENABLED_ENGINES = os.getenv("ENABLED_ENGINES", "baidu__general")
SEARCH_LANGUAGE = os.getenv("SEARCH_LANGUAGE", "auto")

# Anti-Crawl Configuration
ANTI_CRAWL_ENABLED = os.getenv("ANTI_CRAWL_ENABLED", "true").lower() == "true"
ENABLE_PROXY_ROTATION = os.getenv("ENABLE_PROXY_ROTATION", "false").lower() == "true"
ENABLE_USER_AGENT_ROTATION = os.getenv("ENABLE_USER_AGENT_ROTATION", "true").lower() == "true"
ENABLE_REQUEST_DELAY = os.getenv("ENABLE_REQUEST_DELAY", "true").lower() == "true"
ENABLE_RANDOM_HEADERS = os.getenv("ENABLE_RANDOM_HEADERS", "true").lower() == "true"
ENABLE_BROWSER_HEADERS = os.getenv("ENABLE_BROWSER_HEADERS", "true").lower() == "true"
MIN_REQUEST_DELAY = float(os.getenv("MIN_REQUEST_DELAY", "0.5"))
MAX_REQUEST_DELAY = float(os.getenv("MAX_REQUEST_DELAY", "3.0"))
PROXY_ROTATION_MODE = os.getenv("PROXY_ROTATION_MODE", "random")  # "random" or "sequential"
USE_MOBILE_AGENTS = os.getenv("USE_MOBILE_AGENTS", "false").lower() == "true"

# Proxy Configuration (comma-separated list of proxy URLs)
# Format: http://proxy1:port,http://proxy2:port or http://user:pass@proxy:port
PROXY_LIST = os.getenv("PROXY_LIST", "").strip()

# Custom User-Agents (comma-separated list)
CUSTOM_USER_AGENTS = os.getenv("CUSTOM_USER_AGENTS", "").strip()


def get_config_info() -> Dict[str, Any]:
    """Returns a dictionary of current configuration information

    Returns:
        dict: Dictionary containing all configuration parameters
    """
    return {
        "searxng": {
            "host": SEARXNG_HOST,
            "port": SEARXNG_PORT,
            "base_path": SEARXNG_BASE_PATH,
            "api_base": SEARXNG_API_BASE
        },
        "api": {
            "host": API_HOST,
            "port": API_PORT
        },
        "reader": {
            "enabled": READER_ENABLED,
            "url": READER_URL
        },
        "crawler": {
            "default_search_limit": DEFAULT_SEARCH_LIMIT,
            "content_filter_threshold": CONTENT_FILTER_THRESHOLD,
            "word_count_threshold": WORD_COUNT_THRESHOLD
        },
        "search_engines": {
            "disabled": DISABLED_ENGINES,
            "enabled": ENABLED_ENGINES
        },
        "anti_crawl": {
            "enabled": ANTI_CRAWL_ENABLED,
            "enable_proxy_rotation": ENABLE_PROXY_ROTATION,
            "enable_user_agent_rotation": ENABLE_USER_AGENT_ROTATION,
            "enable_request_delay": ENABLE_REQUEST_DELAY,
            "enable_random_headers": ENABLE_RANDOM_HEADERS,
            "enable_browser_headers": ENABLE_BROWSER_HEADERS,
            "min_request_delay": MIN_REQUEST_DELAY,
            "max_request_delay": MAX_REQUEST_DELAY,
            "proxy_rotation_mode": PROXY_ROTATION_MODE,
            "use_mobile_agents": USE_MOBILE_AGENTS,
            "proxy_count": len(PROXY_LIST.split(",")) if PROXY_LIST else 0,
            "custom_user_agents_count": len(CUSTOM_USER_AGENTS.split(",")) if CUSTOM_USER_AGENTS else 0
        }
    }