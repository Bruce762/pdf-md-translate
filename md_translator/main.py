"""
Markdown 論文翻譯工具 - 主要模組
支持 OpenAI GPT 和 Google Gemini 模型
"""

import os
import sys
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from openai import OpenAI
from google import genai
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# 導入配置管理模塊
from .config import config_manager

# --- 動態設定區（從配置讀取）---
def init_api_config():
    """初始化 API 配置"""
    global API_PROVIDER, OPENAI_API_KEY, GOOGLE_API_KEY, openai_client, gemini_client
    
    API_PROVIDER = config_manager.get_api_provider()
    
    # 初始化 OpenAI
    OPENAI_API_KEY = config_manager.get_openai_api_key()
    openai_client = None
    if OPENAI_API_KEY:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    
    # 初始化 Gemini
    GOOGLE_API_KEY = config_manager.get_gemini_api_key()
    gemini_client = None
    if GOOGLE_API_KEY:
        gemini_client = genai.Client(api_key=GOOGLE_API_KEY)

# 默認值（將在 init_api_config() 中設置）
API_PROVIDER = "gemini"
OPENAI_API_KEY = ""
GOOGLE_API_KEY = ""
openai_client = None
gemini_client = None

# 模型配置
OPENAI_MODEL = "gpt-5.4-mini"
GEMINI_MODEL = "gemini-2.5-flash"

# 顏色定義
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

# 自定義異常類
class QuotaExceededException(Exception):
    """API 配額超限異常"""
    def __init__(self, provider, retry_after=None):
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(f"API 配額已超限 ({provider})")

def call_translation_api(text, is_heading=False, target_language="繁體中文"):
    """
    呼叫翻譯 API（支持 OpenAI 和 Google Gemini）
    is_heading: 是否為標題
    target_language: 目標翻譯語言
    """
    system_prompt = (
        "你是一位精通演算法與計算優化的資工專家，專長是學術論文翻譯。\n\n"
        "### 任務規範：\n"
        f"1. 將 Markdown 文字翻譯成專業的{target_language}。\n"
        "2. **嚴格保留 LaTeX 公式**：所有以 `$` 或 `$$` 包圍的內容絕對不准變動，保持原始位置。\n"
        "3. **保留資工術語**：如 Mutation (變異), Crossover (交叉), Population (種群), $F$ (Scaling factor), $CR$ (Crossover rate) 等建議保留原文或標註原文。\n"
        "4. **僅輸出翻譯結果**，不要有任何解釋性文字。\n"
        "5. 可能出現單字也要翻譯"
    )
    
    # 如果是標題，添加第6點
    if is_heading:
        system_prompt += "\n6. 刪除所有標題編號：直接忽略原文開頭的層級數字（如 1.1, 1.2, 2.3.1 等），僅翻譯後續的實質內容文字。"
    
    prompt = (
        "範例輸入：The mutant vector $V_{i,G+1}$ is calculated using the formula $V_{i,G+1} = X_{r1,G} + F \\cdot (X_{r2,G} - X_{r3,G})$.\n"
        "範例輸出：變異向量 $V_{i,G+1}$ 是使用公式 $V_{i,G+1} = X_{r1,G} + F \\cdot (X_{r2,G} - X_{r3,G})$ 計算得出的。\n\n"
        f"現在請翻譯以下段落：\n\n{text}"
    )
    
    try:
        # 確保使用最新的配置
        provider = config_manager.get_api_provider()
        if provider == "openai":
            return _call_openai_api(prompt, system_prompt)
        elif provider == "gemini":
            return _call_gemini_api(prompt, system_prompt)
        else:
            print(f"❌ 未知的 API 提供商: {provider}")
            return None
    except QuotaExceededException:
        # 配額不足異常，向上傳播
        raise
    except Exception as e:
        print(f"\n⚠️ 翻譯出錯：{e}")
        return None


def _call_openai_api(prompt, system_prompt):
    """呼叫 OpenAI API"""
    if not openai_client:
        print("❌ OpenAI 客戶端未初始化，請檢查 OPENAI_API_KEY")
        return None
    
    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # 檢測 429 配額超限錯誤
        if "429" in str(e) or "quota" in str(e).lower() or "rate_limit" in str(e).lower():
            raise QuotaExceededException("OpenAI")
        raise


