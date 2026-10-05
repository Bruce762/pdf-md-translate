"""翻譯 prompt：原本的學術模式、易懂模式與自訂模式。"""

PROMPT_LABELS = {
    "academic": "原本的學術翻譯（預設）",
    "plain": "容易理解的翻譯",
    "custom": "自訂 prompt",
}


def build_translation_prompts(text, target_language="繁體中文", is_heading=False,
                              style="academic", custom_prompt=""):
    if style == "plain" or (style == "custom" and custom_prompt.strip()):
        if style == "plain":
            instructions = (
                "你擅長把學術內容翻譯成容易理解的文字。使用自然、親切、清楚的語氣，目的是讓讀者看懂。\n"
                "避免艱澀用字、冗長句子與過度正式的學術腔；優先用日常用語說清楚概念。\n"
                "必要的專業術語保留或標註原文，並用簡短、白話的譯法表達。\n"
                "忠實保留原文的資訊、條件、數字與推論，不省略內容、不過度簡化，也不自行新增解說或例子。\n"
                "翻成繁體中文時使用台灣用語與句法。"
            )
        else:
            instructions = custom_prompt.strip().replace("{target_language}", target_language)
        system_prompt = (
            instructions + "\n\n### 翻譯基本規則：\n"
            f"將以下 Markdown 文字翻譯成{target_language}。\n"
            "嚴格保留 Markdown 格式與 LaTeX 公式：所有以 `$` 或 `$$` 包圍的內容不可變動，保持原始位置。\n"
            "僅輸出翻譯結果，不要加入前言或額外解釋。"
        )
        if is_heading:
            system_prompt += "\n刪除所有標題編號：忽略原文開頭的層級數字（如 1.1, 1.2, 2.3.1 等），僅翻譯後續內容。"
        return f"現在請翻譯以下段落：\n\n{text}", system_prompt

    # 保留現有學術 prompt 與範例，舊設定檔沿用此模式。
    system_prompt = (
        "你的專長是學術論文翻譯。\n\n"
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

    return prompt, system_prompt
