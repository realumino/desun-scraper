# 世格外贸单证教学系统题目下载器

## 项目简介

这是一个基于 Python 和 Selenium 的自动化工具，用于从世格外贸单证教学系统下载题目相关的所有文件，包括：

- 要求和说明文档
- 参考文件
- 参考答案

项目采用模块化设计，支持用户自定义配置系统访问地址和 ChromeDriver 路径，具有高度的灵活性和易用性。

## 功能特点

- ✅ **智能配置管理**：支持用户交互式配置系统 URL 和 ChromeDriver 路径
- ✅ **输入验证机制**：自动验证 URL 格式和文件路径有效性
- ✅ **手动登录支持**：尊重网站安全机制，支持手动登录后自动接管
- ✅ **自动解析下载**：智能解析题目列表，自动下载所有相关文件
- ✅ **文件组织管理**：按题目编号和名称创建文件夹，规范化文件命名
- ✅ **错误处理机制**：完善的异常处理和错误提示
- ✅ **会话保持**：自动管理 cookies 和会话状态

## 环境要求

- **Python**: 3.7+
- **浏览器**: Chrome 浏览器
- **驱动**: ChromeDriver (与 Chrome 版本匹配)

## 核心依赖

- `selenium>=4.0.0` - 浏览器自动化框架
- `requests>=2.25.0` - HTTP 请求库

## 安装步骤

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 ChromeDriver

- 从 [ChromeDriver 官网](https://chromedriver.chromium.org/) 下载对应版本的 ChromeDriver
- 可选择以下任一方式：
  - 将 ChromeDriver 添加到系统 PATH 环境变量中
  - 在程序运行时手动指定 ChromeDriver 完整路径

## 使用方法

### 基本使用流程

1. **启动程序**：

```bash
python scraper.py
```

2. **配置系统访问地址**：

   - 程序启动后，首先提示输入世格外贸单证教学系统的完整 URL
   - 格式要求：必须以 `http://` 或 `https://` 开头

3. **配置 ChromeDriver 路径**：

   - 输入 ChromeDriver 的完整路径
   - 如不输入，将使用默认路径 `C:/WebDriver/bin/chromedriver.exe`
   - 路径验证：确保文件存在且为有效的.exe 文件

4. **手动登录系统**：

   - 程序自动打开 Chrome 浏览器并导航到登录页面
   - **手动输入**用户名和密码完成登录
   - 登录成功后，在命令行按回车键继续

5. **自动下载过程**：
   - 程序自动导航到题目列表页面
   - 解析所有题目信息
   - 为每个题目创建独立文件夹
   - 下载所有相关文件（要求文档、参考文件、参考答案）
   - 解析所有题目信息
   - 为每个题目创建文件夹
   - 下载所有相关文件

## 核心功能说明

### 配置管理模块

- **`get_base_url_from_user()`**: 交互式获取系统 URL，包含格式验证和用户确认
- **`get_chromedriver_path_from_user()`**: 获取 ChromeDriver 路径，支持默认值和自定义路径
- **输入验证**: 自动验证 URL 格式、文件存在性、文件类型等

### 浏览器自动化模块

- **`DesunScraper`类**: 核心爬虫类，管理整个下载流程
- **`setup_driver()`**: 配置 Chrome 浏览器和驱动，支持自定义 ChromeDriver 路径
- **`manual_login()`**: 手动登录流程，自动获取 cookies 用于后续请求

### 数据解析模块

- **`parse_question_list()`**: 解析题目列表，提取题目编号、名称和链接
- **`process_question()`**: 处理单个题目，下载所有相关文件
- **文件命名**: 自动从 URL 提取文件名，添加序号前缀

### 文件下载模块

- **`download_file()`**: 基于 requests 会话下载文件，支持大文件流式下载
- **文件夹管理**: 自动创建题目文件夹，清理非法字符
- **进度显示**: 实时显示下载进度和状态

## 文件保存结构

下载的文件将保存在 `downloads` 目录下，结构如下：

```
downloads/
├── 010101-建立业务关系/
│   ├── 010101Q_requirement.mht
│   ├── 参考文件_1_010101Q_mail.mht
│   └── 参考答案_1_010101A_introduce.mht
├── 010102-建立业务关系/
│   ├── 010102Q_requirement.mht
│   ├── 参考文件_1_010102Q_mail.mht
│   └── 参考答案_1_010102A_introduce.mht
├── 010201-询盘/
│   ├── 010201Q_requirement.mht
│   ├── 参考文件_1_010201Q_mail.mht
│   └── 参考答案_1_010201A_enquiry.mht
└── ...
```

## 接口调用方式

### 直接实例化使用

```python
from scraper import DesunScraper

# 创建爬虫实例
scraper = DesunScraper(
    base_url="http://your-system-url.com/doc",
    chromedriver_path="C:/path/to/chromedriver.exe"
)

# 运行下载程序
scraper.run()
```

### 自定义配置流程

```python
from scraper import DesunScraper, get_base_url_from_user, get_chromedriver_path_from_user

# 获取用户配置
base_url = get_base_url_from_user()
chromedriver_path = get_chromedriver_path_from_user()

# 创建并运行爬虫
scraper = DesunScraper(base_url=base_url, chromedriver_path=chromedriver_path)
scraper.run()
```

## 输入输出格式

### 输入参数

- **base_url**: 系统访问地址，必须包含协议头
- **chromedriver_path**: ChromeDriver 可执行文件路径（可选）

### 输出文件

- **文件格式**: 主要为.mht 格式，可用浏览器直接打开
- **命名规范**:
  - 文件夹: `题目编号-题目名称`
  - 要求文档: `题目编号Q_requirement.mht`
  - 参考文件: `参考文件_序号_文件名.mht`
  - 参考答案: `参考答案_序号_文件名.mht`

## 注意事项

1. **登录操作**: 由于网站安全机制，首次登录需要手动完成
2. **网络连接**: 确保网络连接稳定，避免下载中断
3. **Chrome 版本**: 确保 ChromeDriver 版本与 Chrome 浏览器版本匹配
4. **权限要求**: 确保有足够的文件读写权限
5. **系统兼容**: 目前主要支持 Windows 系统，其他系统可能需要路径调整

## 故障排除

### 常见问题

- **程序无法启动**: 检查 Python 环境、依赖包安装、ChromeDriver 配置
- **浏览器无法打开**: 验证 ChromeDriver 路径是否正确，版本是否匹配
- **登录失败**: 确认系统 URL 正确，网络连接正常
- **下载中断**: 检查网络稳定性，重新运行程序

### 错误信息说明

- **URL 格式错误**: 确保 URL 以 http://或 https://开头
- **文件路径不存在**: 检查 ChromeDriver 路径是否正确
- **权限拒绝**: 确保有足够的文件读写权限

## 技术架构

- **自动化框架**: Selenium WebDriver
- **HTTP 请求**: requests 库
- **文件处理**: Python 标准库 os、re 模块
- **URL 处理**: urllib.parse 模块
- **用户交互**: 标准输入输出

## 扩展方向

1. **配置文件支持**: 添加配置文件支持，避免重复输入
2. **多线程下载**: 实现并发下载提升效率
3. **断点续传**: 支持下载中断后继续下载
4. **GUI 界面**: 开发图形用户界面
5. **多平台支持**: 增强 Linux 和 macOS 兼容性
6. **错误恢复**: 增强错误处理和自动重试机制

## 开发说明

项目采用模块化设计，核心类`DesunScraper`封装了所有功能逻辑，各方法职责明确，便于维护和扩展。
