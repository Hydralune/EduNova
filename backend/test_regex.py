import regex
import sys

def test_regex_parts():
    """测试正则表达式的各个部分，找出问题所在"""
    
    # 基本设置
    avoid_at_start = r"[\s\]})>,']"
    punctuation = r"[.!?…]|\.{3}|[\u2026\u2047-\u2049]|[\p{Emoji_Presentation}\p{Extended_Pictographic}]"
    quote_end = r"(?:'(?=`)|''(?=``))"
    sentence_end = f"(?:{punctuation}(?<!{avoid_at_start}(?={punctuation}))|{quote_end})(?=\\S|$)"
    sentence_boundary = f"(?:{sentence_end}|(?=[\\r\\n]|$))"
    lookahead_range = 100
    lookahead_pattern = f"(?:(?!{sentence_end}).){{1,{lookahead_range}}}${sentence_end}"
    not_punctuation_space = f"(?!{punctuation}\\s)"
    
    # 测试句子模式
    try:
        max_length = 100
        sentence_pattern = f"{not_punctuation_space}(?:[^\\r\\n]{{1,{max_length}}}{sentence_boundary}|[^\\r\\n]{{1,{max_length}}}(?={punctuation}|{quote_end})(?:{lookahead_pattern})?){avoid_at_start}*"
        print("句子模式编译成功")
        regex.compile(sentence_pattern)
    except Exception as e:
        print(f"句子模式编译失败: {e}")
    
    # 测试正则表达式的各个部分
    parts = [
        ("避免开始", avoid_at_start),
        ("标点符号", punctuation),
        ("引号结束", quote_end),
        ("句子结束", sentence_end),
        ("句子边界", sentence_boundary),
        ("前瞻模式", lookahead_pattern),
        ("非标点空格", not_punctuation_space)
    ]
    
    for name, pattern in parts:
        try:
            regex.compile(pattern)
            print(f"{name} 编译成功")
        except Exception as e:
            print(f"{name} 编译失败: {e}")
    
    # 测试简化版的正则表达式
    try:
        simple_regex = r"([^\n]{1,100}(?:[.!?]|$))"
        regex.compile(simple_regex)
        print("简化版正则表达式编译成功")
    except Exception as e:
        print(f"简化版正则表达式编译失败: {e}")

if __name__ == "__main__":
    test_regex_parts() 