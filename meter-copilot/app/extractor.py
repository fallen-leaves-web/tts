"""从用户问题中提取台区编号。"""
import re

# 示例：TQ-10086、tq-10001（不区分大小写）
DISTRICT_PATTERN = re.compile(r"\b(TQ-\d{4,6})\b", re.IGNORECASE)


def extract_district_id(question: str) -> str | None:
    match = DISTRICT_PATTERN.search(question.strip())
    if not match:
        return None
    return match.group(1).upper()
