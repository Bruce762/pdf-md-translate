# pdf-md-translate

一個強大的文檔轉換和翻譯工具，可以：

1. **將 PDF 轉換為 Markdown 文件** - 自動提取 PDF 中的文本和結構，轉換為易於編輯的 Markdown 格式
2. **將文件中的原文翻譯成多種語言** - 使用 LLM（大型語言模型）自動翻譯 PDF 與 Markdown 論文
3. **將 Markdown 轉換為 PDF** - 支持自定義樣式的 PDF 生成，完成 PDF → MD → PDF 的完整轉換流程

支持 OpenAI GPT 和 Google Gemini 模型進行高質量的學術論文翻譯。

## 功能特性

- 🤖 **多模型支持**：支持 OpenAI GPT 和 Google Gemini
- 📄 **多格式支持**：支持 PDF 和 Markdown 文件翻譯
- 🧮 **公式保護**：自動保留 LaTeX 數學公式，不進行翻譯
- 🌍 **多語言翻譯**：支持自定義目標翻譯語言
- ⚡ **並發處理**：使用多執行緒加速翻譯效能
- ⚙️ **靈活配置**：交互式配置管理，安全存儲 API Key

## 安裝

### 前置要求

- Python >= 3.8
- 有效的 OpenAI API Key 或 Google Gemini API Key
- **Google Chrome 或 Chromium**（用於 PDF 生成）

#### 安裝 Chrome / Chromium

**macOS**：

```bash
brew install --cask google-chrome
```

**Linux (Ubuntu/Debian)**：

```bash
sudo apt-get install google-chrome-stable
```

或

```bash
sudo apt-get install chromium-browser
```

**Windows**：

