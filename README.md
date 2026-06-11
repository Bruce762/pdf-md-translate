# pdf-md-translate

把 **PDF / Markdown 論文翻譯成你要的語言**，並輸出排版好看的 PDF。

支持 OpenAI GPT 與 Google Gemini，自動保留 LaTeX 公式、程式碼與表格。

```bash
pip install pdf-md-translate     # 1. 安裝
md-translate --setup             # 2. 設定 API Key（第一次才需要）
md-translate paper.pdf           # 3. 翻譯！輸出 paper_trans.pdf
```

---

## 安裝（3 步驟）

### 1. 安裝 Chrome（用來生成 PDF）

| 系統 | 指令 |
| --- | --- |
| **macOS** | `brew install --cask google-chrome` |
| **Linux** | `sudo apt-get install google-chrome-stable`（或 `chromium-browser`） |
| **Windows** | 下載 [Google Chrome](https://www.google.com/chrome/) |

> 只輸出 Markdown（加 `-m`）時不需要 Chrome。

### 2. 安裝套件

```bash
pip install pdf-md-translate
```

需要 Python 3.10 ~ 3.13。Pandoc 會在第一次使用時自動下載，不用手動裝。

### 3. 設定 API Key

```bash
md-translate --setup
```

互動式選單：選擇提供商 → 輸入 API Key 或切換使用中的提供商，可隨時重新進入修改。

| 提供商 | 模型 |
| --- | --- |
| **OpenAI**（預設） | `gpt-5.4-mini` |
| **Google Gemini** | `gemini-3.1-flash-lite` |

---

## 開始使用

> 兩個命令完全等價：`md-translate`（別名）和 `pdf-md-translate`（套件名）。下面都用 `md-translate`。

### 翻譯一個檔案

```bash
md-translate paper.pdf       # PDF → 翻譯 → 輸出 paper_trans.pdf
md-translate paper.md        # Markdown → 翻譯 → 輸出 paper_trans.pdf
```

預設翻成**繁體中文**，輸出檔名固定加上 `_trans` 後綴，**不會覆蓋你的原始檔案**。

### 指定翻譯語言

```bash
md-translate paper.pdf --lang 簡體中文
md-translate paper.pdf -l English      # -l 是 --lang 的簡寫
```

常用語言：`繁體中文`、`簡體中文`、`English`、`日本語`、`한국어`…（LLM 支援的語言都可以試）

### 只要 Markdown，不要 PDF

```bash
md-translate paper.pdf -m              # 輸出 paper_trans.md（不生成 PDF）
```

### 只轉檔不翻譯

```bash
md-translate paper.pdf --no-translate  # PDF → PDF，跳過翻譯
```

就這些。下面是進階選項與細節，需要時再看。

---

## 進階選項

| 參數 | 簡寫 | 作用 |
| --- | --- | --- |
| `--lang LANG` | `-l` | 指定翻譯**目標**語言（不加則用預設） |
| `--md-only` | `-m` | 只輸出 Markdown，不轉 PDF |
| `--no-translate` | | 跳過翻譯，只做格式轉換 |
| `--css FILE` | `--style FILE` | 用自訂 CSS 生成 PDF |
| `--no-css` | | 用內建 **GitHub 風格主題**（白底、Open Sans） |
| `--black-css` | | 用內建 **night 暗色主題**（深色背景、適合螢幕閱讀） |
| `--cpu` | | PDF 轉檔改用輕量 CPU 後端（低資源備援，辨識較弱） |
| `--ocr-lang LANG` | | PDF **原文**的 OCR 辨識語言（預設 `en`） |

設定命令：

| 命令 | 簡寫 | 作用 |
| --- | --- | --- |
| `md-translate --setup` | `-s` | 重新設定 API Key 與預設語言 |
| `md-translate --config` | `-c` | 顯示設定檔位置 |
| `md-translate --lang` | | 互動式選擇預設語言 |
| `md-translate --help` | `-h` | 顯示說明 |

**參數可任意順序、任意組合**，例如：

```bash
md-translate thesis.pdf --lang 繁體中文 --no-css
md-translate file.pdf -m --no-translate --ocr-lang ch_lite
```

> ⚠️ **別把兩個「語言」搞混**：
> - `--lang` / `-l` = 要翻成**什麼**語言（翻譯目標）
> - `--ocr-lang` = PDF 原文**本身**是什麼語言（OCR 辨識來源）
>
> 翻譯非英文論文時，要改的是 `--ocr-lang`，不是 `-l`。

---

## 它做了什麼（處理流程）

```
PDF  ──(mineru)──►  Markdown  ──(LLM)──►  翻譯後 Markdown  ──(pandoc+Chrome)──►  PDF
MD   ─────────────────────────(LLM)──►  翻譯後 Markdown  ──(pandoc+Chrome)──►  PDF
```

- **輸出檔名**統一加 `_trans` 後綴：`paper.pdf` → `paper_trans.pdf`
- **原始檔案永遠保留**，翻譯結果是新檔案
- 最終輸出 PDF 時，中間的 `.md` 與圖片資料夾會自動清掉；用 `-m` 時則保留 `.md`

### 不同輸入 × 參數的輸出對照

| 命令 | 流程 | 輸出 |
| --- | --- | --- |
| `md-translate file.pdf` | PDF→MD→翻譯→PDF | `file_trans.pdf` |
| `md-translate file.pdf -m` | PDF→MD→翻譯 | `file_trans.md` |
| `md-translate file.pdf --no-translate` | PDF→MD→PDF | `file_trans.pdf` |
| `md-translate file.pdf -m --no-translate` | PDF→MD | `file_trans.md` |
| `md-translate file.md` | 翻譯→PDF | `file_trans.pdf` |
| `md-translate file.md -m` | 翻譯 | `file_trans.md` |
| `md-translate file.md --no-translate` | →PDF | `file_trans.pdf` |

---

## 翻譯特性

- 🧮 **保留 LaTeX 公式**：`$...$` / `$$...$$` 內容原封不動，不翻譯
- 💻 **保留程式碼與表格**：程式碼塊（```）、Markdown／HTML 表格不翻譯
- 🔖 **資工術語**：常見術語會保留原文或標註原文
- 🔢 **移除標題編號**：自動去掉原文標題的 `1.1`、`2.3.1` 等編號
- 📑 **雙語對照**：內文輸出「原文 + 譯文」對照（標題則同行並排）

範例——公式在翻譯後位置不變：

> 原文：The mutant vector `$V_{i,G+1}$` is calculated using `$V_{i,G+1} = X_{r1,G} + F \cdot (X_{r2,G} - X_{r3,G})$`.
>
> 譯文：變異向量 `$V_{i,G+1}$` 是使用公式 `$V_{i,G+1} = X_{r1,G} + F \cdot (X_{r2,G} - X_{r3,G})$` 計算得出的。

---

## PDF 樣式（CSS）

輸出 PDF 時有四種樣式可選，**擇一使用**：

```bash
md-translate paper.md                 # 預設主題（PT Serif 襯線、米色背景）
md-translate paper.md --no-css        # 內建 GitHub 主題（Open Sans、白底）
md-translate paper.md --black-css     # 內建 night 暗色主題（深色背景）
md-translate paper.md --css mine.css  # 你自己的 CSS
```

### `--no-css`：內建 GitHub 主題

不用自己寫 CSS 就能套用乾淨現代的版面：

- 🅰️ Open Sans 字體 + 白色背景，貼近 GitHub 的 Markdown 預覽
- 📦 字體已內建，免另外安裝
- 🈶 完整中文支援（含程式碼區塊內的中文）
- 🧱 程式碼區塊是單一連續方框，不會斷裂

### `--black-css`：內建 night 暗色主題

深色背景版面，適合在螢幕上閱讀：

- 🌙 深灰背景（`#363B40`）+ 淺色文字，長時間閱讀較不刺眼
- 🈶 完整中文支援（含程式碼區塊內的中文）
- 🎨 程式碼採暗色語法高亮，在深色底上清晰易讀

> 此主題以 Typora 的 night 主題為基礎，並針對 PDF 輸出補上中文字體與程式碼區塊樣式。

### `--css`：自訂樣式

最簡單的做法是複製內建的 [`default.css`](https://github.com/Bruce762/markdown_translator/blob/main/md_translator/default.css) 改：

```bash
cp default.css my_style.css
# 編輯 my_style.css …
md-translate paper.md --css my_style.css
```

系統會自動偵測背景色、加上列印最佳化，且**不會修改你的原始 CSS 檔**。支援 `--bg-color` 等 CSS 變數。

> ℹ️ **中文字體**：靠系統內建的 CJK 字體顯示（macOS／Windows 開箱即用）。極簡 Linux 環境若缺中文字體，請自行安裝，例如 `apt install fonts-noto-cjk`。

---

## CPU 模式與後端差異（`--cpu`）

很多人以為 `--cpu` 只是「把 GPU 的工作改用 CPU 做、單純變慢」，其實**它會切換成另一套完全不同的解析引擎**，辨識能力也跟著不同：

| | 不加 `--cpu`（預設 VLM 後端） | 加 `--cpu`（pipeline 後端） |
| --- | --- | --- |
| **核心模型** | 視覺語言模型 MinerU2.5（VLM） | 傳統 CV 流水線：版面偵測 + PaddleOCR + 公式／表格模型 |
| **工作方式** | 像「看懂整頁」一樣直接輸出結構化 markdown | 分模組：先框版面 → 再分別 OCR |
| **程式碼辨識** | 完整（行內、程式碼塊） | 弱，圖片式偽代碼常抓不到 |
| **算力需求** | 需要 GPU（M 系列 Mac 用 Apple GPU 跑） | 輕量，CPU 也能跑 |

> 💡 **結論**：追求辨識品質就**不要加 `--cpu`**，走預設 VLM 後端；`--cpu` 只當作記憶體不足、預設模式跑不動時的輕量備援，代價是辨識明顯變弱。
>
> 🍎 **Mac 用戶**：M 系列 Mac 不加 `--cpu` 時會用 Apple GPU 跑精度更高的 VLM 後端，建議優先不要加 `--cpu`。

---

## OCR 語言（`--ocr-lang`）

`--ocr-lang` 決定 mineru 用哪種語言模型辨識**原文 PDF**，預設 `en`（適合英文論文）。翻譯非英文論文時要改的是這個參數，不是 `--lang`：

```bash
md-translate english_paper.pdf                          # 英文論文（預設 en）
md-translate 中文論文.pdf --ocr-lang ch_lite             # 中文論文
md-translate 中文論文.pdf --ocr-lang ch_lite --lang 英文  # 中文原文 → 翻成英文
```

常用代碼（完整清單見 `mineru --help`）：

| 代碼 | 語言 | 備註 |
| --- | --- | --- |
| `en` | 英文 | **預設值**，最適合英文論文 |
| `ch_lite` | 簡體中文（輕量） | ✅ **中文首選**：字典匹配、不會崩 |
| `ch_server` | 簡體中文（伺服器版） | 比 lite 更準；加 `--cpu` 時會被降級成 `ch_lite` |
| `chinese_cht` | 繁體中文 | 加 `--cpu` 時會被降級成 `ch_lite` |
| `japan` | 日文 | 加 `--cpu` 時會被降級成 `ch_lite` |
| `korean` | 韓文 | |
| `latin` | 拉丁字母系（英／法／德／西等） | |
| `arabic` / `cyrillic` / `devanagari` / `th` … | 阿拉伯／西里爾／天城文／泰文等 | |
| `ch` | 簡體中文 | ⚠️ **不建議**：舊字典不匹配，含表格時會崩潰 |

---

## 設定檔

位置：`~/.config/markdown-translator/config.json`（用 `md-translate --config` 查看）

```json
{
  "api_provider": "openai",
  "openai_api_key": "your_key_here",
  "gemini_api_key": "",
  "target_language": "繁體中文"
}
```

> API Key 以 600 權限（僅所有者可讀寫）安全存放在個人設定目錄。

---

## 故障排除

<details>
<summary><b>找不到 Chrome（<code>chrome not found</code> / <code>Chromium executable not found</code>）</b></summary>

1. 確認已安裝：`which google-chrome`（macOS／Linux）或 `where chrome`（Windows）
2. 沒裝就依〈安裝〉一節裝 Chrome
3. 已裝但仍找不到，指定路徑：
   ```bash
   export PUPPETEER_EXECUTABLE_PATH=/path/to/chrome
   md-translate file.pdf
   ```
</details>

<details>
<summary><b>Chrome 沙箱錯誤（<code>Failed to move temp folder</code>）</b></summary>

在命令前停用沙箱（僅在出問題時用）：
```bash
export PYPPETEER_CHROMIUM_REVISION=1054519
md-translate file.pdf
```
</details>

<details>
<summary><b>Chrome 崩潰或超時</b></summary>

- 大檔案很吃資源，確認記憶體與 `/tmp` 空間足夠（`df -h /tmp`）
- 超過 100 頁的文件可先切成小檔
- 試著升級 Chrome：`brew upgrade google-chrome`
</details>

<details>
<summary><b>API Key 無效</b></summary>

重新設定並確認 Key 正確：`md-translate --setup`
</details>

<details>
<summary><b>API 配額超限（429）</b></summary>

工具會在配額不足時自動停止並顯示已翻譯進度。可：等配額重置、升級方案、或 `--setup` 切換到另一個提供商。
</details>

<details>
<summary><b><code>--css</code> 樣式沒套用</b></summary>

- 確認 CSS 路徑正確（相對或絕對路徑皆可）
- 確認 CSS 語法正確、背景色用 `--bg-color` 變數或 `body { background: ... }`
</details>

<details>
<summary><b>翻譯很慢</b></summary>

正常現象，速度取決於檔案大小、網路、與 LLM。OpenAI 和 Gemini 都用 5 線程並發，請耐心等待。
</details>

---

## 常見問題

**Q：兩個命令 `md-translate` 和 `pdf-md-translate` 有差別嗎？**
完全一樣，任選一個用。

**Q：`-m` 和 `--no-translate` 差在哪？**
`-m` = 只輸出 Markdown 不轉 PDF；`--no-translate` = 跳過翻譯只轉檔。兩者可一起用。

**Q：原始檔案會被覆蓋嗎？**
不會。輸出一律加 `_trans` 後綴，原始 PDF／MD 永遠保留。

**Q：可以一次翻譯多個檔案嗎？**
目前不行，請逐一執行。

**Q：Mac 需要加 `--cpu` 嗎？**
建議不要。M 系列 Mac 預設用 Apple GPU 跑更準的 VLM 後端，只有跑不動時才拿 `--cpu` 當備援（見〈CPU 模式與後端差異〉）。

**Q：要先裝 Pandoc 嗎？**
不用。`pypandoc` 會在第一次使用時自動下載（約 50–100 MB，一次性）。

**Q：支援哪些翻譯語言？**
由 LLM 決定，繁中／簡中／英／日／韓／法／西／德等常見語言都支援，其他語言也可以試。

---

## 相依套件

| 套件 | 用途 |
| --- | --- |
| `openai` / `google-genai` | 呼叫 LLM 翻譯 API |
| `mineru[all]` | PDF → Markdown |
| `pypandoc` | Markdown → HTML/PDF（自動下載 Pandoc） |
| `tqdm` | 進度條 |

授權：GNU AGPL v3