def _call_gemini_api(prompt, system_prompt):
    """呼叫 Google Gemini API"""
    api_key = config_manager.get_gemini_api_key()
    if not api_key:
        print("❌ Gemini API Key 未設置")
        return None
    
    try:
        # 使用 google-genai 新 API
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.3,
                system_instruction=system_prompt
            )
        )
        return response.text.strip()
    except Exception as e:
        # 檢測 429 配額超限錯誤
        error_str = str(e)
        if "429" in error_str or "quota" in error_str.lower() or "exceeded" in error_str.lower():
            raise QuotaExceededException("Gemini")
        raise

def is_markdown_table(text):
    """
    檢測是否為 Markdown 表格或 HTML 表格
    Markdown 表格特徵：至少有一行包含 | 且下一行是分隔符 (|---|...|)
    HTML 表格特徵：包含 <table> 標籤
    """
    # 檢測 HTML 表格
    if '<table' in text or '</table>' in text:
        return True
    
    lines = text.strip().split('\n')
    if len(lines) < 2:
        return False
    
    # 檢查是否有 Markdown 表格分隔符 (|---|---|...)
    for i, line in enumerate(lines):
        if '|' in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            # 表格分隔符：包含 |、- 和可選的 :
            if re.match(r'^\|[\s\-:|]*\|?[\s\-:|]*$', next_line) and '-' in next_line:
                return True
    return False

def translate_paragraph(p_strip, target_language="繁體中文"):
    """
    翻譯單個段落，返回雙語段落或原文
    target_language: 目標翻譯語言
    """
    # 1. 處理空行
    if not p_strip:
        return None
        
    # 2. 跳過不需翻譯的區塊：公式塊 ($$)、程式碼塊 (```)、表格
    if p_strip.startswith("$$") or p_strip.startswith("```") or is_markdown_table(p_strip):
        return p_strip
    
    # 2.5 檢測是否為標題（以 # 開頭）
    is_heading = p_strip.startswith("#")
    
    # 3. 處理包含圖片的段落：提取說明文字翻譯
    image_pattern = r'!\[.*?\]\(.*?\)'
    has_image = re.search(image_pattern, p_strip)
    
    if has_image:
        # 提取圖片語法
        images = re.findall(image_pattern, p_strip)
        image_str = '\n'.join(images)
        
        # 提取說明文字（移除圖片語法）
        caption = re.sub(image_pattern, '', p_strip).strip()
        
        # 如果沒有說明文字，直接返回圖片
        if not caption:
            return image_str
        
        # 翻譯說明文字
        translated_caption = call_translation_api(caption, is_heading=False, target_language=target_language)
        if not translated_caption:
            return p_strip  # 翻譯失敗則保留原文
        
        # 組合：圖片 + 原始說明 + 翻譯說明
        bilingual = f"{image_str}\n\n{caption}\n\n{translated_caption}"
        return bilingual
    
    # 4. 翻譯普通段落或標題
    else:
        # 如果是標題，提取標題文本（去掉 # 符號）
        if is_heading:
            # 提取 # 和前後空格，保留實際標題文本
            heading_text = p_strip.lstrip("#").strip()
            translated_text = call_translation_api(heading_text, is_heading=True, target_language=target_language)
        else:
            translated_text = call_translation_api(p_strip, is_heading=False, target_language=target_language)
        
        if not translated_text:
            return p_strip  # 翻譯失敗則保留原文
        
        # 根據是否為標題決定連接方式
        if is_heading:
            # 標題：原文 + 空格 + 翻譯（同一行）
            bilingual_paragraph = f"{p_strip} {translated_text}"
        else:
            # 普通段落：原文 -> 中譯段落（要換行）
            bilingual_paragraph = f"{p_strip}\n\n{translated_text}"
        
        return bilingual_paragraph

