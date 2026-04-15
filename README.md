# pdf-md-translate

一個強大的論文翻譯工具，可以：

1. **將 PDF 轉換為 Markdown 文件** - 自動提取 PDF 中的文本和結構，轉換為易於編輯的 Markdown 格式
2. **將文件中的原文翻譯成多種語言** - 使用 LLM（大型語言模型）自動翻譯 PDF 與 Markdown 論文

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

- 選擇 API 提供商（Google Gemini 或 OpenAI）
- 輸入對應的 API Key
- 設定預設翻譯語言

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

| 命令                                    | 別名 | 用途                            |
| --------------------------------------- | ---- | ------------------------------- |
| `md-translate <file>`                   | -    | 翻譯指定的 PDF 或 Markdown 文件 |
| `md-translate <file> --lang <language>` | `-l` | 翻譯文件並指定目標語言          |
| `md-translate --setup`                  | `-s` | 進行初始設置和配置              |
| `md-translate --config`                 | `-c` | 顯示配置文件位置                |
| `md-translate --lang`                   | -    | 進入交互式語言選擇模式          |
| `md-translate --help`                   | `-h` | 顯示幫助信息                    |

## 使用範例

### 範例 1：翻譯英文 Markdown 論文為繁體中文

```bash
md-translate paper.md --lang 繁體中文
```

輸出文件將自動保存為 `paper_translated.md`

### 範例 2：翻譯 PDF 論文

```bash
md-translate research_paper.pdf
```

系統會自動使用 MineRU 將 PDF 轉換為 Markdown，然後進行翻譯。

### 範例 3：使用 OpenAI 而不是 Gemini

首先重新配置：

```bash
md-translate --setup
```

選擇 `openai` 作為 API 提供商，然後：

```bash
md-translate document.md
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

## 依賴說明

| 套件           | 用途                   |
| -------------- | ---------------------- |
| `openai`       | OpenAI GPT API 調用    |
| `google-genai` | Google Gemini API 調用 |
| `tqdm`         | 進度條顯示             |
| `mineru`       | PDF 轉換為 Markdown    |