- 下載並安裝 [Google Chrome](https://www.google.com/chrome/)
- 或使用 Chocolatey：`choco install googlechrome`

### 安裝套件

```bash
pip install pdf-md-translate
```

或從源代碼安裝：

```bash
pip install -e .
```

## 快速開始

> ✅ **注意**：本工具支持兩個命令名稱，使用以下任一命令都可以：
>
> - `pdf-md-translate` - 套件名（推薦使用）
> - `md-translate` - 別名（向後兼容）

### 1. 初始配置

首次使用時，進行配置設置（輸入 API Key 和選擇偏好的 LLM 模型）：

```bash
md-translate --setup
```

或使用簡短命令：

```bash
md-translate -s
```

此命令會引導您：

- 選擇 API 提供商（OpenAI 或 Google Gemini，**默認為 OpenAI**）
- 輸入對應的 API Key
- 設定預設翻譯語言

#### API 提供商選擇指南

| 提供商            | 模型               | 優點            | 缺點        | 適合           |
| ----------------- | ------------------ | --------------- | ----------- | -------------- |
| **OpenAI** ⭐     | `gpt-5.4-mini`     | 🥇 翻譯質量最好 | 💰 需要付費 | 論文、專業文檔 |
| **Google Gemini** | `gemini-2.5-flash` | 🆓 免費額度充足 | ⚠️ 速度較慢 | 測試、批量翻譯 |

> ⭐ **默認選項**：系統默認使用 OpenAI  
> 💡 **提示**：如果沒有 OpenAI 額度，可以在配置時選擇切換到免費的 Gemini

### 2. 翻譯文件

#### 翻譯 Markdown 文件

```bash
md-translate your_file.md
```

#### 翻譯 PDF 文件

預設會翻成繁體中文

```bash
md-translate your_file.pdf
```

#### 指定翻譯語言

```bash
md-translate your_file.md --lang 繁體中文
```

或使用簡短命令：

```bash
md-translate your_file.md -l 簡體中文
```

**支持的語言示例**：

- 繁體中文
- 簡體中文
- English
- 日本語
- 한국어

> ℹ️ **提示**：如果沒有指定 `--lang` 參數，預設會翻譯成 **繁體中文**

### 3. 配置管理

#### 查看配置文件位置

```bash
md-translate --config
```

或：

```bash
md-translate -c
```

配置文件位置：`~/.config/markdown-translator/config.json`

#### 重新配置 API 和語言

```bash
md-translate --setup
```

#### 交互式語言選擇

```bash
md-translate --lang
```

此命令會進入交互式模式，讓您選擇翻譯語言。

## 命令行參考

> 💡 下表中所有 `md-translate` 命令均可替換為 `pdf-md-translate`（例如：`pdf-md-translate your_file.md`）

### 主要命令

| 命令                                    | 別名 | 用途                            |
| --------------------------------------- | ---- | ------------------------------- |
| `md-translate <file>`                   | -    | 翻譯指定的 PDF 或 Markdown 文件 |
| `md-translate <file> --lang <language>` | `-l` | 翻譯文件並指定目標語言          |
| `md-translate --setup`                  | `-s` | 進行初始設置和配置              |
| `md-translate --config`                 | `-c` | 顯示配置文件位置                |
| `md-translate --lang`                   | -    | 進入交互式語言選擇模式          |
| `md-translate --help`                   | `-h` | 顯示幫助信息                    |

### 高級參數

| 參數                          | 簡寫 | 說明                             | 示例                                    |
| ----------------------------- | ---- | -------------------------------- | --------------------------------------- |
| `-m` / `--md-only`            | -    | 只輸出 Markdown，不轉換為 PDF    | `md-translate file.pdf -m`              |
| `--no-translate`              | -    | 跳過翻譯，只進行轉換             | `md-translate file.pdf --no-translate`  |
| `--lang LANG`                 | `-l` | 指定目標翻譯語言                 | `md-translate file.md --lang 日本語`    |
| `--css FILE` / `--style FILE` | -    | 指定自定義 CSS 文件用於 PDF 樣式 | `md-translate file.md --css custom.css` |

> 💡 **提示**：
>
> - `-l` 是 `--lang` 的簡寫，使用方式相同
> - `--css` 和 `--style` 是同義詞，功能完全相同

### 參數特點

- ✅ **參數順序任意**：所有參數可以任意排列組合
- ✅ **參數組合**：支持任意搭配多個參數
- ✅ **向後兼容**：新參數不影響現有命令

## 使用範例

### 基礎用法

#### 範例 1：翻譯英文 Markdown 論文為繁體中文

```bash
md-translate paper.md --lang 繁體中文
```

輸出文件：`paper_trans.pdf`

> 說明：Markdown 翻譯後轉換為 PDF。只輸出最終 PDF 文件。

#### 範例 2：翻譯 PDF 論文

```bash
md-translate research_paper.pdf
```

輸出文件：`research_paper_trans.pdf`

> 說明：PDF 轉為 Markdown → 翻譯 → 轉換為 PDF。只輸出最終 PDF 文件。

#### 範例 3：使用 OpenAI 而不是 Gemini

首先重新配置：

```bash
md-translate --setup
```

選擇 `openai` 作為 API 提供商，然後：

```bash
md-translate document.md
```

### 高級用法

#### 範例 4：只輸出 Markdown，不轉 PDF

```bash
md-translate paper.pdf -m
```

輸出文件：只有 `paper_trans.md`（不會生成 PDF）

> 說明：此時只輸出翻譯後的 Markdown 文件。

#### 範例 5：無翻譯的格式轉換

```bash
md-translate paper.pdf --no-translate
```

輸出文件：`paper_trans.pdf`（PDF 格式，未翻譯）

#### 範例 6：指定語言，只輸出 Markdown

```bash
md-translate document.pdf -m --lang 簡體中文
```

輸出文件：`document_trans.md`（簡體中文版本）

#### 範例 7：使用自定義 CSS 樣式

```bash
md-translate paper.md --css my_style.css
```

輸出文件：`paper_trans.pdf`（使用自定義 CSS 樣式生成的 PDF）

> 說明：指定 CSS 樣式後，系統會自動應用到 PDF 中。中間的 MD 文件會被刪除，只保留最終 PDF。

#### 範例 8：綜合示例（多參數組合）

```bash
# PDF → MD 翻譯 → 自定義樣式 PDF
md-translate thesis.pdf --css dark-theme.css --lang 繁體中文

# PDF → MD（只輸出 MD，無翻譯）
md-translate thesis.pdf -m --no-translate

# Markdown 翻譯成日文（無 PDF）
md-translate article.md -m --lang 日本語

# 參數順序可任意
md-translate file.pdf --lang 簡體中文 --css custom.css -m
md-translate file.pdf -m --css custom.css --lang 簡體中文  # 同一效果
```

## 參數組合矩陣

### PDF 文件操作

| 命令                                      | 輸入 | 操作                       | 輸出             |
| ----------------------------------------- | ---- | -------------------------- | ---------------- |
| `md-translate file.pdf`                   | PDF  | PDF→MD→翻譯→PDF            | `file_trans.pdf` |
| `md-translate file.pdf -m`                | PDF  | PDF→MD→翻譯                | `file_trans.md`  |
| `md-translate file.pdf --no-translate`    | PDF  | PDF→MD→PDF                 | `file_trans.pdf` |
| `md-translate file.pdf -m --no-translate` | PDF  | PDF→MD                     | `file_trans.md`  |
| `md-translate file.pdf --css custom.css`  | PDF  | PDF→MD→翻譯→PDF(自定義CSS) | `file_trans.pdf` |

### Markdown 文件操作

| 命令                                     | 輸入 | 操作                | 輸出             |
| ---------------------------------------- | ---- | ------------------- | ---------------- |
| `md-translate file.md`                   | MD   | 翻譯→PDF            | `file_trans.pdf` |
| `md-translate file.md -m`                | MD   | 翻譯                | `file_trans.md`  |
| `md-translate file.md --no-translate`    | MD   | →PDF                | `file_trans.pdf` |
| `md-translate file.md -m --no-translate` | MD   | 無操作              | 無               |
| `md-translate file.md --css custom.css`  | MD   | 翻譯→PDF(自定義CSS) | `file_trans.pdf` |

## 文件輸出說明

### 文件命名規則

所有輸出文件統一使用 `_trans` 後綴：

- **翻譯 Markdown**：`file.md` → `file_trans.md`
- **轉換 PDF**：`file.md` → `file_trans.pdf`
- **PDF 轉 Markdown**：`file.pdf` → `file_trans.md`

### 文件保留和刪除規則

| 輸入     | 參數             | 輸出類型 | 最終保留文件                  | 刪除文件     |
| -------- | ---------------- | -------- | ----------------------------- | ------------ |
| PDF      | 默認             | PDF      | 原始 PDF<br/>`file_trans.pdf` | 中間 MD 文件 |
| PDF      | `-m`             | MD       | 原始 PDF<br/>`file_trans.md`  | -            |
| PDF      | `--no-translate` | PDF      | 原始 PDF<br/>`file_trans.pdf` | 中間 MD 文件 |
| Markdown | 默認             | PDF      | 原始 MD<br/>`file_trans.pdf`  | 中間 MD 文件 |
| Markdown | `-m`             | MD       | 原始 MD<br/>`file_trans.md`   | -            |
| Markdown | `--no-translate` | PDF      | 原始 MD<br/>`file_trans.pdf`  | -            |

### 重要提示

✅ **所有原始輸入文件（PDF 或 MD）都會被保留**  
❌ **中間的轉換文件會被刪除（如果最終輸出是 PDF）**  
❌ **臨時文件（HTML、臨時 CSS 等）總是會被刪除**

### 範例說明

#### 範例 A：PDF → PDF 轉換

```bash
# 輸入: thesis.pdf
md-translate thesis.pdf

# 生成流程:
# 1. thesis.pdf → thesis.md（中間文件，隨後刪除）
# 2. thesis.md → thesis_trans.md（翻譯）
# 3. thesis_trans.md → thesis_trans.pdf（最終輸出）

# 最終保留: thesis.pdf（原始）、thesis_trans.pdf（輸出）
# 最終刪除: thesis.md、thesis_trans.md（中間文件）
```

#### 範例 B：MD → PDF 轉換

```bash
# 輸入: paper.md
md-translate paper.md

# 生成流程:
# 1. paper.md → paper_trans.md（翻譯）
# 2. paper_trans.md → paper_trans.pdf（最終輸出）

# 最終保留: paper.md（原始）、paper_trans.pdf（輸出）
# 最終刪除: paper_trans.md（中間文件）
```

#### 範例 C：PDF → MD 轉換（使用 -m）

```bash
# 輸入: thesis.pdf
md-translate thesis.pdf -m

# 生成流程:
# 1. thesis.pdf → thesis.md（中間文件）
# 2. thesis.md → thesis_trans.md（翻譯）

# 最終保留: thesis.pdf（原始）、thesis_trans.md（輸出）
# 最終刪除: thesis.md（中間未翻譯文件）
```

## 自定義 CSS 樣式

### 使用自定義 CSS

```bash
md-translate file.pdf --css my_style.css
```

或

```bash
md-translate file.md --style my_style.css
```

### CSS 特性

- ✅ **自動顏色檢測**：自動從 CSS 中提取背景顏色
- ✅ **列印最佳化**：自動添加打印樣式確保 PDF 效果
- ✅ **CSS 變量支持**：支持 `--bg-color` 等 CSS 變量
- ✅ **無修改原文件**：自定義 CSS 文件不會被修改

### CSS 文件示例

```css
:root {
  --bg-color: #f3f2ee;
  --text-color: #333;
  --font-family: "Microsoft YaHei", "SimHei", sans-serif;
}

body {
  background-color: var(--bg-color);
  color: var(--text-color);
  font-family: var(--font-family);
  line-height: 1.6;
}

h1,
h2,
h3 {
  color: #2c3e50;
  margin-top: 24px;
  margin-bottom: 12px;
}

code {
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
}
```

## 翻譯特性

### LaTeX 公式保護

所有 LaTeX 數學公式都會被自動保護，不進行翻譯。例如：

**原文：**

```
The mutant vector $V_{i,G+1}$ is calculated using the formula $V_{i,G+1} = X_{r1,G} + F \cdot (X_{r2,G} - X_{r3,G})$.
```

**翻譯結果：**

```
變異向量 $V_{i,G+1}$ 是使用公式 $V_{i,G+1} = X_{r1,G} + F \cdot (X_{r2,G} - X_{r3,G})$ 計算得出的。
```

### 資工術語保留

常見的資工術語會根據上下文保留原文或進行適當的標註。

### 標題編號移除

自動移除原文標題中的編號（如 1.1, 1.2, 2.3.1）。

## 配置文件格式

配置文件位置：`~/.config/markdown-translator/config.json`

```json
{
  "api_provider": "gemini",
  "gemini_api_key": "your_gemini_api_key_here",
  "openai_api_key": "",
  "target_language": "繁體中文"
}
```

**注意**：API Key 會安全存儲在個人配置目錄中，權限設定為 600（僅所有者可讀寫）。

## 支持的文件格式

- **Markdown**：`.md` - 直接翻譯
- **PDF**：`.pdf` - 使用 MineRU 轉換後翻譯

## 故障排除

### 問題：找不到文件

確保文件路徑正確且文件存在：

```bash
md-translate ./path/to/your/file.md
```

### 問題：API Key 無效

重新進行配置設置：

```bash
md-translate --setup
```

檢查您的 API Key 是否正確有效。

### 問題：翻譯速度慢

這是正常的，因為需要調用 LLM API。翻譯速度取決於：

- 文件大小
- API 網絡連接速度
- LLM 处理能力

系統已使用多執行緒加速，請耐心等待。

### 問題：Chrome 未找到

**錯誤信息**：`chrome not found` 或 `Chromium executable not found`

**解決方案**：

1. **檢查 Chrome 是否安裝**

   ```bash
   which google-chrome          # Linux/macOS
   # 或
   where chrome                 # Windows
   ```

2. **如果未安裝，根據您的系統安裝**

   **macOS**：

   ```bash
   brew install --cask google-chrome
   ```

   **Linux (Ubuntu/Debian)**：

   ```bash
   sudo apt-get install google-chrome-stable
   # 或 Chromium
   sudo apt-get install chromium-browser
   ```

   **Windows**：安裝 [Google Chrome](https://www.google.com/chrome/)

3. **如果 Chrome 已安裝但仍未找到**，設置環境變數：

   ```bash
   export PUPPETEER_EXECUTABLE_PATH=/path/to/chrome
   md-translate file.pdf
   ```

### 問題：Chrome 沙箱錯誤

**錯誤信息**：`Failed to move temp folder` 或沙箱相關錯誤

**解決方案**：

在命令前添加環境變數禁用沙箱（僅在沙箱有問題時使用）：

```bash
export PYPPETEER_CHROMIUM_REVISION=1054519
md-translate file.pdf
```

或編輯 `config.json`（通常在 `~/.md-translate/config.json`），添加：

```json
{
  "chrome_args": ["--no-sandbox", "--disable-setuid-sandbox"]
}
```

### 問題：Chrome 崩潰或超時

**錯誤信息**：`Timeout` 或 `Process crashed`

**解決方案**：

1. **檢查系統資源**（特別是大文件轉換）

   ```bash
   # macOS
   top -o rsize      # 查看記憶體使用
   ```

2. **嘗試以下方法**：
   - **重新啟動工具**：
     ```bash
     md-translate file.pdf
     ```
   - **分割大文件**：如果文件超過 100 頁，嘗試分割成多個小文件
   - **檢查磁盤空間**：確保 `/tmp` 文件夾有足夠空間
     ```bash
     df -h /tmp       # macOS/Linux
     ```

3. **如果持續出現，嘗試升級 Chrome**：

   ```bash
   # macOS
   brew upgrade google-chrome
   ```

### 問題：PDF 生成的 CSS 樣式未應用

**症狀**：使用 `--css` 參數但 PDF 中沒有樣式

**解決方案**：

1. **檢查 CSS 文件路徑**

   ```bash
   md-translate file.md --css ./styles/custom.css   # 使用相對路徑
   md-translate file.md --css /full/path/custom.css # 或絕對路徑
   ```

2. **檢查 CSS 語法**

   確保 CSS 格式正確，例如：

   ```css
   body {
     font-family: Arial, sans-serif;
     background-color: #f5f5f5;
   }

   @media print {
     body {
       margin: 0;
     }
   }
   ```

3. **檢查 CSS 變量**

   系統支持自定義背景顏色變量：

   ```css
   :root {
     --bg-color: #ffffff;
   }

   body {
     background: var(--bg-color);
   }
   ```

## 常見問題（FAQ）

### Q: `-m` 參數是什麼意思？

A: `-m` 表示「只輸出 Markdown 文件，不轉換為 PDF」。

- 不加 `-m`：會生成 Markdown + PDF 文件
- 加 `-m`：只生成 Markdown 文件

```bash
md-translate paper.pdf         # 輸出：paper_trans.md + paper_trans.pdf
md-translate paper.pdf -m      # 輸出：只有 paper_trans.md
```

### Q: `--no-translate` 參數的用途？

A: 跳過翻譯步驟，只進行格式轉換。

```bash
md-translate paper.pdf --no-translate        # PDF → PDF（不翻譯）
md-translate paper.md --no-translate         # MD → PDF（不翻譯）
md-translate paper.pdf -m --no-translate     # PDF → MD（不翻譯）
```

### Q: 參數可以組合嗎？順序重要嗎？

A: 是的，參數可以自由組合，**順序完全不重要**。以下命令結果一樣：

```bash
md-translate file.pdf -m --lang 簡體中文 --css custom.css
md-translate file.pdf --css custom.css -m --lang 簡體中文
md-translate file.pdf --lang 簡體中文 --css custom.css -m
```

### Q: 自定義 CSS 有什麼用途？

A: 自定義 CSS 可以控制 PDF 的樣式（顏色、字體、佈局等）。

```bash
md-translate file.md --css dark-theme.css    # 使用深色主題
md-translate file.md --css light-theme.css   # 使用淺色主題
```

系統會自動：

- 檢測 CSS 中的背景顏色
- 為打印優化樣式
- 不修改原始 CSS 文件

### Q: 為什麼所有輸出文件都要加 `_trans` 後綴？

A: 使用 `_trans` 後綴有以下優點：

1. **避免覆蓋原文件**：即使文件名相同，翻譯後的文件也不會覆蓋原始文件
2. **清晰識別**：一眼就能看出哪個文件是翻譯後的版本
3. **版本管理**：同時保留原文和譯文便於對比和版本管理
4. **自動化處理**：腳本可以自動識別哪些文件已翻譯

範例：

```
原始文件: thesis.pdf ✓ 保留
翻譯输出: thesis_trans.pdf ✓ 新文件（不會覆蓋原文件）

原始文件: paper.md ✓ 保留
翻譯输出: paper_trans.md ✓ 新文件（不會覆蓋原文件）
```

### Q: 為什麼有些文件生成了中間 MD 文件又刪除了？

A: 這是正常行為。系統的邏輯是：

**當輸出為 PDF 時**，中間生成的 MD 文件（包括翻譯後的 `_trans.md`）會被自動刪除，只保留最終的 PDF 和原始輸入文件。

**當輸出為 MD 時**，中間轉換的文件不會被刪除（如果有的話）。

詳細說明請參考上面的 **[文件輸出說明](#文件輸出說明)** 部分。

### Q: 所有輸入文件都會被保留嗎？

A: 是的！**所有原始輸入文件（PDF 或 MD）都會被保留**。

系統只會刪除過程中的臨時文件（如 HTML）。

### Q: 可以同時翻譯多個文件嗎？

A: 暫時不支持一次翻譯多個文件。請逐個翻譯：

```bash
md-translate paper1.pdf
md-translate paper2.pdf
md-translate paper3.md
```

### Q: 別人電腦沒裝 Pandoc 怎麼辦？

A: 不用擔心。`pypandoc` 會自動處理：

- 首次運行時自動下載 Pandoc（約 50-100 MB）
- 之後可以離線使用
- 完全自動，用戶無需介入

### Q: 支持哪些語言翻譯？

A: 由 LLM 決定。常見支持的語言包括：

- 繁體中文
- 簡體中文
- English
- 日本語
- 한국어
- Français
- Español
- Deutsch
- 等等

可以嘗試其他語言，LLM 通常會支持。

### Q: 翻譯質量如何？

A: 質量取決於選擇的 LLM。本工具支持的模型：

**Google Gemini**：

- 模型：`gemini-2.5-flash`
- 優點：免費額度充足，速度快，質量不錯
- 適合：快速翻譯、測試、免費用戶

**OpenAI** (默認)：

- 模型：`gpt-5.4-mini`
- 優點：翻譯質量最高，術語準確度最好
- 適合：論文翻譯、專業文檔、要求高質量的場景

公式、代碼、表格會被保護並正確處理。

> 📝 **注意**：模型版本會不定期更新。執行 `md-translate --setup` 可查看當前使用的模型。

| 套件           | 用途                     | 自動處理 |
| -------------- | ------------------------ | -------- |
| `openai`       | OpenAI GPT API 調用      | -        |
| `google-genai` | Google Gemini API 調用   | -        |
| `tqdm`         | 進度條顯示               | -        |
| `mineru`       | PDF 轉換為 Markdown      | -        |
| `pypandoc`     | Markdown 轉換為 HTML/PDF | ✅ 自動  |

### 關於 Pandoc

- `pypandoc` 會自動下載並管理 Pandoc 二進制文件
- 首次使用時會自動下載（約 50-100 MB，一次性）
- 無需手動安裝 Pandoc
- 支持所有平台：Windows、macOS、Linux

## 系統需求

### 必需

- Python >= 3.8
- 有效的 OpenAI API Key 或 Google Gemini API Key

### 可選

- 無（所有系統依賴由包自動處理）