def translate_markdown(file_path, target_language="繁體中文"):
    output_path = file_path.replace(".md", "_bilingual.md")
    
    if not os.path.exists(file_path):
        print(f"❌ 錯誤：找不到檔案 {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 以雙換行切分段落，這是 Markdown 最常見的結構
    paragraphs = content.split("\n\n")

    # 根據 API 提供商設置不同的線程數
    provider = config_manager.get_api_provider()
    if provider == "gemini":
        num_threads = 1
        thread_desc = f"📊 使用 1 個線程並發翻譯 (Gemini)...\n"
    else:  # openai
        num_threads = 5
        thread_desc = f"📊 使用 5 個線程並發翻譯 (OpenAI)...\n"
    
    print(f"🚀 開始翻譯：{file_path}，總計 {len(paragraphs)} 個段落...")
    print(f"🌐 目標語言：{target_language}")
    print(thread_desc)
    bilingual_content = [None] * len(paragraphs)  # 預先分配列表以保持順序
    quota_exceeded = False
    
    try:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # 提交所有翻譯任務並保存索引
            futures = {executor.submit(translate_paragraph, p.strip(), target_language): idx for idx, p in enumerate(paragraphs)}
            
            # 使用 tqdm 顯示進度
            for future in tqdm(as_completed(futures), total=len(paragraphs), desc="翻譯進度"):
                try:
                    idx = futures[future]
                    result = future.result()
                    if result is not None:  # 過濾空行
                        bilingual_content[idx] = result
                except QuotaExceededException as e:
                    quota_exceeded = True
                    # 停止所有待處理任務
                    executor.shutdown(wait=False)
                    print()  # 新行
                    print(f"\n{Colors.RED}{'='*50}{Colors.NC}")
                    print(f"{Colors.RED}❌ API 配額已超限！{Colors.NC}")
                    print(f"{Colors.RED}{'='*50}{Colors.NC}")
                    print(f"\n{Colors.YELLOW}📊 翻譯統計：{Colors.NC}")
                    translated_count = sum(1 for item in bilingual_content if item is not None)
                    print(f"  - 已成功翻譯: {translated_count}/{len(paragraphs)} 個段落")
                    print(f"  - 未翻譯: {len(paragraphs) - translated_count} 個段落")
                    print(f"\n{Colors.YELLOW}解決方案：{Colors.NC}")
                    print(f"  1. 等待 API 配額重置（通常需要 1-24 小時）")
                    print(f"  2. 升級 API 方案以獲得更高的配額")
                    print(f"  3. 使用其他 API 提供商（如切換到 OpenAI）")
                    print(f"  4. 分割文件成更小的部分，逐次翻譯")
                    print(f"\n{Colors.YELLOW}查看更多信息：{Colors.NC}")
                    print(f"  - Gemini 配額信息: https://ai.google.dev/gemini-api/docs/rate-limits")
                    print(f"  - OpenAI 配額信息: https://platform.openai.com/account/rate-limits")
                    print()
                    raise  # 重新拋出異常以退出
                except Exception as e:
                    # 記錄失敗的段落，但不重新發送
                    idx = futures[future]
                    error_msg = str(e)[:100]  # 只取前 100 字
                    print(f"\n⚠️ 段落 {idx+1} 翻譯失敗: {error_msg}")
                    # 保留原文作為備用（不再嘗試翻譯）
                    if bilingual_content[idx] is None:
                        bilingual_content[idx] = paragraphs[idx].strip()
    except QuotaExceededException:
        return  # 配額超限，退出不保存

    if quota_exceeded:
        return  # 已顯示錯誤信息並退出

    # 移除 None 值（來自空行）
    bilingual_content = [item for item in bilingual_content if item is not None]

    # 寫入新檔案
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(bilingual_content))
    
    print(f"\n✅ 翻譯完成！儲存路徑：{output_path}")

