# -*- coding: utf-8 -*-
"""
Crawler Module - Provides web crawling and content processing functionality

This module provides web crawling and content processing functionality.
It encapsulates the AsyncWebCrawler from crawl4ai library and provides
high-level methods for crawling web pages and processing their content.
"""

from typing import List, Dict, Any, Optional, AsyncGenerator
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
)
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter
import markdown
from bs4 import BeautifulSoup
import re
import httpx
import json
import asyncio
from fastapi import HTTPException
from loguru import logger

# Import configuration
from .config import (
    SEARXNG_HOST,
    SEARXNG_PORT,
    SEARXNG_BASE_PATH,
    DISABLED_ENGINES,
    ENABLED_ENGINES,
    SEARCH_LANGUAGE,
    CONTENT_FILTER_THRESHOLD,
    WORD_COUNT_THRESHOLD,
    ANTI_CRAWL_ENABLED,
    ENABLE_PROXY_ROTATION,
    ENABLE_USER_AGENT_ROTATION,
    ENABLE_REQUEST_DELAY,
    ENABLE_RANDOM_HEADERS,
    ENABLE_BROWSER_HEADERS,
    MIN_REQUEST_DELAY,
    MAX_REQUEST_DELAY,
    PROXY_ROTATION_MODE,
    USE_MOBILE_AGENTS,
    PROXY_LIST,
    CUSTOM_USER_AGENTS,
    READER_ENABLED,
)
from .reader import fetch_with_reader
from .cache import CacheManager
from .anti_crawl import (
    AntiCrawlConfig,
    ProxyConfig,
    ProxyType
)


