# 指令

`pip install -e .` 下載本地套件

`pip install -e . --force-reinstall --no-deps` 下載本地套件（不包含依賴的套件）

## 上傳到pypi的打包指令

`pip install build twine` 安裝等等要用套件

`python3.10 -m build` 會產生dist資料夾裡面有tar.gz、py3-none-any.whl檔案

以我寫的markdown翻譯套件來說，檔案結構應該會長這樣

```
/Users/wangguanzhe/Desktop/code/pythonCode/markdown_translator/test-file/learn.md/Users/wangguanzhe/Desktop/code/pythonCode/markdown_translator/test-file/learn.mdmarkdown_translator/
├── LICENSE                          # 許可證（依賴的套件有的話自己的也要加上或調整）
├── MANIFEST.in                      # 包含清單
├── pyproject.toml                   # Python 項目配置檔案
├── README.md                        # 項目說明文檔（會在pypi頁面顯示）
│
├── md_translator/                   # 主要源代碼目錄
│   ├── __init__.py                  # 包初始化
│   ├── config.py                    # 配置文件
│   └── main.py                      # 主程序
│
├── pdf_md_translate.egg-info/       # Python 包元數據目錄（在build時會自動產生）
│   ├── dependency_links.txt         # 依賴鏈接
│   ├── entry_points.txt             # 入口點配置
│   ├── PKG-INFO                     # 包信息
│   ├── requires.txt                 # 依賴列表
│   ├── SOURCES.txt                  # 源文件列表
│   └── top_level.txt                # 頂層模塊
│
└── dist/                                        # 構建產物（發布包在build時會自動產生）
    ├── pdf_md_translate-0.1.2-py3-none-any.whl  # Wheel 格式包
    └── pdf_md_translate-0.1.2.tar.gz            # 源代碼包
```

`twine upload dist/*` 把套件上傳到PYPI，然後會要求自己PYPI賬號的api key，如果失敗的話可能就是名子取的跟別人一樣

## 版本更新

每次更新都要改toml裡的version到新的版本

`rm -rf dist/ build/ *.egg-info`

`python3 -m build`

`twine upload dist/*`

## pyproject.toml 配置詳解

### [build-system] — 構建系統配置

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

- `requires` — 構建時需要的依賴（必須安裝 setuptools 版本 61.0 以上）
- `build-backend` — 告訴 pip 使用 setuptools 作為構建系統

### [project] — 項目基本信息

```toml
[project]
name = "pdf-md-translate"              # 項目名稱（在 PyPI 上的名稱）
version = "0.1.2"                      # 版本號（遵循語義化版本）
description = "使用 LLM 自動翻譯 PDF 與 Markdown 論文"  # 簡短描述
readme = "README.md"                   # 指定 README 文件位置
requires-python = ">=3.8"              # 支援的 Python 最低版本
```

#### authors — 作者信息

```toml
authors = [
    {name = "Bruce762", email = "a0909861061@gmail.com"}
]
```

- 項目作者的名稱和郵箱，會顯示在 PyPI 上

#### keywords — 搜索關鍵詞

```toml
keywords = ["pdf", "markdown", "translation", "llm", "openai", "gemini"]
```

- PyPI 搜索時用的關鍵詞，幫助用戶發現你的項目

#### classifiers — 項目分類標籤

```toml
classifiers = [
    "Development Status :: 3 - Alpha",              # 開發狀態
    "Intended Audience :: Science/Research",        # 目標用戶
    "License :: OSI Approved :: GNU Affero General Public License v3",  # 許可證
    "Programming Language :: Python :: 3",          # 支援 Python 3
    "Programming Language :: Python :: 3.8",        # 具體版本
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
```

- 顯示在 PyPI 上，便於用戶篩選符合需求的項目

#### dependencies — 依賴包

```toml
dependencies = [
    "openai",           # OpenAI API 客戶端
    "google-genai",     # Google Gemini API
    "tqdm",             # 進度條庫
    "mineru[all]"       # 文檔處理工具（安裝所有功能）
]
```

- 項目運行時必需的第三方包
- 用戶安裝你的項目時會自動安裝這些依賴

### [project.scripts] — 命令行入口

```toml
[project.scripts]
md-translate = "md_translator.main:main"
```

- 格式：`命令名 = "模塊名.檔案名:函數名"`
- 安裝後可以直接命令行運行 `md-translate`
- 會調用 `md_translator/main.py` 中的 `main()` 函數

### [project.urls] — 項目鏈接

```toml
[project.urls]
Homepage = "https://github.com/Bruce762/pdf-md-translate"
Documentation = "https://github.com/Bruce762/pdf-md-translate#readme"
Repository = "https://github.com/Bruce762/pdf-md-translate.git"
```

- 顯示在 PyPI 上，方便用戶找到相關資源

### [tool.setuptools] — Setuptools 工具配置

```toml
[tool.setuptools]
include-package-data = true
packages = ["md_translator"]
```

- `include-package-data = true` — 告訴 setuptools 在打包時包含 `MANIFEST.in` 中指定的非 Python 文件（如 README、LICENSE 等）
- `packages = ["md_translator"]` — 明確指定要打包的包，避免 setuptools 自動發現其他不需要的目錄（如 `images/` 等生成的文件夾）
- 確保發布的包只包含必要的代碼和文檔

#### 常見問題

**問題：`error: Multiple top-level packages discovered`**

當運行 `python3 -m build` 時，如果看到此錯誤，通常是因為工作目錄中存在多個被 setuptools 誤認為是包的目錄（例如運行程序後生成的 `images/` 文件夾）。

**解決方案：**

1. 在 `pyproject.toml` 的 `[tool.setuptools]` 添加 `packages` 配置：

   ```toml
   [tool.setuptools]
   include-package-data = true
   packages = ["md_translator"]
   ```
2. 或者清理工作目錄中的無關文件夾再重試：

   ```bash
   rm -rf dist/ build/ *.egg-info images/
   python3 -m build
   ```

## MANIFEST.in 配置詳解

控制源碼發佈包中要包含哪些**非 Python 文件**（文檔、許可證等）。

### 常用指令

| 指令                                | 說明                   |
| ----------------------------------- | ---------------------- |
| `include README.md`               | 包含 README 文件       |
| `include LICENSE`                 | 包含許可證             |
| `recursive-exclude * __pycache__` | 排除 Python 緩存目錄   |
| `recursive-exclude * *.py[co]`    | 排除 .pyc 和 .pyo 文件 |

### 本項目配置

```
include README.md                      # 包含文檔
include LICENSE                        # 包含許可證
recursive-exclude * __pycache__        # 排除緩存
recursive-exclude * *.py[co]           # 排除編譯文件
```

### 與 pyproject.toml 配合

```toml
[tool.setuptools]
include-package-data = true    # 告訴 setuptools 尊重 MANIFEST.in
```
