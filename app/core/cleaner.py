# 清洗用户输入脏数据 文本规范化 
# 工具模块 提供各种清洗和规范化功能

import re

# 多个空格变成一个空格
def normalize_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()

# 删除垃圾字符
def strip_control_chars(text: str) -> str:
    return re.sub(r'[\x00-\x1F\x7F]', '', text)

# 中文标点符号转换为英文标点符号 因为很多模型/检索系统更偏向英文符号
def normalize_punctuation(text: str) -> str:
    return (
        text.replace('，', ',')
            .replace('。', '.')
            .replace('！', '!')
            .replace('？', '?')
    )


# 核心函数
# light_query 轻量级处理query
def light_clean(text: str) -> str:
    text = strip_control_chars(text)
    text = normalize_whitespace(text)
    text = normalize_punctuation(text)
    return text

#test
# if __name__ == "__main__":
#     test_text = "  你好\x00，世界！！！  . "
#     print(light_clean(test_text))