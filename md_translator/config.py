"""
配置管理模块 - 管理 API Key 和用户设置
"""

import os
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


DEFAULT_MODELS = {"openai": "gpt-5.4-mini", "gemini": "gemini-3.1-flash-lite"}


# Verified against https://developers.openai.com/api/docs/models/<model>
# on 2026-09-12. Unknown models keep the API default.
REASONING_EFFORTS = {
    "gpt-6-astra": ("low", "medium", "high", "xhigh", "max"),
    "gpt-5.6": ("none", "low", "medium", "high", "xhigh", "max"),
    "gpt-5.6-sol": ("none", "low", "medium", "high", "xhigh", "max"),
    "gpt-5.6-terra": ("none", "low", "medium", "high", "xhigh", "max"),
    "gpt-5.6-luna": ("none", "low", "medium", "high", "xhigh", "max"),
    "gpt-5.5": ("none", "low", "medium", "high", "xhigh"),
    "gpt-5.4": ("none", "low", "medium", "high", "xhigh"),
    "gpt-5.4-mini": ("none", "low", "medium", "high", "xhigh"),
}


def reasoning_options(model):
    base = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", model)
    return ("default",) + REASONING_EFFORTS.get(base, ())


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
            "target_language": "繁體中文",  # 目标翻译语言
            "openai_model": DEFAULT_MODELS["openai"],
            "gemini_model": DEFAULT_MODELS["gemini"]
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
    
    def get_model(self, provider: str) -> str:
        return self.config.get(f"{provider}_model") or DEFAULT_MODELS[provider]

    def set_model(self, provider: str, model: str):
        if provider not in DEFAULT_MODELS:
            raise ValueError("不支援的提供商")
        model = model.strip()
        if not model or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/-]*", model):
            raise ValueError("請輸入有效的模型 ID（不可包含空白）")
        self.config[f"{provider}_model"] = model
        self._save_config()
        print(f"✅ {provider} 模型已設為：{model}")

    def get_reasoning_effort(self, model=None):
        model = model or self.get_model("openai")
        saved = self.config.get("openai_reasoning_efforts", {}).get(model, "default")
        return saved if saved in reasoning_options(model) else "default"

    def set_reasoning_effort(self, effort):
        model = self.get_model("openai")
        if effort not in reasoning_options(model):
            raise ValueError(f"{model} 不支援此推理程度：{effort}")
        self.config.setdefault("openai_reasoning_efforts", {})[model] = effort
        self._save_config()
        print(f"✅ {model} 推理程度：{effort}")

    def _reasoning_submenu(self):
        model = self.get_model("openai")
        options = reasoning_options(model)
        print(f"\n模型：{model}；目前推理程度：{self.get_reasoning_effort()}")
        print("模型預設不傳入參數；none 表示關閉推理，兩者不同。")
        print("較高推理程度通常會增加等待時間與用量。")
        if len(options) == 1:
            print("此模型尚無已確認的可選推理程度，僅提供模型預設。")
        for index, effort in enumerate(options, 1):
            label = "模型預設（不傳入參數）" if effort == "default" else effort
            print(f"  {index}. {label}")
        choice = input("輸入編號（留空取消）: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            self.set_reasoning_effort(options[int(choice) - 1])
        elif choice:
            print("⚠️ 無效編號，原設定未變更。")

    def list_openai_models(self):
        from openai import OpenAI
        key = self.get_openai_api_key()
        if not key:
            raise ValueError("請先設定 OpenAI API Key")
        with OpenAI(api_key=key, timeout=15, max_retries=0) as client:
            models = list(client.models.list())
        # The API has no endpoint-capability field. These are text candidates,
        # not a guarantee of Chat Completions support for every model.
        excluded = ("audio", "realtime", "live", "image", "transcribe", "tts", "search",
                    "codex", "deep-research", "-pro", "instruct")
        candidates = [m for m in models if re.match(r"^(gpt-|chatgpt-|o[134](?:-|$))", m.id)
                      and not any(part in m.id.lower() for part in excluded)]
        return sorted(candidates, key=lambda m: (-m.created, m.id))

    def _model_submenu(self, provider: str):
        while True:
            print(f"\n目前模型：{self.get_model(provider)}")
            print("  1. 手動輸入模型 ID")
            print("  2. 從 OpenAI 即時清單選擇" if provider == "openai" else "  2. 恢復預設模型")
            print("  3. 返回")
            choice = input("請輸入選擇 [3]: ").strip() or "3"
            if choice == "3":
                return
            if choice == "1":
                model = input("模型 ID（留空取消）: ").strip()
                if model:
                    try:
                        self.set_model(provider, model)
                    except ValueError as error:
                        print(f"⚠️ {error}")
            elif choice == "2" and provider == "gemini":
                self.set_model(provider, DEFAULT_MODELS[provider])
            elif choice == "2":
                try:
                    models = self.list_openai_models()
                except Exception:
                    print("⚠️ 無法取得模型清單，請檢查網路、API Key 與權限；仍可手動輸入。原設定未變更。")
                    continue
                if not models:
                    print("⚠️ 找不到文字模型候選，可改用手動輸入。")
                    continue
                print("依 API 建立時間由新到舊排列，非能力或價格排名。")
                print("請選支援 Chat Completions 文字輸出的模型；清單不保證介面相容性。")
                for index, model in enumerate(models, 1):
                    date = datetime.fromtimestamp(model.created, timezone.utc).date()
                    print(f"  {index}. {model.id}  ({date})")
                selected = input("輸入編號（留空取消）: ").strip()
                if selected.isdigit() and 1 <= int(selected) <= len(models):
                    self.set_model(provider, models[int(selected) - 1].id)
                elif selected:
                    print("⚠️ 無效編號，原設定未變更。")

    def setup_wizard(self):
        """交互式設置向導"""
        print("\n" + "="*50)
        print("🔧 首次使用設置向導")
        print("="*50 + "\n")
        
        # 選擇 API 提供商
        print("選擇 API 提供商:")
        print("1. OpenAI")
        print("2. Gemini")
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
    
    def _provider_submenu(self, provider: str):
        """顯示單一提供商的子選單"""
        is_openai = provider == "openai"
        name = "OpenAI" if is_openai else "Gemini"
        has_key = bool(self.get_openai_api_key() if is_openai else self.get_gemini_api_key())
        is_current = self.get_api_provider() == provider
        key_status = "✅ 已設定" if has_key else "❌ 未設定"
        current_status = "（目前使用中）" if is_current else ""

        while True:
            print(f"\n{'─'*50}")
            print(f"  {name} 設定 {current_status}")
            print(f"{'─'*50}")
            print(f"  1. 輸入 API Key  [{key_status}]")
            print(f"  2. 選擇此提供商")
            print(f"  3. 選擇／指定模型 [{self.get_model(provider)}]")
            print("  4. 返回")
            if is_openai:
                print(f"  5. 推理程度 [{self.get_reasoning_effort()}]")
            sub = input("\n請輸入選擇 [4]: ").strip()

            if sub == "1":
                if has_key:
                    confirm = input(f"\n  目前已有 {name} API Key，是否要更新？(y/N): ").strip().lower()
                    if confirm != "y":
                        print("  ⚠️  已跳過")
                        continue
                if is_openai:
                    print("  取得地址: https://platform.openai.com/api-keys")
                    api_key = input("  請輸入 OpenAI API Key: ").strip()
                    if api_key:
                        self.set_openai_api_key(api_key)
                        has_key = True
                    else:
                        print("  ⚠️  已跳過")
                else:
                    print("  取得地址: https://aistudio.google.com/apikey")
                    api_key = input("  請輸入 Gemini API Key: ").strip()
                    if api_key:
                        self.set_gemini_api_key(api_key)
                        has_key = True
                    else:
                        print("  ⚠️  已跳過")

            elif sub == "2":
                self.set_api_provider(provider)
                is_current = True
                current_status = "（目前使用中）"

            elif sub == "3":
                self._model_submenu(provider)
            elif sub == "5" and is_openai:
                self._reasoning_submenu()
            elif sub in ("4", ""):
                break

    def reconfigure(self):
        """重新配置"""
        while True:
            current = self.get_api_provider()
            openai_mark = " ✅" if current == "openai" else ""
            gemini_mark = " ✅" if current == "gemini" else ""
            print("\n" + "="*50)
            print("⚙️  API 配置")
            print("="*50)
            print("\n  選擇 API 提供商：")
            print(f"  1. OpenAI{openai_mark}")
            print(f"  2. Gemini{gemini_mark}")
            print("  3. 退出設定")
            choice = input("\n請輸入選擇 (1-3) [默認: 3]: ").strip() or "3"

            if choice == "1":
                self._provider_submenu("openai")
            elif choice == "2":
                self._provider_submenu("gemini")
            elif choice == "3":
                print("\n  已退出設定。\n")
                break
    
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
