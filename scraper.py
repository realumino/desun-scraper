#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世格外贸单证教学系统题目下载器
根据模板HTML结构自动下载题目相关文件
"""

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin, urlparse
import re


class DesunScraper:
    def __init__(self, base_url=None, chromedriver_path=None):
        self.driver = None
        self.base_url = base_url
        self.chromedriver_path = chromedriver_path
        self.session = requests.Session()
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        
        # 创建下载目录
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
    
    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        chrome_options = Options()
        # 设置下载目录
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # 使用用户指定的chromedriver路径，如果没有指定则使用默认路径
        chromedriver_path = self.chromedriver_path or "C:/WebDriver/bin/chromedriver.exe"
        service = webdriver.ChromeService(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(options=chrome_options, service=service)
        self.driver.implicitly_wait(10)
    
    def manual_login(self):
        """手动登录流程"""
        print("正在打开登录页面...")
        self.driver.get(f"{self.base_url}/Default.aspx")
        
        print("=" * 50)
        print("请手动完成登录操作:")
        print("1. 在浏览器中输入用户名和密码")
        print("2. 点击登录按钮")
        print("3. 登录成功后，程序将自动接管浏览器")
        print("=" * 50)
        
        # 等待用户手动登录
        input("按回车键继续（确认已登录成功）...")
        
        # 获取登录后的cookies用于requests会话
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])
    
    def navigate_to_question_list(self):
        """导航到题目列表页面"""
        print("正在导航到题目列表页面...")
        # 根据模板，题目列表页面的URL格式
        self.driver.get(f"{self.base_url}/Main.aspx?tabindex=1&tabid=6")
        
        # 等待页面加载完成
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tr"))
        )
    
    def parse_question_list(self):
        """解析题目列表"""
        print("正在解析题目列表...")
        questions = []
        
        # 查找题目表格行
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table tr[style*='color:#000066']")
        
        for row in rows:
            try:
                # 提取题目编号
                question_id = row.find_element(By.CSS_SELECTOR, "td:first-child").text.strip()
                
                # 提取题目名称
                question_name = row.find_element(By.CSS_SELECTOR, "span[id*='LabelA0801']").text.strip()
                
                # 提取答题链接
                answer_link = row.find_element(By.CSS_SELECTOR, "a[id*='HyperLinkShow']")
                answer_url = answer_link.get_attribute("href")
                
                # 提取要求和说明链接
                requirement_link = row.find_element(By.CSS_SELECTOR, "a[id*='HyperLinkA0801']")
                requirement_url = requirement_link.get_attribute("href")
                
                questions.append({
                    'id': question_id,
                    'name': question_name,
                    'answer_url': answer_url,
                    'requirement_url': requirement_url
                })
                
                print(f"找到题目: {question_id} - {question_name}")
                
            except Exception as e:
                print(f"解析题目时出错: {e}")
                continue
        
        return questions
    
    def download_file(self, url, filename):
        """下载文件"""
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"下载成功: {filename}")
            return True
        except Exception as e:
            print(f"下载失败 {url}: {e}")
            return False
    
    def extract_filename_from_url(self, url):
        """从URL中提取文件名"""
        parsed = urlparse(url)
        return os.path.basename(parsed.path)
    
    def process_question(self, question):
        """处理单个题目"""
        question_id = question['id']
        question_name = question['name']
        
        # 创建题目文件夹
        folder_name = f"{question_id}-{question_name}"
        # 清理文件夹名称中的非法字符
        folder_name = re.sub(r'[<>:"/\\|?*]', '_', folder_name)
        question_folder = os.path.join(self.download_dir, folder_name)
        
        if not os.path.exists(question_folder):
            os.makedirs(question_folder)
        
        print(f"\n处理题目: {folder_name}")
        
        # 下载要求和说明文件
        if question['requirement_url']:
            req_filename = self.extract_filename_from_url(question['requirement_url'])
            req_path = os.path.join(question_folder, req_filename)
            self.download_file(question['requirement_url'], req_path)
        
        # 导航到题目详情页面获取参考文件和参考答案
        try:
            self.driver.get(question['answer_url'])
            time.sleep(2)  # 等待页面加载
            
            # 下载参考文件
            reference_files = self.driver.find_elements(By.CSS_SELECTOR, "#DataListFiles a")
            for i, ref_file in enumerate(reference_files):
                ref_url = ref_file.get_attribute("href")
                if ref_url:
                    ref_filename = self.extract_filename_from_url(ref_url)
                    ref_path = os.path.join(question_folder, f"参考文件_{i+1}_{ref_filename}")
                    self.download_file(ref_url, ref_path)
            
            # 下载参考答案
            answer_files = self.driver.find_elements(By.CSS_SELECTOR, "#DatalistAnswers a")
            for i, ans_file in enumerate(answer_files):
                ans_url = ans_file.get_attribute("href")
                if ans_url:
                    ans_filename = self.extract_filename_from_url(ans_url)
                    ans_path = os.path.join(question_folder, f"参考答案_{i+1}_{ans_filename}")
                    self.download_file(ans_url, ans_path)
                    
        except Exception as e:
            print(f"处理题目详情时出错: {e}")
    
    def run(self):
        """运行主程序"""
        try:
            print("启动世格外贸单证教学系统题目下载器")
            self.setup_driver()
            
            # 手动登录
            self.manual_login()
            
            # 导航到题目列表
            self.navigate_to_question_list()
            
            # 解析题目列表
            questions = self.parse_question_list()
            
            if not questions:
                print("未找到任何题目")
                return
            
            print(f"\n找到 {len(questions)} 个题目，开始下载...")
            
            # 处理每个题目
            for i, question in enumerate(questions, 1):
                print(f"\n进度: {i}/{len(questions)}")
                self.process_question(question)
                
                # 添加延迟避免请求过快
                time.sleep(1)
            
            print(f"\n所有题目处理完成！文件保存在: {self.download_dir}")
            
        except Exception as e:
            print(f"程序运行出错: {e}")
        finally:
            if self.driver:
                input("按回车键关闭浏览器...")
                self.driver.quit()


def get_base_url_from_user():
    """从用户获取base_url配置"""
    while True:
        print("=" * 50)
        print("请配置世格外贸单证教学系统访问地址:")
        print("1. 输入完整的系统访问URL（例如: http://URL/doc）")
        print("2. 确保URL格式正确，包含协议头（http:// 或 https://）")
        print("=" * 50)
        
        base_url = input("请输入系统访问URL: ").strip()
        
        # 验证URL格式
        if not base_url:
            print("错误: URL不能为空，请重新输入。")
            continue
            
        if not base_url.startswith(('http://', 'https://')):
            print("错误: URL必须以 http:// 或 https:// 开头，请重新输入。")
            continue
            
        # 简单的URL格式验证
        try:
            parsed = urlparse(base_url)
            if not parsed.netloc:
                print("错误: URL格式不正确，请重新输入。")
                continue
        except Exception:
            print("错误: URL格式不正确，请重新输入。")
            continue
            
        # 确认用户输入
        print(f"\n您输入的URL是: {base_url}")
        confirm = input("确认使用此URL? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes', '是']:
            return base_url
        else:
            print("重新输入URL...\n")


def get_chromedriver_path_from_user():
    """从用户获取chromedriver路径配置"""
    while True:
        print("=" * 50)
        print("请配置chromedriver.exe的位置:")
        print("1. 输入chromedriver.exe的完整路径（例如: C:/WebDriver/bin/chromedriver.exe）")
        print("2. 如果不输入，将使用默认路径: C:/WebDriver/bin/chromedriver.exe")
        print("=" * 50)
        
        chromedriver_path = input("请输入chromedriver.exe的路径 (直接回车使用默认路径): ").strip()
        
        # 如果用户没有输入路径，使用默认路径
        if not chromedriver_path:
            return None
        
        # 验证路径是否存在且是文件
        if not os.path.exists(chromedriver_path):
            print(f"错误: 路径 '{chromedriver_path}' 不存在，请重新输入。")
            continue
            
        if not os.path.isfile(chromedriver_path):
            print(f"错误: '{chromedriver_path}' 不是一个有效的文件，请重新输入。")
            continue
            
        # 验证文件名是否正确
        if not chromedriver_path.endswith('.exe'):
            print("错误: 文件名必须以 .exe 结尾，请重新输入。")
            continue
            
        # 确认用户输入
        print(f"\n您输入的chromedriver路径是: {chromedriver_path}")
        confirm = input("确认使用此路径? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes', '是']:
            return chromedriver_path
        else:
            print("重新输入chromedriver路径...\n")


def main():
    """主函数"""
    # 获取用户配置的base_url
    base_url = get_base_url_from_user()
    
    # 获取用户配置的chromedriver路径
    chromedriver_path = get_chromedriver_path_from_user()
    
    # 创建爬虫实例并传入配置的base_url和chromedriver路径
    scraper = DesunScraper(base_url=base_url, chromedriver_path=chromedriver_path)
    scraper.run()


if __name__ == "__main__":
    main()