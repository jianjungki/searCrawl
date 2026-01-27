# 反防爬机制使用指南 / Anti-Crawl Detection Avoidance Guide

[English](#english) | [中文](#中文)

---

## 中文

### 概述

SearCrawl 集成了完善的反防爬机制，帮助您避免被目标网站的反爬虫系统检测和封禁。该机制包括以下核心功能：

- **IP 代理池轮换**：支持多个代理服务器轮换使用
- **User-Agent 随机化**：内置丰富的 User-Agent 池，支持自定义
- **请求延迟**：随机延迟请求，模拟真实用户行为
- **随机请求头**：生成真实的浏览器请求头
- **浏览器指纹隐藏**：隐藏自动化特征，避免被检测

### 快速开始

#### 1. 基础配置

在 `.env` 文件中启用反防爬功能：

```bash
# 启用反防爬功能
ANTI_CRAWL_ENABLED=true

# 启用 User-Agent 轮换
ENABLE_USER_AGENT_ROTATION=true

# 启用请求延迟
ENABLE_REQUEST_DELAY=true

# 设置延迟范围（秒）
MIN_REQUEST_DELAY=0.5
MAX_REQUEST_DELAY=3.0
```

#### 2. 配置代理池（可选）

如果需要使用代理服务器：

```bash
# 启用代理轮换
ENABLE_PROXY_ROTATION=true

# 代理轮换模式：random（随机）或 sequential（顺序）
PROXY_ROTATION_MODE=random

# 配置代理列表（逗号分隔）
# 格式：protocol://host:port 或 protocol://username:password@host:port
PROXY_LIST=http://proxy1.com:8080,http://user:pass@proxy2.com:8080,socks5://proxy3.com:1080
```

#### 3. 自定义 User-Agent（可选）

```bash
# 添加自定义 User-Agent
CUSTOM_USER_AGENTS=Mozilla/5.0 (Custom Agent 1),Mozilla/5.0 (Custom Agent 2)

# 是否包含移动端 User-Agent
USE_MOBILE_AGENTS=false
```

### 功能详解

#### 1. IP 代理池轮换

**功能说明**：
- 支持 HTTP、HTTPS、SOCKS5 代理协议
- 支持带认证的代理服务器
- 两种轮换模式：随机选择或顺序轮换

**配置示例**：

```bash
# 启用代理轮换
ENABLE_PROXY_ROTATION=true

# 代理列表示例
PROXY_LIST=http://proxy1.example.com:8080,http://username:password@proxy2.example.com:8080,socks5://proxy3.example.com:1080

# 轮换模式
PROXY_ROTATION_MODE=random  # 或 sequential
```

**注意事项**：
- 确保代理服务器可用且稳定
- 建议使用高质量的付费代理服务
- 免费代理可能不稳定或已被目标网站封禁

#### 2. User-Agent 随机化

**功能说明**：
- 内置 12+ 常见桌面浏览器 User-Agent
- 内置 4+ 常见移动浏览器 User-Agent
- 支持自定义 User-Agent 列表
- 每次请求随机选择

**内置 User-Agent 示例**：
- Chrome (Windows/Mac/Linux)
- Firefox (Windows/Linux)
- Safari (Mac/iOS)
- Edge (Windows)
- 移动端浏览器（可选）

**自定义配置**：

```bash
# 添加自定义 User-Agent
CUSTOM_USER_AGENTS=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)

# 启用移动端 User-Agent
USE_MOBILE_AGENTS=true
```

#### 3. 请求延迟

**功能说明**：
- 在每次爬取前随机延迟
- 模拟真实用户浏览行为
- 可配置延迟范围

**配置示例**：

```bash
# 启用请求延迟
ENABLE_REQUEST_DELAY=true

# 最小延迟（秒）
MIN_REQUEST_DELAY=0.5

# 最大延迟（秒）
MAX_REQUEST_DELAY=3.0
```

**建议**：
- 对于严格的网站，建议设置较长的延迟（2-5秒）
- 对于宽松的网站，可以使用较短的延迟（0.5-2秒）

#### 4. 随机请求头

**功能说明**：
- 自动生成真实的浏览器请求头
- 包括 Accept、Accept-Language、Accept-Encoding 等
- 随机选择 Referer

**自动生成的请求头**：
```
User-Agent: [随机选择]
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: [随机选择：en-US,en;q=0.9 或 zh-CN,zh;q=0.9]
Accept-Encoding: gzip, deflate, br
DNT: 1
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Cache-Control: max-age=0
Referer: [随机选择：Google、Bing、Baidu、DuckDuckGo]
```

**配置**：

```bash
# 启用随机请求头
ENABLE_RANDOM_HEADERS=true

# 启用浏览器级别的请求头
ENABLE_BROWSER_HEADERS=true
```

#### 5. 浏览器指纹隐藏

**功能说明**：
- 隐藏 Playwright/Puppeteer 自动化特征
- 禁用 WebDriver 检测
- 模拟真实浏览器环境

**自动应用的浏览器参数**：
```
--disable-blink-features=AutomationControlled
--disable-dev-shm-usage
--no-sandbox
--disable-setuid-sandbox
--disable-web-security
--disable-features=IsolateOrigins,site-per-process
```

### 完整配置示例

#### 基础配置（推荐新手）

```bash
# 启用反防爬
ANTI_CRAWL_ENABLED=true

# 启用 User-Agent 轮换
ENABLE_USER_AGENT_ROTATION=true

# 启用请求延迟
ENABLE_REQUEST_DELAY=true
MIN_REQUEST_DELAY=1.0
MAX_REQUEST_DELAY=3.0

# 启用随机请求头
ENABLE_RANDOM_HEADERS=true
ENABLE_BROWSER_HEADERS=true

# 不使用代理
ENABLE_PROXY_ROTATION=false
```

#### 高级配置（使用代理）

```bash
# 启用反防爬
ANTI_CRAWL_ENABLED=true

# 启用所有功能
ENABLE_PROXY_ROTATION=true
ENABLE_USER_AGENT_ROTATION=true
ENABLE_REQUEST_DELAY=true
ENABLE_RANDOM_HEADERS=true
ENABLE_BROWSER_HEADERS=true

# 代理配置
PROXY_ROTATION_MODE=random
PROXY_LIST=http://proxy1.com:8080,http://user:pass@proxy2.com:8080

# 延迟配置
MIN_REQUEST_DELAY=2.0
MAX_REQUEST_DELAY=5.0

# User-Agent 配置
USE_MOBILE_AGENTS=true
CUSTOM_USER_AGENTS=Mozilla/5.0 (Custom Agent)
```

### 最佳实践

1. **逐步启用功能**
   - 先启用基础功能（User-Agent、请求头）
   - 如果仍被封禁，再启用代理和延迟

2. **合理设置延迟**
   - 不要设置过短的延迟（< 0.5秒）
   - 根据目标网站的严格程度调整

3. **使用高质量代理**
   - 避免使用免费代理
   - 定期检查代理可用性
   - 使用住宅代理效果更好

4. **监控爬取状态**
   - 查看日志中的成功率
   - 如果失败率高，调整配置

5. **遵守网站规则**
   - 查看网站的 robots.txt
   - 不要过度频繁地爬取
   - 尊重网站的服务条款

### 故障排查

#### 问题：仍然被封禁

**解决方案**：
1. 增加请求延迟时间
2. 启用代理轮换
3. 检查代理是否可用
4. 添加更多自定义 User-Agent

#### 问题：代理连接失败

**解决方案**：
1. 检查代理格式是否正确
2. 验证代理服务器是否在线
3. 确认认证信息是否正确
4. 尝试使用不同的代理协议

#### 问题：爬取速度太慢

**解决方案**：
1. 减少请求延迟时间
2. 使用顺序轮换模式而非随机
3. 考虑是否真的需要所有反防爬功能

### 性能影响

| 功能 | 性能影响 | 推荐场景 |
|------|---------|---------|
| User-Agent 轮换 | 极小 | 所有场景 |
| 随机请求头 | 极小 | 所有场景 |
| 浏览器指纹隐藏 | 小 | 所有场景 |
| 请求延迟 | 中等 | 严格的网站 |
| 代理轮换 | 中等-大 | 被封禁的网站 |

---

## English

### Overview

SearCrawl integrates comprehensive anti-crawl detection avoidance mechanisms to help you avoid being detected and blocked by target websites' anti-bot systems. The mechanism includes the following core features:

- **IP Proxy Pool Rotation**: Support for rotating multiple proxy servers
- **User-Agent Randomization**: Built-in rich User-Agent pool with custom support
- **Request Delays**: Random request delays to simulate real user behavior
- **Random Headers**: Generate realistic browser request headers
- **Browser Fingerprint Hiding**: Hide automation features to avoid detection

### Quick Start

#### 1. Basic Configuration

Enable anti-crawl features in your `.env` file:

```bash
# Enable anti-crawl features
ANTI_CRAWL_ENABLED=true

# Enable User-Agent rotation
ENABLE_USER_AGENT_ROTATION=true

# Enable request delays
ENABLE_REQUEST_DELAY=true

# Set delay range (seconds)
MIN_REQUEST_DELAY=0.5
MAX_REQUEST_DELAY=3.0
```

#### 2. Configure Proxy Pool (Optional)

If you need to use proxy servers:

```bash
# Enable proxy rotation
ENABLE_PROXY_ROTATION=true

# Proxy rotation mode: random or sequential
PROXY_ROTATION_MODE=random

# Configure proxy list (comma-separated)
# Format: protocol://host:port or protocol://username:password@host:port
PROXY_LIST=http://proxy1.com:8080,http://user:pass@proxy2.com:8080,socks5://proxy3.com:1080
```

#### 3. Custom User-Agents (Optional)

```bash
# Add custom User-Agents
CUSTOM_USER_AGENTS=Mozilla/5.0 (Custom Agent 1),Mozilla/5.0 (Custom Agent 2)

# Include mobile User-Agents
USE_MOBILE_AGENTS=false
```

### Feature Details

#### 1. IP Proxy Pool Rotation

**Features**:
- Support for HTTP, HTTPS, SOCKS5 proxy protocols
- Support for authenticated proxy servers
- Two rotation modes: random selection or sequential rotation

**Configuration Example**:

```bash
# Enable proxy rotation
ENABLE_PROXY_ROTATION=true

# Proxy list example
PROXY_LIST=http://proxy1.example.com:8080,http://username:password@proxy2.example.com:8080,socks5://proxy3.example.com:1080

# Rotation mode
PROXY_ROTATION_MODE=random  # or sequential
```

**Notes**:
- Ensure proxy servers are available and stable
- Recommend using high-quality paid proxy services
- Free proxies may be unstable or already blocked by target websites

#### 2. User-Agent Randomization

**Features**:
- Built-in 12+ common desktop browser User-Agents
- Built-in 4+ common mobile browser User-Agents
- Support for custom User-Agent lists
- Random selection for each request

**Built-in User-Agent Examples**:
- Chrome (Windows/Mac/Linux)
- Firefox (Windows/Linux)
- Safari (Mac/iOS)
- Edge (Windows)
- Mobile browsers (optional)

**Custom Configuration**:

```bash
# Add custom User-Agents
CUSTOM_USER_AGENTS=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)

# Enable mobile User-Agents
USE_MOBILE_AGENTS=true
```

#### 3. Request Delays

**Features**:
- Random delay before each crawl
- Simulate real user browsing behavior
- Configurable delay range

**Configuration Example**:

```bash
# Enable request delays
ENABLE_REQUEST_DELAY=true

# Minimum delay (seconds)
MIN_REQUEST_DELAY=0.5

# Maximum delay (seconds)
MAX_REQUEST_DELAY=3.0
```

**Recommendations**:
- For strict websites, recommend longer delays (2-5 seconds)
- For lenient websites, use shorter delays (0.5-2 seconds)

#### 4. Random Headers

**Features**:
- Automatically generate realistic browser request headers
- Include Accept, Accept-Language, Accept-Encoding, etc.
- Random Referer selection

**Auto-generated Headers**:
```
User-Agent: [randomly selected]
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: [randomly selected: en-US,en;q=0.9 or zh-CN,zh;q=0.9]
Accept-Encoding: gzip, deflate, br
DNT: 1
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Cache-Control: max-age=0
Referer: [randomly selected: Google, Bing, Baidu, DuckDuckGo]
```

**Configuration**:

```bash
# Enable random headers
ENABLE_RANDOM_HEADERS=true

# Enable browser-level headers
ENABLE_BROWSER_HEADERS=true
```

#### 5. Browser Fingerprint Hiding

**Features**:
- Hide Playwright/Puppeteer automation features
- Disable WebDriver detection
- Simulate real browser environment

**Auto-applied Browser Arguments**:
```
--disable-blink-features=AutomationControlled
--disable-dev-shm-usage
--no-sandbox
--disable-setuid-sandbox
--disable-web-security
--disable-features=IsolateOrigins,site-per-process
```

### Complete Configuration Examples

#### Basic Configuration (Recommended for Beginners)

```bash
# Enable anti-crawl
ANTI_CRAWL_ENABLED=true

# Enable User-Agent rotation
ENABLE_USER_AGENT_ROTATION=true

# Enable request delays
ENABLE_REQUEST_DELAY=true
MIN_REQUEST_DELAY=1.0
MAX_REQUEST_DELAY=3.0

# Enable random headers
ENABLE_RANDOM_HEADERS=true
ENABLE_BROWSER_HEADERS=true

# Don't use proxies
ENABLE_PROXY_ROTATION=false
```

#### Advanced Configuration (With Proxies)

```bash
# Enable anti-crawl
ANTI_CRAWL_ENABLED=true

# Enable all features
ENABLE_PROXY_ROTATION=true
ENABLE_USER_AGENT_ROTATION=true
ENABLE_REQUEST_DELAY=true
ENABLE_RANDOM_HEADERS=true
ENABLE_BROWSER_HEADERS=true

# Proxy configuration
PROXY_ROTATION_MODE=random
PROXY_LIST=http://proxy1.com:8080,http://user:pass@proxy2.com:8080

# Delay configuration
MIN_REQUEST_DELAY=2.0
MAX_REQUEST_DELAY=5.0

# User-Agent configuration
USE_MOBILE_AGENTS=true
CUSTOM_USER_AGENTS=Mozilla/5.0 (Custom Agent)
```

### Best Practices

1. **Enable Features Gradually**
   - Start with basic features (User-Agent, headers)
   - If still blocked, enable proxies and delays

2. **Set Reasonable Delays**
   - Don't set delays too short (< 0.5 seconds)
   - Adjust based on target website's strictness

3. **Use High-Quality Proxies**
   - Avoid free proxies
   - Regularly check proxy availability
   - Residential proxies work better

4. **Monitor Crawl Status**
   - Check success rate in logs
   - Adjust configuration if failure rate is high

5. **Respect Website Rules**
   - Check website's robots.txt
   - Don't crawl too frequently
   - Respect website's terms of service

### Troubleshooting

#### Issue: Still Getting Blocked

**Solutions**:
1. Increase request delay time
2. Enable proxy rotation
3. Check if proxies are working
4. Add more custom User-Agents

#### Issue: Proxy Connection Failed

**Solutions**:
1. Check proxy format is correct
2. Verify proxy server is online
3. Confirm authentication credentials are correct
4. Try different proxy protocols

#### Issue: Crawling Too Slow

**Solutions**:
1. Reduce request delay time
2. Use sequential rotation instead of random
3. Consider if all anti-crawl features are necessary

### Performance Impact

| Feature | Performance Impact | Recommended Scenario |
|---------|-------------------|---------------------|
| User-Agent Rotation | Minimal | All scenarios |
| Random Headers | Minimal | All scenarios |
| Browser Fingerprint Hiding | Small | All scenarios |
| Request Delays | Medium | Strict websites |
| Proxy Rotation | Medium-Large | Blocked websites |

---

## 技术架构 / Technical Architecture

### 模块结构 / Module Structure

```
src/crawler/
├── anti_crawl.py          # 反防爬核心模块 / Anti-crawl core module
├── config.py              # 配置管理 / Configuration management
└── crawler.py             # 爬虫主模块 / Main crawler module
```

### 类图 / Class Diagram

```
AntiCrawlConfig
├── UserAgentPool          # User-Agent 池管理
├── ProxyPool              # 代理池管理
└── RequestHeaderGenerator # 请求头生成器
```

### 工作流程 / Workflow

1. 初始化爬虫时加载反防爬配置
2. 从配置中解析代理列表和自定义 User-Agent
3. 初始化浏览器时应用反防爬设置
4. 每次爬取前应用请求延迟
5. 动态生成请求头和选择代理

---

## 更新日志 / Changelog

### v1.0.0 (2026-01-14)

- ✨ 初始版本发布
- ✨ 支持 IP 代理池轮换
- ✨ 支持 User-Agent 随机化
- ✨ 支持请求延迟
- ✨ 支持随机请求头生成
- ✨ 支持浏览器指纹隐藏

---

## 许可证 / License

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