class WebCrawler:
    """Web crawler class that encapsulates web crawling and content processing functionality"""

    def __init__(self, cache_manager: Optional[CacheManager] = None, anti_crawl_config: Optional[AntiCrawlConfig] = None):
        """Initialize crawler instance
        
        Args:
            cache_manager: Optional cache manager instance for caching crawl results
            anti_crawl_config: Optional anti-crawl configuration for evasion techniques
        """
        self.crawler: Optional[AsyncWebCrawler] = None
        self.cache_manager = cache_manager
        self.anti_crawl_config = anti_crawl_config or self._create_default_anti_crawl_config()
        logger.info("Initializing WebCrawler instance")
        logger.info(f"Anti-crawl configuration: {self.anti_crawl_config.to_dict()}")

    def _create_default_anti_crawl_config(self) -> AntiCrawlConfig:
        """Create default anti-crawl configuration from environment variables"""
        if not ANTI_CRAWL_ENABLED:
            logger.info("Anti-crawl features disabled")
            return AntiCrawlConfig(
                enable_proxy_rotation=False,
                enable_user_agent_rotation=False,
                enable_request_delay=False,
                enable_random_headers=False,
                enable_browser_headers=False
            )
        
        # Parse proxy list
        proxies = []
        if PROXY_LIST:
            for proxy_str in PROXY_LIST.split(","):
                proxy_str = proxy_str.strip()
                if not proxy_str:
                    continue
                
                try:
                    # Parse proxy URL format: http://user:pass@host:port or http://host:port
                    if "@" in proxy_str:
                        # Has authentication
                        parts = proxy_str.split("://")
                        if len(parts) == 2:
                            protocol = parts[0]
                            auth_and_host = parts[1].split("@")
                            if len(auth_and_host) == 2:
                                auth = auth_and_host[0].split(":")
                                host = auth_and_host[1]
                                if len(auth) == 2:
                                    proxies.append(ProxyConfig(
                                        url=host,
                                        proxy_type=ProxyType(protocol),
                                        username=auth[0],
                                        password=auth[1]
                                    ))
                    else:
                        # No authentication
                        parts = proxy_str.split("://")
                        if len(parts) == 2:
                            protocol = parts[0]
                            host = parts[1]
                            proxies.append(ProxyConfig(
                                url=host,
                                proxy_type=ProxyType(protocol)
                            ))
                except Exception as e:
                    logger.warning(f"Failed to parse proxy: {proxy_str}, error: {e}")
        
        # Parse custom user agents
        custom_agents = []
        if CUSTOM_USER_AGENTS:
            custom_agents = [ua.strip() for ua in CUSTOM_USER_AGENTS.split(",") if ua.strip()]
        
        return AntiCrawlConfig(
            enable_proxy_rotation=ENABLE_PROXY_ROTATION,
            enable_user_agent_rotation=ENABLE_USER_AGENT_ROTATION,
            enable_request_delay=ENABLE_REQUEST_DELAY,
            enable_random_headers=ENABLE_RANDOM_HEADERS,
            enable_browser_headers=ENABLE_BROWSER_HEADERS,
            min_delay=MIN_REQUEST_DELAY,
            max_delay=MAX_REQUEST_DELAY,
            proxy_rotation_mode=PROXY_ROTATION_MODE,
            custom_user_agents=custom_agents,
            use_mobile_agents=USE_MOBILE_AGENTS,
            proxies=proxies
        )

    async def initialize(self) -> None:
        """Initialize AsyncWebCrawler instance

        Must be called before using the crawler
        """
        # Build browser config with anti-crawl settings
        if ANTI_CRAWL_ENABLED:
            # Get anti-crawl headers
            headers = self.anti_crawl_config.get_headers()
            
            # Get proxy if enabled
            proxy = self.anti_crawl_config.get_proxy()
            
            # Add browser arguments to hide automation
            extra_args = [
                "--disable-blink-features=AutomationControlled",  # Hide automation
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
            
            # Configure browser with anti-crawl settings
            browser_config = BrowserConfig(
                headless=True,
                verbose=False,
                extra_args=extra_args,
                headers=headers if headers else {},
                proxy=proxy if proxy else ""
            )
        else:
            # Configure browser without anti-crawl settings
            browser_config = BrowserConfig(headless=True, verbose=False)
        
        # Initialize crawler
        self.crawler = await AsyncWebCrawler(config=browser_config).__aenter__()
        logger.info("AsyncWebCrawler initialization completed with anti-crawl features")

    async def close(self) -> None:
        """Close crawler instance and release resources"""
        if self.crawler:
            await self.crawler.__aexit__(None, None, None)
            logger.info("AsyncWebCrawler closed")

    @staticmethod
    def markdown_to_text_regex(markdown_str: str) -> str:
        """Convert Markdown text to plain text using regular expressions

        Args:
            markdown_str: Markdown formatted text

        Returns:
            str: Converted plain text
        """
        # Remove heading symbols
        text = re.sub(r'#+\s*', '', markdown_str)

        # Remove links and images
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove bold, italic, and other emphasis markers
        text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
        text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)

        # Remove list markers
        text = re.sub(r'^[\*\-\+]\s*', '', text, flags=re.MULTILINE)

        # Remove code blocks
        text = re.sub(r'`{3}.*?`{3}', '', text, flags=re.DOTALL)
        text = re.sub(r'`(.*?)`', r'\1', text)

        # Remove quote blocks
        text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)

        return text.strip()

    @staticmethod
    def markdown_to_text(markdown_str: str) -> str:
        """Convert Markdown text to plain text using markdown and BeautifulSoup libraries

        Args:
            markdown_str: Markdown formatted text

        Returns:
            str: Converted plain text
        """
        html = markdown.markdown(markdown_str, extensions=['fenced_code'])
        # Extract plain text using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        text = soup.get_text(separator="\n")  # Preserve paragraph line breaks

        # Clean up extra blank lines
        cleaned_text = "\n".join([
            line.strip() for line in text.split("\n") if line.strip()
        ])

        return cleaned_text

    @staticmethod
    async def make_searxng_request(
        query: str,
        limit: int = 10,
        disabled_engines: str = DISABLED_ENGINES,
        enabled_engines: str = ENABLED_ENGINES
    ) -> dict:
        """Send search request to SearXNG

        Args:
            query: Search query string
            limit: Limit on number of results to return
            disabled_engines: List of disabled search engines, comma-separated
            enabled_engines: List of enabled search engines, comma-separated

        Returns:
            dict: Search results returned by SearXNG

        Raises:
            Exception: Raised when request fails
        """
        try:
            form_data = {
                'q': query,
                'format': 'json',
                'language': SEARCH_LANGUAGE,
                'time_range': 'week',
                'safesearch': '2',
                'pageno': '1',
                'category_general': '1'
            }

            headers = {
                'Cookie': f'disabled_engines={disabled_engines};enabled_engines={enabled_engines};method=POST',
                'User-Agent': 'Sear-Crawl4AI/1.0.0',
                'Accept': '*/*',
                'Host': f'{SEARXNG_HOST}:{SEARXNG_PORT}',
                'Connection': 'keep-alive',
            }
            
            url = f"http://{SEARXNG_HOST}:{SEARXNG_PORT}{SEARXNG_BASE_PATH}"

            async with httpx.AsyncClient() as client:
                logger.info(f"Sending search request to SearXNG: {query}")
                response = await client.post(url, data=form_data, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"SearXNG request failed with status {e.response.status_code}: {e.response.text}")
            raise Exception(f"Search request failed: {e.response.text}")
        except Exception as e:
            logger.error(f"SearXNG request failed: {str(e)}")
            raise Exception(f"Search request failed: {str(e)}")

    async def crawl_urls(self, urls: List[str], instruction: str) -> Dict[str, Any]:
        """Crawl multiple URLs and process content

        Args:
            urls: List of URLs to crawl
            instruction: Crawling instruction, typically a search query

        Returns:
            Dict[str, Any]: Dictionary containing processed content, success count, and failed URLs

        Raises:
            HTTPException: Raised when all URL crawls fail
        """
        try:
            # Check if crawler has been initialized
            if not self.crawler:
                logger.warning("Crawler not initialized, auto-initializing")
                await self.initialize()

            # Check cache first if cache manager is available
            cached_results = []
            urls_to_process = []
            
            if self.cache_manager and self.cache_manager.is_available():
                logger.info(f"Checking cache for {len(urls)} URLs")
                cache_hits = self.cache_manager.get_batch(urls, instruction)
                
                for url in urls:
                    cached_data = cache_hits.get(url)
                    if cached_data:
                        cached_results.append({
                            "content": cached_data.get("content"),
                            "reference": cached_data.get("reference")
                        })
                        logger.info(f"Cache hit for URL: {url}")
                    else:
                        urls_to_process.append(url)
                
                logger.info(f"Cache hits: {len(cached_results)}, URLs to process: {len(urls_to_process)}")
            else:
                urls_to_process = urls
                logger.info("Cache not available, processing all URLs")

            # If all URLs are cached, return cached results
            if not urls_to_process:
                logger.info("All URLs found in cache, returning cached results")
                return {
                    "results": cached_results,
                    "success_count": len(cached_results),
                    "failed_urls": [],
                    "cache_hits": len(cached_results)
                }

            all_results = []
            failed_urls = []

            all_results = []
            failed_urls = []

            if READER_ENABLED:
                # --- Jina Reader Path ---
                logger.info(f"Using Jina Reader service for {len(urls_to_process)} URLs")
                tasks = [fetch_with_reader(url) for url in urls_to_process]
                reader_results = await asyncio.gather(*tasks)
                
                for result in reader_results:
                    if result:
                        all_results.append(result)
                    # In a strict either/or setup, we don't fallback, so we just log failures.
                    # The failed URLs will be collected at the end.

            else:
                # --- Crawl4AI Path ---
                urls_to_crawl = urls_to_process
                logger.info(f"Using Crawl4AI for {len(urls_to_crawl)} URLs")
                
                # Configure Markdown generator
                md_generator = DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter(threshold=CONTENT_FILTER_THRESHOLD),
                    options={
                        "ignore_links": True,
                        "ignore_images": True,
                        "escape_html": False,
                    }
                )

                # Configure crawler run parameters
                run_config = CrawlerRunConfig(
                    word_count_threshold=WORD_COUNT_THRESHOLD,
                    exclude_external_links=True,
                    remove_overlay_elements=True,
                    excluded_tags=['img', 'header', 'footer', 'iframe', 'nav'],
                    process_iframes=True,
                    markdown_generator=md_generator,
                    cache_mode=CacheMode.BYPASS
                )

                logger.info(f"Starting to crawl URLs: {', '.join(urls_to_crawl)}")
                
                # Apply anti-crawl delay before crawling
                if ANTI_CRAWL_ENABLED and self.anti_crawl_config.enable_request_delay:
                    self.anti_crawl_config.apply_delay()
                
                # Ensure crawler is initialized
                if not self.crawler:
                    raise RuntimeError("Crawler not initialized")
                
                # Crawl URLs and get results
                crawl_result = await self.crawler.arun_many(urls=urls_to_crawl, config=run_config)
                
                # Convert to list if it's an async generator
                results: list = []
                if hasattr(crawl_result, '__aiter__'):
                    async for result in crawl_result:  # type: ignore
                        results.append(result)
                else:
                    results = list(crawl_result) if crawl_result else []  # type: ignore

                # Create a list to store crawl results from all successful URLs
                retry_urls = []

                # First crawl attempt processing
                for i, result in enumerate(results):
                    try:
                        if result is None:
                            logger.debug(f"URL crawl result is None: {urls_to_crawl[i]}")
                            retry_urls.append(urls_to_crawl[i])
                            continue

                        if not hasattr(result, 'success'):
                            logger.debug(f"URL crawl result missing success attribute: {urls_to_crawl[i]}")
                            retry_urls.append(urls_to_crawl[i])
                            continue

                        if result.success:
                            if not hasattr(result, 'markdown') or not hasattr(result.markdown, 'fit_markdown'):
                                logger.debug(f"URL crawl result missing markdown content: {urls_to_crawl[i]}")
                                retry_urls.append(urls_to_crawl[i])
                                continue

                            # Add successful result's markdown content to the list
                            all_results.append({
                                "content": result.markdown.fit_markdown,
                                "reference": urls_to_crawl[i]
                            })
                            logger.info(f"Successfully crawled URL: {urls_to_crawl[i]}")
                        else:
                            logger.debug(f"URL crawl failed: {urls_to_crawl[i]}")
                            retry_urls.append(urls_to_crawl[i])
                    except Exception as e:
                        # Record URLs that need retry
                        retry_urls.append(urls_to_crawl[i])
                        error_msg = str(e)
                        logger.warning(f"URL first crawl attempt failed: {urls_to_crawl[i]}, error: {error_msg}")

                # If there are URLs to retry, perform second crawl attempt
                if retry_urls:
                    logger.info(f"Retrying failed URLs: {', '.join(retry_urls)}")
                    
                    # Crawl retry URLs and get results
                    retry_crawl_result = await self.crawler.arun_many(urls=retry_urls, config=run_config)
                    
                    # Convert to list if it's an async generator
                    retry_results: list = []
                    if hasattr(retry_crawl_result, '__aiter__'):
                        async for result in retry_crawl_result:  # type: ignore
                            retry_results.append(result)
                    else:
                        retry_results = list(retry_crawl_result) if retry_crawl_result else []  # type: ignore

                    for i, result in enumerate(retry_results):
                        try:
                            if result is None:
                                logger.debug(f"Retry URL crawl result is None: {retry_urls[i]}")
                                failed_urls.append(retry_urls[i])
                                continue

                            if not hasattr(result, 'success'):
                                logger.debug(f"Retry URL crawl result missing success attribute: {retry_urls[i]}")
                                failed_urls.append(retry_urls[i])
                                continue

                            if result.success:
                                if not hasattr(result, 'markdown') or not hasattr(result.markdown, 'fit_markdown'):
                                    logger.debug(f"Retry URL crawl result missing markdown content: {retry_urls[i]}")
                                    failed_urls.append(retry_urls[i])
                                    continue

                                # Add successful retry result to the list
                                all_results.append({
                                    "content": result.markdown.fit_markdown,
                                    "reference": retry_urls[i]
                                })
                                logger.info(f"Successfully crawled URL on retry: {retry_urls[i]}")
                            else:
                                logger.debug(f"Retry URL crawl still failed: {retry_urls[i]}")
                                failed_urls.append(retry_urls[i])
                        except Exception as e:
                            # Record finally failed URLs
                            failed_urls.append(retry_urls[i])
                            error_msg = str(e)
                            logger.error(f"URL second crawl attempt failed: {retry_urls[i]}, error: {error_msg}")
            
            # Consolidate failed URLs
            crawled_urls = {res["reference"] for res in all_results}
            failed_urls.extend([url for url in urls_to_process if url not in crawled_urls])

            if not all_results:
                logger.error("All URL crawls failed")
                raise HTTPException(status_code=500, detail="All URL crawls failed")

            # Process each result to convert markdown to plain text
            processed_results = []
            for result in all_results:
                plain_text = self.markdown_to_text_regex(self.markdown_to_text(result["content"]))
                processed_results.append({
                    "content": plain_text,
                    "reference": result["reference"]
                })

            # Cache newly crawled results
            if self.cache_manager and self.cache_manager.is_available() and processed_results:
                cache_items = []
                for result in processed_results:
                    cache_items.append({
                        "url": result["reference"],
                        "content": result["content"],
                        "reference": result["reference"]
                    })
                cached_count = self.cache_manager.set_batch(cache_items, instruction)
                logger.info(f"Cached {cached_count} newly crawled results")

            # Combine cached and newly crawled results
            all_processed_results = cached_results + processed_results

            response = {
                "results": all_processed_results,
                "success_count": len(all_processed_results),
                "failed_urls": failed_urls,
                "cache_hits": len(cached_results),
                "newly_crawled": len(processed_results)
            }

            logger.info(f"Crawl completed, total: {len(all_processed_results)}, cache hits: {len(cached_results)}, newly crawled: {len(processed_results)}, failed: {len(failed_urls)}")
            return response
        except Exception as e:
            logger.error(f"Exception occurred during crawling: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
