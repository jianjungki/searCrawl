# -*- coding: utf-8 -*-
"""
Anti-Crawl Detection Avoidance Module

This module provides mechanisms to avoid being detected and blocked by anti-crawl systems.
It includes IP proxy rotation, random User-Agent selection, request delays, and other evasion techniques.
"""

import random
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import httpx
from loguru import logger


class ProxyType(Enum):
    """Proxy type enumeration"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"


@dataclass
class ProxyConfig:
    """Proxy configuration"""
    url: str
    proxy_type: ProxyType = ProxyType.HTTP
    username: Optional[str] = None
    password: Optional[str] = None
    
    def get_proxy_url(self) -> str:
        """Get formatted proxy URL with authentication if needed"""
        if self.username and self.password:
            return f"{self.proxy_type.value}://{self.username}:{self.password}@{self.url}"
        return f"{self.proxy_type.value}://{self.url}"


class UserAgentPool:
    """User-Agent pool for random selection"""
    
    # Common desktop User-Agents
    DESKTOP_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    ]
    
    # Common mobile User-Agents
    MOBILE_USER_AGENTS = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    ]
    
    def __init__(self, custom_agents: Optional[List[str]] = None, use_mobile: bool = False):
        """Initialize User-Agent pool
        
        Args:
            custom_agents: Custom list of User-Agents to use
            use_mobile: Whether to include mobile User-Agents
        """
        self.custom_agents = custom_agents or []
        self.use_mobile = use_mobile
        self._build_pool()
    
    def _build_pool(self) -> None:
        """Build the User-Agent pool"""
        self.pool = self.DESKTOP_USER_AGENTS.copy()
        
        if self.use_mobile:
            self.pool.extend(self.MOBILE_USER_AGENTS)
        
        if self.custom_agents:
            self.pool.extend(self.custom_agents)
        
        logger.info(f"User-Agent pool initialized with {len(self.pool)} agents")
    
    def get_random(self) -> str:
        """Get a random User-Agent from the pool"""
        return random.choice(self.pool)
    
    def get_all(self) -> List[str]:
        """Get all User-Agents in the pool"""
        return self.pool.copy()


class ProxyPool:
    """Proxy pool for IP rotation"""
    
    def __init__(self, proxies: Optional[List[ProxyConfig]] = None):
        """Initialize proxy pool
        
        Args:
            proxies: List of ProxyConfig objects
        """
        self.proxies = proxies or []
        self.current_index = 0
        logger.info(f"Proxy pool initialized with {len(self.proxies)} proxies")
    
    def add_proxy(self, proxy: ProxyConfig) -> None:
        """Add a proxy to the pool"""
        self.proxies.append(proxy)
        logger.info(f"Proxy added: {proxy.url}")
    
    def add_proxies(self, proxies: List[ProxyConfig]) -> None:
        """Add multiple proxies to the pool"""
        self.proxies.extend(proxies)
        logger.info(f"Added {len(proxies)} proxies to pool")
    
    def get_random(self) -> Optional[ProxyConfig]:
        """Get a random proxy from the pool"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def get_next(self) -> Optional[ProxyConfig]:
        """Get the next proxy in rotation"""
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_all(self) -> List[ProxyConfig]:
        """Get all proxies in the pool"""
        return self.proxies.copy()
    
    def is_available(self) -> bool:
        """Check if proxy pool has available proxies"""
        return len(self.proxies) > 0


class RequestHeaderGenerator:
    """Generate realistic request headers"""
    
    @staticmethod
    def generate_headers(user_agent: str, include_referer: bool = True) -> Dict[str, str]:
        """Generate realistic request headers
        
        Args:
            user_agent: User-Agent string
            include_referer: Whether to include Referer header
            
        Returns:
            Dictionary of headers
        """
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice([
                "en-US,en;q=0.9",
                "zh-CN,zh;q=0.9",
                "en-US,en;q=0.9,zh-CN;q=0.8",
            ]),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }
        
        if include_referer:
            headers["Referer"] = random.choice([
                "https://www.google.com/",
                "https://www.bing.com/",
                "https://www.baidu.com/",
                "https://www.duckduckgo.com/",
            ])
        
        return headers


