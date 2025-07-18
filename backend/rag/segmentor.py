import regex
# Import Optional to fix the type hint error
from typing import List, Dict, Any, Tuple, Optional

# 默认配置
DEFAULT_CONFIG = {
  "maxHeadingLength": 7,
  "maxHeadingContentLength": 200,
  "maxHeadingUnderlineLength": 200,
  "maxHtmlHeadingAttributesLength": 100,
  "maxListItemLength": 200,
  "maxNestedListItems": 6,
  "maxListIndentSpaces": 7,
  "maxBlockquoteLineLength": 200,
  "maxBlockquoteLines": 15,
  "maxCodeBlockLength": 1500,
  "maxCodeLanguageLength": 20,
  "maxIndentedCodeLines": 20,
  "maxTableCellLength": 200,
  "maxTableRows": 20,
  "maxHtmlTableLength": 2000,
  "minHorizontalRuleLength": 3,
  "maxSentenceLength": 400,
  "maxQuotedTextLength": 300,
  "maxParentheticalContentLength": 200,
  "maxNestedParentheses": 5,
  "maxMathInlineLength": 100,
  "maxMathBlockLength": 500,
  "maxParagraphLength": 1000,
  "maxStandaloneLineLength": 800,
  "maxHtmlTagAttributesLength": 100,
  "maxHtmlTagContentLength": 1000,
  "lookaheadRange": 100
}

def create_chunk_regex(config: Dict[str, Any]) -> Any:
    """
    根据配置创建用于文本分块的正则表达式。
    从JavaScript版本转换为Python版本，修复了开放组引用问题
    """
    max_heading_length = config["maxHeadingLength"]
    max_heading_content_length = config["maxHeadingContentLength"]
    max_paragraph_length = config["maxParagraphLength"]
    max_sentence_length = config["maxSentenceLength"]
    max_list_item_length = config["maxListItemLength"]
    max_code_block_length = config["maxCodeBlockLength"]
    max_table_cell_length = config["maxTableCellLength"]

    # 简化的句子模式，避免复杂的引用和嵌套
    sentence_pattern = r"[^\r\n]{1,{MAX_LENGTH}}"

    # 构建正则表达式部分
    regex_parts = [
        # 标题匹配
        f"(?:^#{1,{max_heading_length}} [^\r\n]{{1,{max_heading_content_length}}}(?:\r?\n|$))",
        
        # 列表项匹配 ()
        f"(?:(?:^|\\r?\\n)[ \\t]{{0,3}}(?:[-*+•]|\\d{{1,3}}\\.) [^\r\n]{{1,{max_list_item_length}}})",
        
        # 代码块匹配 ()
        f"(?:(?:^|\\r?\\n)```[\\s\\S]{{0,{max_code_block_length}}}?```(?:\\r?\\n|$))",
        
        # 表格匹配 ()
        f"(?:(?:^|\\r?\\n)\\|[^\\r\\n]{{0,{max_table_cell_length}}}\\|(?:\\r?\\n|$))",
        
        # 段落匹配 ()
        f"(?:(?:^|\\r?\\n\\r?\\n)[^\r\n]{{1,{max_paragraph_length}}}(?=\\r?\\n\\r?\\n|$))",
        
        # 句子匹配 ()
        f"[^\r\n]{{1,{max_sentence_length}}}"
    ]
    
    # 合并所有部分
    regex_str = "|".join(regex_parts)
    
    # 创建最终的正则表达式
    return regex.compile(f"({regex_str})", regex.MULTILINE | regex.UNICODE)