def convert_pdf_with_mineru(pdf_file, output_dir):
    """
    使用 mineru 將 PDF 轉換為 Markdown
    返回生成的 MD 文件路徑
    """
    if not os.path.exists(pdf_file):
        print(f"{Colors.RED}❌ 錯誤：找不到 PDF 文件 '{pdf_file}'{Colors.NC}")
        return None
    
    pdf_basename = Path(pdf_file).stem  # 文件名不含路徑和副檔名
    
    print(f"{Colors.GREEN}========================================{Colors.NC}")
    print(f"{Colors.GREEN}開始處理：{pdf_basename}{Colors.NC}")
    print(f"{Colors.GREEN}輸出目錄：{output_dir}{Colors.NC}")
    print(f"{Colors.GREEN}========================================{Colors.NC}")
    
    # 第 1 步：使用 mineru 轉換 PDF
    print(f"\n{Colors.YELLOW}📄 第 1 步：使用 mineru 轉換 PDF...{Colors.NC}")
    temp_output = tempfile.mkdtemp(prefix="mineru_output_")
    
    try:
        print(f"{Colors.YELLOW}執行命令: mineru -p {pdf_file} -o {temp_output}{Colors.NC}\n")
        result = subprocess.run(
            ["mineru", "-p", pdf_file, "-o", temp_output],
            text=True
        )
        
        if result.returncode != 0:
            print(f"{Colors.RED}❌ mineru 轉換失敗{Colors.NC}")
            shutil.rmtree(temp_output, ignore_errors=True)
            return None
        
        # 第 2 步：查找生成的 MD 文件
        print(f"{Colors.YELLOW}🔍 查找轉換後的 MD 文件...{Colors.NC}")
        
        # 預期路徑：output/{PDF_NAME}/{pdf_basename}/hybrid_auto/{PDF_NAME}.md
        expected_path = os.path.join(temp_output, pdf_basename, "hybrid_auto", f"{pdf_basename}.md")
        
        md_file = None
        md_dir = None  # MD 文件所在的目錄（可能包含圖片）
        if os.path.exists(expected_path):
            md_file = expected_path
            md_dir = os.path.dirname(md_file)  # 獲取 MD 文件所在的目錄
        else:
            # 如果預期路徑不存在，查找任何 .md 文件
            for root, dirs, files in os.walk(temp_output):
                for file in files:
                    if file.endswith(".md"):
                        md_file = os.path.join(root, file)
                        md_dir = root  # 獲取 MD 文件所在的目錄
                        break
                if md_file:
                    break
        
        if not md_file:
            print(f"{Colors.RED}❌ 錯誤：找不到生成的 MD 文件{Colors.NC}")
            print(f"{Colors.RED}預期路徑：{expected_path}{Colors.NC}")
            shutil.rmtree(temp_output, ignore_errors=True)
            return None
        
        print(f"{Colors.GREEN}✅ 找到 MD 文件：{md_file}{Colors.NC}")
        
        # 第 3 步：複製 MD 文件到工作目錄
        print(f"{Colors.YELLOW}📋 複製 MD 文件到輸出目錄...{Colors.NC}")
        os.makedirs(output_dir, exist_ok=True)
        work_md = os.path.join(output_dir, f"{pdf_basename}.md")
        shutil.copy2(md_file, work_md)
        
        print(f"{Colors.GREEN}✅ MD 文件已保存：{work_md}{Colors.NC}")
        
        # 第 3.5 步：保留圖片文件夾（統一放在 images/{pdf_basename}/ 下）
        print(f"{Colors.YELLOW}📁 保存圖片文件夾...{Colors.NC}")
        source_image_folder = None  # 記錄原始圖片文件夾名
        if md_dir:
            # 查找所有圖片相關的文件夾（通常名為 'images' 或含有圖片的子目錄）
            for item in os.listdir(md_dir):
                item_path = os.path.join(md_dir, item)
                if os.path.isdir(item_path) and item.lower() in ['images', 'figures', 'pics', 'pictures']:
                    source_image_folder = item.lower()
                    # 統一保存到 images/{pdf_basename}/ 下
                    images_base_dir = os.path.join(output_dir, "images")
                    dest_dir = os.path.join(images_base_dir, pdf_basename)
                    os.makedirs(images_base_dir, exist_ok=True)
                    if os.path.exists(dest_dir):
                        shutil.rmtree(dest_dir)
                    shutil.copytree(item_path, dest_dir)
                    print(f"{Colors.GREEN}✅ 圖片文件夾已保存：{dest_dir}{Colors.NC}")
                    break  # 找到第一個圖片文件夾就停止
                elif os.path.isdir(item_path):
                    # 檢查是否有圖片文件的目錄
                    has_images = False
                    for root, dirs, files in os.walk(item_path):
                        for file in files:
                            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                                has_images = True
                                break
                        if has_images:
                            break
                    
                    if has_images:
                        source_image_folder = item
                        # 統一保存到 images/{pdf_basename}/ 下
                        images_base_dir = os.path.join(output_dir, "images")
                        dest_dir = os.path.join(images_base_dir, pdf_basename)
                        os.makedirs(images_base_dir, exist_ok=True)
                        if os.path.exists(dest_dir):
                            shutil.rmtree(dest_dir)
                        shutil.copytree(item_path, dest_dir)
                        print(f"{Colors.GREEN}✅ 圖片文件夾已保存：{dest_dir}{Colors.NC}")
                        break  # 找到第一個圖片文件夾就停止
        
        # 第 3.6 步：更新 MD 文件中的圖片路徑引用
        if os.path.exists(work_md):
            print(f"{Colors.YELLOW}📝 更新圖片路徑參考...{Colors.NC}")
            with open(work_md, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 將所有圖片路徑統一為 images/{pdf_basename}/filename 格式
            # 處理格式：![alt](images/xxx.jpg), ![alt](./images/xxx.jpg), ![alt](images/subdir/xxx.jpg) 等
            
            # 先找出所有圖片引用
            pattern = r'!\[([^\]]*)\]\s*\(\s*([^)]*?\.(?:png|jpg|jpeg|gif|webp|svg))\s*\)'
            
            def replace_image_path(match):
                import urllib.parse
                alt_text = match.group(1)
                img_path = match.group(2).strip()
                
                # 從路徑中提取檔案名
                filename = os.path.basename(img_path)
                
                # 返回新的路徑格式：images/{pdf_basename}/filename
                # 對空格進行 URL 編碼（%20）以支持各種 markdown 渲染器
                new_path = f'images/{pdf_basename}/{filename}'
                new_path = urllib.parse.quote(new_path, safe='/')  # safe='/' 保持斜杠不編碼
                
                return f'![{alt_text}]({new_path})'
            
            updated_content = re.sub(pattern, replace_image_path, content, flags=re.IGNORECASE)
            
            if updated_content != content:
                with open(work_md, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"{Colors.GREEN}✅ 圖片路徑已更新{Colors.NC}")
            else:
                print(f"{Colors.YELLOW}⚠️ 沒有找到需要更新的圖片路徑{Colors.NC}")
        
        return work_md
        
    finally:
        # 清理臨時文件
        print(f"{Colors.YELLOW}🧹 清理臨時文件...{Colors.NC}")
        shutil.rmtree(temp_output, ignore_errors=True)

def print_usage():
    """打印使用說明"""
    print(f"{Colors.YELLOW}使用方式：{Colors.NC}\n")
    print(f"{Colors.GREEN}翻譯 PDF 文件（PDF → Markdown → 翻譯）：{Colors.NC}")
    print("  md-translate paper.pdf                # 輸出到當前目錄，使用默認語言")
    print("  md-translate paper.pdf ./output       # 輸出到 ./output")
    print("  md-translate paper.pdf --lang         # 進入交互式語言選擇")
    print("  md-translate paper.pdf --lang 简体中文 # 指定目標語言")
    print()
    print(f"{Colors.GREEN}翻譯 Markdown 文件（直接翻譯）：{Colors.NC}")
    print("  md-translate paper.md                 # 使用默認語言翻譯")
    print("  md-translate paper.md output.md       # 指定輸出文件，使用默認語言")
    print("  md-translate paper.md --lang          # 進入交互式語言選擇")
    print("  md-translate paper.md --lang 日本語   # 指定目標語言")
    print()
    print(f"{Colors.GREEN}語言設置和幫助：{Colors.NC}")
    print("  md-translate --lang                   # 進入語言選擇（保存到配置）")
    print("  md-translate --setup                  # 設置或修改 API Key")
    print("  md-translate --config                 # 查看配置文件位置")
    print("  md-translate --help                   # 顯示此幫助信息")
    print()
    print(f"{Colors.YELLOW}示例：{Colors.NC}")
    print("  # 翻譯成默認語言（繁體中文）")
    print("  md-translate paper.md")
    print("  # 進入交互式語言選擇")
    print("  md-translate paper.md --lang")
    print("  # 翻譯成簡體中文")
    print("  md-translate paper.md --lang 简体中文")
    print("  # 翻譯成日語")
    print("  md-translate paper.pdf --lang 日本語")
    print()
    print(f"{Colors.YELLOW}功能說明：{Colors.NC}")
    print("  • 自動檢測文件類型（PDF 或 Markdown）")
    print("  • 支持多種語言翻譯，交互式語言選擇")
    print("  • 保留 LaTeX 公式、代碼塊、表格")
    print("  • 生成雙語文件（英文 + 目標語言）")
    print("  • 智能配額管理，配額不足時自動停止")

def interactive_language_select():
    """交互式語言選擇"""
    print(f"\n{Colors.YELLOW}🌐 語言選擇{Colors.NC}")
    print("="*50)
    print("\n常用語言：")
    print("1. 繁體中文")
    print("2. 简体中文")
    print("3. 日本語")
    print("4. English")
    print("5. Español")
    print("6. Français")
    print("7. Deutsch")
    print("8. 한국어")
    print("0. 自定義語言")
    print()
    
    choice = input("請選擇語言 (0-8) [默認: 1]: ").strip() or "1"
    
    language_map = {
        "1": "繁體中文",
        "2": "简体中文",
        "3": "日本語",
        "4": "English",
        "5": "Español",
        "6": "Français",
        "7": "Deutsch",
        "8": "한국어"
    }
    
    if choice in language_map:
        target_language = language_map[choice]
    elif choice == "0":
        target_language = input("請輸入自定義語言: ").strip()
        if not target_language:
            target_language = "繁體中文"
    else:
        target_language = "繁體中文"
    
    print(f"\n✅ 確認：將翻譯成 {Colors.GREEN}{target_language}{Colors.NC}\n")
    return target_language

def main():
    """程式進入點 - 支持 PDF 和 Markdown 文件"""
    # 檢查命令行參數
    if len(sys.argv) < 2:
        print_usage()
        return
    
    # 處理特殊命令
    if sys.argv[1] in ["--setup", "-s"]:
        config_manager.reconfigure()
        return
    elif sys.argv[1] in ["--config", "-c"]:
        config_manager.show_config_file_location()
        return
    elif sys.argv[1] in ["--help", "-h"]:
        print_usage()
        return
    elif sys.argv[1] in ["--lang", "-l"]:
        # 只輸入 --lang，進入交互式模式
        target_language = interactive_language_select()
        config_manager.set_target_language(target_language)
        return
    
    # 初始化 API 配置
    config_manager.check_and_setup()
    init_api_config()
    
    current_provider = config_manager.get_api_provider()
    # 显示当前使用的模型
    if current_provider == "gemini":
        model_name = GEMINI_MODEL
        model_display = f"🤖 Gemini ({model_name})"
    else:  # openai
        model_name = OPENAI_MODEL
        model_display = f"🤖 OpenAI ({model_name})"
    
    print(f"使用的模型：{model_display}\n")
    
    # 獲取文件路徑
    input_file = sys.argv[1]
    
    # 解析 --lang 參數
    target_language = config_manager.get_target_language()  # 默認值
    if "--lang" in sys.argv:
        lang_idx = sys.argv.index("--lang")
        if lang_idx + 1 < len(sys.argv) and not sys.argv[lang_idx + 1].startswith("-"):
            target_language = sys.argv[lang_idx + 1]
        else:
            # --lang 沒有跟參數，進入交互式模式
            target_language = interactive_language_select()
    
    # 檢查文件是否存在
    if not os.path.exists(input_file):
        print(f"{Colors.RED}❌ 錯誤：找不到檔案 {input_file}{Colors.NC}")
        return
    
    # 根據文件擴展名判斷文件類型
    if input_file.lower().endswith('.pdf'):
        # PDF 文件：使用 mineru 轉換後翻譯
        _handle_pdf_translation(input_file, target_language)
    elif input_file.lower().endswith('.md'):
        # Markdown 文件：直接翻譯
        _handle_markdown_translation(input_file, target_language)
    else:
        print(f"{Colors.RED}❌ 錯誤：不支持的文件格式{Colors.NC}")
        print(f"支持的格式: .pdf, .md")
        return


def _handle_pdf_translation(pdf_file, target_language="繁體中文"):
    """處理 PDF 翻譯"""
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "."
    
    # 第 1 步：使用 mineru 轉換 PDF
    md_file = convert_pdf_with_mineru(pdf_file, output_dir)
    
    if md_file:
        # 第 2 步：翻譯 MD 文件
        print(f"\n{Colors.YELLOW}🌐 第 2 步：開始翻譯...{Colors.NC}")
        translate_markdown(md_file, target_language)
        
        # 第 3 步：重命名雙語文件為最終輸出
        bilingual_file = md_file.replace(".md", "_bilingual.md")
        if os.path.exists(bilingual_file):
            os.remove(md_file)
            os.rename(bilingual_file, md_file)
        
        # 完成
        print(f"\n{Colors.GREEN}========================================{Colors.NC}")
        print(f"{Colors.GREEN}✅ 完成！{Colors.NC}")
        print(f"{Colors.GREEN}========================================{Colors.NC}")
        print(f"輸出文件: {Colors.GREEN}{md_file}{Colors.NC}")
        print()


def _handle_markdown_translation(md_file, target_language="繁體中文"):
    """處理 Markdown 直接翻譯"""
    # 獲取輸出文件（如果指定）
    output_file = None
    if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        output_file = sys.argv[2]
    
    print(f"{Colors.GREEN}========================================{Colors.NC}")
    print(f"{Colors.GREEN}Markdown 翻譯工具{Colors.NC}")
    print(f"{Colors.GREEN}輸入文件：{md_file}{Colors.NC}")
    print(f"{Colors.GREEN}目標語言：{target_language}{Colors.NC}")
    print(f"{Colors.GREEN}========================================{Colors.NC}\n")
    
    # 翻譯 MD 文件
    print(f"{Colors.YELLOW}🌐 開始翻譯...{Colors.NC}")
    translate_markdown(md_file, target_language)
    
    # 輸出文件處理
    bilingual_file = md_file.replace(".md", "_bilingual.md")
    
    if output_file:
        # 使用指定的輸出文件名
        if os.path.exists(bilingual_file):
            os.rename(bilingual_file, output_file)
        print(f"\n{Colors.GREEN}========================================{Colors.NC}")
        print(f"{Colors.GREEN}✅ 翻譯完成！{Colors.NC}")
        print(f"{Colors.GREEN}========================================{Colors.NC}")
        print(f"輸出文件: {Colors.GREEN}{output_file}{Colors.NC}\n")
    else:
        # 默認輸出文件名：filename_translated.md
        if os.path.exists(bilingual_file):
            final_output = md_file.replace(".md", "_translated.md")
            os.rename(bilingual_file, final_output)
            print(f"\n{Colors.GREEN}========================================{Colors.NC}")
            print(f"{Colors.GREEN}✅ 翻譯完成！{Colors.NC}")
            print(f"{Colors.GREEN}========================================{Colors.NC}")
            print(f"輸出文件: {Colors.GREEN}{final_output}{Colors.NC}\n")

def print_translate_file_usage():
    """打印 MD 翻譯用法"""
    print(f"{Colors.YELLOW}Markdown 翻譯工具 - 只翻譯 MD 文件{Colors.NC}\n")
    print("用法：")
    print("  md-translate-file <markdown_file>              # 翻譯 MD 文件")
    print("  md-translate-file <markdown_file> <output_file> # 指定輸出文件")
    print("  md-translate-file --setup                      # 設置或修改 API Key")
    print("  md-translate-file --config                     # 查看配置文件位置")
    print("\n示例：")
    print("  md-translate-file paper.md                   # 生成 paper_translated.md")
    print("  md-translate-file paper.md output.md         # 指定輸出文件")
    print("\n說明：")
    print("  - 直接翻譯 Markdown 文件（無需 PDF 轉換）")
    print("  - 保留 LaTeX 公式、代碼塊、表格")
    print("  - 生成雙語文件（英文 + 繁體中文）")

def main_translate_file():
    """
    只翻譯 MD 文件的進入點（向後兼容）
    
    此函數為了向后兼容而保留，直接调用 main() 函数
    新用户应该使用 md-translate 命令并自动检测文件类型
    """
    # 直接调用 main() 函数，新的 main() 已支持 MD 文件
    main()

if __name__ == "__main__":
    main()