class AntiCrawlConfig:
    """Anti-crawl configuration"""
    
    def __init__(
        self,
        enable_proxy_rotation: bool = False,
        enable_user_agent_rotation: bool = True,
        enable_request_delay: bool = True,
        enable_random_headers: bool = True,
        enable_browser_headers: bool = True,
        min_delay: float = 0.5,
        max_delay: float = 3.0,
        proxy_rotation_mode: str = "random",  # "random" or "sequential"
        custom_user_agents: Optional[List[str]] = None,
        use_mobile_agents: bool = False,
        proxies: Optional[List[ProxyConfig]] = None,
    ):
        """Initialize anti-crawl configuration
        
        Args:
            enable_proxy_rotation: Enable IP proxy rotation
            enable_user_agent_rotation: Enable User-Agent rotation
            enable_request_delay: Enable random request delays
            enable_random_headers: Enable random header generation
            enable_browser_headers: Enable realistic browser headers
            min_delay: Minimum delay between requests (seconds)
            max_delay: Maximum delay between requests (seconds)
            proxy_rotation_mode: Proxy rotation mode ("random" or "sequential")
            custom_user_agents: Custom User-Agent list
            use_mobile_agents: Include mobile User-Agents
            proxies: List of proxy configurations
        """
        self.enable_proxy_rotation = enable_proxy_rotation
        self.enable_user_agent_rotation = enable_user_agent_rotation
        self.enable_request_delay = enable_request_delay
        self.enable_random_headers = enable_random_headers
        self.enable_browser_headers = enable_browser_headers
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.proxy_rotation_mode = proxy_rotation_mode
        
        # Initialize User-Agent pool
        self.user_agent_pool = UserAgentPool(
            custom_agents=custom_user_agents,
            use_mobile=use_mobile_agents
        )
        
        # Initialize proxy pool
        self.proxy_pool = ProxyPool(proxies=proxies)
        
        logger.info("AntiCrawlConfig initialized")
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with anti-crawl measures applied"""
        user_agent = self.user_agent_pool.get_random() if self.enable_user_agent_rotation else self.user_agent_pool.get_all()[0]
        
        if self.enable_random_headers or self.enable_browser_headers:
            return RequestHeaderGenerator.generate_headers(user_agent)
        
        return {"User-Agent": user_agent}
    
    def get_proxy(self) -> Optional[str]:
        """Get proxy URL with anti-crawl measures applied"""
        if not self.enable_proxy_rotation or not self.proxy_pool.is_available():
            return None
        
        if self.proxy_rotation_mode == "sequential":
            proxy_config = self.proxy_pool.get_next()
        else:
            proxy_config = self.proxy_pool.get_random()
        
        return proxy_config.get_proxy_url() if proxy_config else None
    
    def get_delay(self) -> float:
        """Get random delay between requests"""
        if not self.enable_request_delay:
            return 0
        
        return random.uniform(self.min_delay, self.max_delay)
    
    def apply_delay(self) -> None:
        """Apply delay before making a request"""
        delay = self.get_delay()
        if delay > 0:
            logger.debug(f"Applying request delay: {delay:.2f}s")
            time.sleep(delay)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "enable_proxy_rotation": self.enable_proxy_rotation,
            "enable_user_agent_rotation": self.enable_user_agent_rotation,
            "enable_request_delay": self.enable_request_delay,
            "enable_random_headers": self.enable_random_headers,
            "enable_browser_headers": self.enable_browser_headers,
            "min_delay": self.min_delay,
            "max_delay": self.max_delay,
            "proxy_rotation_mode": self.proxy_rotation_mode,
            "proxy_count": len(self.proxy_pool.proxies),
            "user_agent_count": len(self.user_agent_pool.pool),
        }
