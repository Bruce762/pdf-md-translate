"""
配置管理模块 - 管理 API Key 和用户设置
"""

import os
import json
from pathlib import Path
from typing import Optional


class ConfigManager:
    """管理程序配置"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "markdown-translator"
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  配置文件读取失败: {e}，使用默认设置")
                return self._default_config()
        return self._default_config()
    
    def _default_config(self) -> dict:
        """默认配置"""
        return {
            "api_provider": "openai",  # 'gemini' 或 'openai'
            "gemini_api_key": "",
            "openai_api_key": "",
            "target_language": "繁體中文"  # 目标翻译语言
        }
    
    def _save_config(self):
        """保存配置到文件"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        # 设置权限为 600 (只有所有者可读写)
        os.chmod(self.config_file, 0o600)
    
    def get_api_provider(self) -> str:
        """获取当前 API 提供商"""
        return self.config.get("api_provider", "gemini")
    
    def set_api_provider(self, provider: str):
        """设置 API 提供商"""
        if provider not in ["gemini", "openai"]:
            raise ValueError("API 提供商必须是 'gemini' 或 'openai'")
        self.config["api_provider"] = provider
        self._save_config()
        print(f"✅ API 提供商已设置为: {provider}")
    
    def get_gemini_api_key(self) -> str:
        """获取 Gemini API Key"""
        # 优先从环境变量读取
        env_key = os.getenv("GOOGLE_API_KEY", "")
        if env_key:
            return env_key
        return self.config.get("gemini_api_key", "")
    
    def set_gemini_api_key(self, api_key: str):
        """设置 Gemini API Key"""
        self.config["gemini_api_key"] = api_key
        self._save_config()
        print("✅ Gemini API Key 已保存")
    
    def get_openai_api_key(self) -> str:
        """获取 OpenAI API Key"""
        # 优先从环境变量读取
        env_key = os.getenv("OPENAI_API_KEY", "")
        if env_key:
            return env_key
        return self.config.get("openai_api_key", "")
    
    def set_openai_api_key(self, api_key: str):
        """设置 OpenAI API Key"""
        self.config["openai_api_key"] = api_key
        self._save_config()
        print("✅ OpenAI API Key 已保存")
    
    def setup_wizard(self):
        """交互式設置向導"""
        print("\n" + "="*50)
        print("🔧 首次使用設置向導")
        print("="*50 + "\n")
        
        # 選擇 API 提供商
        print("選擇 API 提供商:")
        print("1. OpenAI (推薦)")
        print("2. Gemini (較慢)")
        choice = input("請輸入選擇 (1 或 2) [默認: 1]: ").strip() or "1"
        
        if choice == "1":
            self.set_api_provider("openai")
            print("\n請輸入你的 OpenAI API Key (https://platform.openai.com/api-keys):")
            api_key = input("OpenAI API Key: ").strip()
            if api_key:
                self.set_openai_api_key(api_key)
            else:
                print("⚠️  跳過 OpenAI API Key 設置")
        else:
            self.set_api_provider("gemini")
            print("\n請輸入你的 Google Gemini API Key (https://aistudio.google.com/apikey):")
            api_key = input("Gemini API Key: ").strip()
            if api_key:
                self.set_gemini_api_key(api_key)
            else:
                print("⚠️  跳過 Gemini API Key 設置")
        
        print("\n✅ 設置完成！\n")
    
    def check_and_setup(self):
        """检查配置，如果缺失则进行设置"""
        provider = self.get_api_provider()
        
        if provider == "gemini":
            if not self.get_gemini_api_key():
                print("❌ 未找到 Gemini API Key")
                self.setup_wizard()
        elif provider == "openai":
            if not self.get_openai_api_key():
                print("❌ 未找到 OpenAI API Key")
                self.setup_wizard()
    
    def reconfigure(self):
        """重新配置 - 簡化為兩步"""
        print("\n" + "="*50)
        print("⚙️ API 配置")
        print("="*50 + "\n")
        
        # 第一步：選擇 API 提供商
        print("選擇 API 提供商：")
        print("1. OpenAI (推薦)")
        print("2. Gemini (較慢)")
        provider_choice = input("\n請輸入選擇 (1 或 2) [默認: 1]: ").strip() or "1"
        
        # 第二步：輸入 API Key
        if provider_choice == "1":
            self.set_api_provider("openai")
            print("\n🔑 OpenAI API Key 設置")
            print("取得地址: https://platform.openai.com/api-keys")
            api_key = input("\n請輸入 OpenAI API Key: ").strip()
            if api_key:
                self.set_openai_api_key(api_key)
                print("✅ 配置完成！")
            else:
                print("⚠️  已跳過")
        else:
            self.set_api_provider("gemini")
            print("\n🔑 Gemini API Key 設置")
            print("取得地址: https://aistudio.google.com/apikey")
            api_key = input("\n請輸入 Gemini API Key: ").strip()
            if api_key:
                self.set_gemini_api_key(api_key)
                print("✅ 配置完成！")
            else:
                print("⚠️  已跳過")
        
        print()
    
    def show_config_file_location(self):
        """显示配置文件位置"""
        print(f"配置文件位置: {self.config_file}")
    
    def get_target_language(self) -> str:
        """获取目标翻译语言"""
        return self.config.get("target_language", "繁體中文")
    
    def set_target_language(self, language: str):
        """設置目標翻譯語言"""
        self.config["target_language"] = language
        self._save_config()
        print(f"✅ 目標語言已設置為: {language}")


# 全局配置管理器实例
config_manager = ConfigManager()