def split_text_into_chunks(text: str, config: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    将文本分割成语义块。
    使用复杂的正则表达式进行精确分割，失败时回退到简单分割
    """
    try:
        import logging
        final_config = {**DEFAULT_CONFIG, **(config or {})}
        
        # 使用正则表达式分割文本
        chunk_regex = create_chunk_regex(final_config)
        matches = chunk_regex.findall(text)
        
        # 修复：findall可能返回元组，需要正确处理
        chunks = []
        for match in matches:
            # 如果匹配结果是元组，取第一个元素
            if isinstance(match, tuple):
                chunk = match[0]
            else:
                chunk = match
                
            if chunk and chunk.strip():
                chunks.append(chunk)
        
        if chunks:
            logging.info(f"使用正则表达式成功分割文本为 {len(chunks)} 个块")
            return chunks
        else:
            # 如果没有匹配到任何内容，回退到简单分割
            logging.info("正则表达式没有匹配到内容，回退到简单分割")
            return _simple_split_fallback(text, final_config["maxParagraphLength"])
    except Exception as e:
        import logging
        logging.error(f"复杂正则表达式分割失败: {e}")
        # 出错时回退到简单分割
        return _simple_split_fallback(text, DEFAULT_CONFIG["maxParagraphLength"])

def _simple_split_fallback(text: str, max_length: int = 300) -> List[str]:
    """简单的分割方法，作为回退"""
    import logging
    logging.info("回退到简单分割方法")
    
    # 按段落分割
    paragraphs = text.split('\n\n')
    chunks = []
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
            
        # 如果段落很短，直接添加
        if len(paragraph) <= max_length:
            chunks.append(paragraph)
            continue
            
        # 否则按句子分割
        sentences = []
        # 简单的中文句子分割
        for sent in regex.split(r'([。！？\.\!\?]+)', paragraph):
            if sent:
                sentences.append(sent)
        
        current_chunk = ""
        for sent in sentences:
            if len(current_chunk) + len(sent) <= max_length:
                current_chunk += sent
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sent
                
        if current_chunk:
            chunks.append(current_chunk)
    
    logging.info(f"简单分割方法产生了 {len(chunks)} 个块")
    return [chunk for chunk in chunks if chunk.strip()]

def split_text_with_max_length(text: str, max_length: int) -> List[str]:
    """
    一个简化的文本分割函数，主要通过最大长度来配置分块行为。
    """
    config = {
        "maxSentenceLength": max_length,
        "maxParagraphLength": max_length,
        "maxStandaloneLineLength": max_length,
        "maxHeadingContentLength": min(max_length, 200),
        "maxListItemLength": min(max_length, 200),
        "maxBlockquoteLineLength": min(max_length, 200),
        "maxCodeBlockLength": min(max_length * 2, 1500),
        "maxQuotedTextLength": min(max_length, 300),
        "maxParentheticalContentLength": min(max_length, 200)
    }
    return split_text_into_chunks(text, config)

def min_concat_segments_optimized(strings: List[str], max_length: int) -> List[str]:
    """
    使用动态规划和滑动窗口优化的字符串合并算法，确保分组数量最少。
    """
    n = len(strings)
    lengths = [len(s) for s in strings]

    for i, length in enumerate(lengths):
        if length > max_length:
            raise ValueError(f"第 {i+1} 个字符串的长度 ({length}) 超过了最大长度 ({max_length})")

    dp = [float('inf')] * (n + 1)
    dp[0] = 0
    prev = [-1] * (n + 1)

    left = 0
    total = 0
    for right in range(1, n + 1):
        total += lengths[right - 1]
        while total > max_length and left < right - 1:
            total -= lengths[left]
            left += 1
        dp[right] = dp[left] + 1
        prev[right] = left

    groups: List[Tuple[int, int]] = []
    idx = n
    while idx > 0:
        start = prev[idx]
        groups.append((start, idx - 1))
        idx = start
    groups.reverse()

    result: List[str] = []
    for start, end in groups:
        result.append("".join(strings[start : end + 1]))
    return result


def merge_chunks_by_length_greedy(chunks: List[str], max_length: int) -> List[str]:
    """
    贪心算法版本的合并函数，作为备选方案。
    """
    if not chunks:
        return []
    
    merged_chunks: List[str] = []
    current_chunk = chunks[0]
    
    for i in range(1, len(chunks)):
        next_chunk = chunks[i]
        if len(current_chunk) + len(next_chunk) <= max_length:
            current_chunk += next_chunk
        else:
            merged_chunks.append(current_chunk)
            current_chunk = next_chunk
            
    merged_chunks.append(current_chunk)
    return merged_chunks


def merge_chunks_by_length(chunks: List[str], max_length: int) -> List[str]:
    """
    将分割后的文本块重新合并，确保不超过最大长度。
    """
    if not chunks:
        return []
    try:
        return min_concat_segments_optimized(chunks, max_length)
    except ValueError:
        return merge_chunks_by_length_greedy(chunks, max_length)


def segment_text(text: str, max_length: int = 300) -> List[str]:
    """
    主要的文本分割和合并函数。
    首先使用复杂正则表达式分割，如果失败则回退到简单分割
    """
    try:
        # 使用复杂正则表达式分割
        split_result = split_text_with_max_length(text, max_length)
        if split_result:
            return merge_chunks_by_length(split_result, max_length)
    except Exception as e:
        import logging
        logging.error(f"使用复杂分割器时出错: {e}")
    
    # 如果复杂分割失败，回退到简单分割
    chunks = []
    
    # 按段落分割
    paragraphs = text.split('\n')
    current_chunk = ""
    
    for paragraph in paragraphs:
        # 如果段落为空，跳过
        if not paragraph.strip():
            continue
            
        # 如果段落很短，尝试合并到当前块
        if len(current_chunk) + len(paragraph) <= max_length:
            if current_chunk:
                current_chunk += "\n"
            current_chunk += paragraph
        else:
            # 如果当前块不为空，添加到结果中
            if current_chunk:
                chunks.append(current_chunk)
                
            # 如果段落本身超过最大长度，需要进一步分割
            if len(paragraph) > max_length:
                # 简单的按句子分割
                sentences = regex.split(r'([。！？\.\!\?]+)', paragraph)
                current_chunk = ""
                
                for sentence in sentences:
                    if not sentence:
                        continue
                        
                    if len(current_chunk) + len(sentence) <= max_length:
                        current_chunk += sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        
                        # 如果句子本身超过最大长度，按字符分割
                        if len(sentence) > max_length:
                            for i in range(0, len(sentence), max_length):
                                chunks.append(sentence[i:i+max_length])
                            current_chunk = ""
                        else:
                            current_chunk = sentence
            else:
                current_chunk = paragraph
    
    # 添加最后一个块
    if current_chunk:
        chunks.append(current_chunk)
        
    return [chunk for chunk in chunks if chunk.strip()]


# --- 示例用法 ---
# FIX: Ensured the multi-line string is properly terminated with """
# if __name__ == '__main__':
#     sample_text = """
