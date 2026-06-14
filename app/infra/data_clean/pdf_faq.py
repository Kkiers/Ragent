from __future__ import annotations

"""
负责「读文件 + 解析 + 清洗 + FAQ 抽取」。
不关心产品是 RAG 还是客服机器人；以后换 PDF 库只动这里。

这份 PDF 里有明显的封面/目录块、反复出现的页眉页脚、页码与罗马数字页码，
以及目录式重复标题，这些都要在切分前先剥掉。
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


# -----------------------------
# 读取 PDF
# -----------------------------


def extract_text_by_page(pdf_path: str) -> List[Dict]:
    """
    读取 PDF，每页提取文本。

    返回：
    - List[Dict]，每项包含 {"page_num": int, "text": str}
    """
    # 优先 pdfplumber；如果环境没有，再回退到 PyMuPDF（fitz）
    try:
        import pdfplumber  # type: ignore

        pages: List[Dict] = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                full_text = page.extract_text() or ""

                # 先找表格区域，再提取“去表格区域”的纯文本，避免表格文字被 extract_text() 乱序挤出来
                table_bboxes: List[Tuple[float, float, float, float]] = []
                try:
                    table_finders = page.find_tables() or []
                    raw_bboxes = [t.bbox for t in table_finders if getattr(t, "bbox", None)]
                    # 防误伤：收缩 bbox，避免把紧贴表格的题干/标题行一并消掉
                    table_bboxes = []
                    for (x0, top, x1, bottom) in raw_bboxes:
                        shrink = 3  # pt 级别的安全边距
                        t2 = top + shrink
                        b2 = bottom - shrink
                        if b2 > t2:
                            table_bboxes.append((x0, t2, x1, b2))
                except Exception:
                    table_bboxes = []

                non_table_page = page
                # pdfplumber 的 outside_bbox 会保留 bbox 外的对象；多表格时逐个剔除
                for bbox in table_bboxes:
                    try:
                        non_table_page = non_table_page.outside_bbox(bbox)
                    except Exception:
                        # 若某个 bbox 导致异常，忽略该 bbox，避免整页失败
                        continue

                masked_text = non_table_page.extract_text() or ""

                # 关键兜底：如果消隐误删了 “5.1 xxx？” 这类问题行，从 full_text 里把问题编号行补回
                # 这样既能去掉表格重影，又不丢问题标题
                full_lines = [ln.strip() for ln in full_text.splitlines() if ln.strip()]
                masked_lines = [ln.strip() for ln in masked_text.splitlines() if ln.strip()]
                missing_q_lines = [
                    ln for ln in full_lines if _QUESTION_START_RE.match(ln) and ln not in masked_lines
                ]
                if missing_q_lines:
                    masked_text = ("\n".join(missing_q_lines) + "\n" + masked_text).strip()
                text = masked_text

                # 表格抽取：转成稳定 KV 文本块，便于检索/RAG
                try:
                    tables = page.extract_tables() or []
                except Exception:
                    tables = []
                table_text = _tables_to_kv_text(tables)
                if table_text:
                    # 关键：避免“表格属于上一题，但被拼到下一题后面”
                    # 若页面连续出现多个问题编号，且第一个问题与第二个问题之间没有正文，
                    # 则把表格块插在第一个问题后面，保证上一题不会变成空答案而被过滤掉。
                    base = (text or "").rstrip()
                    lines = base.splitlines()
                    q_idx = [idx for idx, ln in enumerate(lines) if _QUESTION_START_RE.match((ln or "").strip())]
                    if len(q_idx) >= 2:
                        a, b = q_idx[0], q_idx[1]
                        between = "\n".join(lines[a + 1 : b]).strip()
                        if not between:
                            insert_at = a + 1
                            lines = lines[:insert_at] + ["", table_text, ""] + lines[insert_at:]
                            base = "\n".join(lines).strip()
                            text = base
                        else:
                            text = (base + "\n\n" + table_text).strip() if base else table_text
                    else:
                        # 正常：表格块与正文之间强制“段落级”分隔
                        text = (base + "\n\n" + table_text).strip() if base else table_text

                pages.append({"page_num": i, "text": text})
        return pages
    except ModuleNotFoundError:
        pass

    try:
        import fitz  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "缺少依赖：pdfplumber 或 PyMuPDF（二选一即可）。\n"
            "安装：pip install pdfplumber\n"
            "或：pip install pymupdf"
        ) from e

    doc = fitz.open(pdf_path)
    pages = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = page.get_text("text") or ""
        pages.append({"page_num": i + 1, "text": text})
    doc.close()
    return pages


# -----------------------------
# 清洗规则（页级）
# -----------------------------


_URL_RE = re.compile(r"(https?://[^\s]+|www\.[^\s]+)", re.IGNORECASE)

# 目录点线 / 装饰性点线
_DOT_LEADER_RE = re.compile(r"(\.{5,}|…{3,}|·{3,}|-{5,}|_{5,})")

# 纯页码（数字或罗马数字）
_PAGE_NUM_ONLY_RE = re.compile(r"^\s*(\d+|[ivxlcdm]+)\s*$", re.IGNORECASE)

# 常见页眉页脚/版权/目录标识（可按文档迭代）
_KILL_LINE_PATTERNS: List[re.Pattern] = [
    re.compile(r"^\s*目\s*录\s*$"),
    re.compile(r"^\s*语音通话\s*$"),
    re.compile(r"^\s*常见问题\s*$"),
    re.compile(r"^\s*语音通话\s*/\s*常见问题\s*$"),
    re.compile(r"文档版本.*版权所有", re.IGNORECASE),
    re.compile(r"版权所有\s*©", re.IGNORECASE),
    # 常见问题导航页眉/目录页眉（PDF 抽取常把它们混进正文）
    re.compile(r"^\s*常见问题\s*\d+\s*常见问题导航\s*$"),
    re.compile(r"^\s*常见问题\s*目\s*录\s*$"),
]


def _is_url_only_line(line: str) -> bool:
    line = line.strip()
    if not line:
        return False
    m = _URL_RE.fullmatch(line)
    return m is not None


def _looks_like_toc_line(line: str) -> bool:
    """
    目录行常见形态：
    - 含大量点线 + 行尾页码
    - 或行尾是页码且中间有点线
    """
    s = line.strip()
    if not s:
        return False
    if _DOT_LEADER_RE.search(s) and re.search(r"\d+\s*$", s):
        return True
    # 例如： "2 产品咨询类.................. 10"
    if re.search(r"\.{5,}\s*\d+\s*$", s):
        return True
    return False


def clean_page_text(text: str) -> Tuple[str, List[str]]:
    """
    清洗单页文本。

    返回：
    - cleaned_text: str
    - urls: list[str]
    """
    urls: List[str] = []
    if not text:
        return "", urls

    lines = [ln.rstrip() for ln in text.splitlines()]

    kept: List[str] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # URL：不放进正文，单独抽出来
        if _is_url_only_line(line):
            urls.append(line)
            continue

        # 必删：页码/罗马页码
        if _PAGE_NUM_ONLY_RE.match(line):
            continue

        # 必删：目录行
        if _looks_like_toc_line(line):
            continue

        # 必删：明显装饰性点线
        if _DOT_LEADER_RE.fullmatch(line):
            continue

        # 必删：页眉页脚/版权/版本等
        if any(p.search(line) for p in _KILL_LINE_PATTERNS):
            continue

        # 删除行尾纯页码（常见于页眉/目录残留）
        if re.search(r"\s+\d+\s*$", line) and _DOT_LEADER_RE.search(line):
            continue

        kept.append(line)

    # 去重：同一页重复页眉页脚残留时，保留第一次
    deduped: List[str] = []
    seen: set[str] = set()
    for ln in kept:
        key = ln
        if key in seen:
            continue
        seen.add(key)
        deduped.append(ln)

    # 合并断行（保留大致语义，不做翻译/润色）
    merged = _merge_lines(deduped)
    merged = re.sub(r"\n{3,}", "\n\n", merged).strip()

    # URLs 去重
    urls = list(dict.fromkeys(urls))
    return merged, urls


_SENT_END = set("。！？!?；;：:")


_NAV_PAGE_HINT_RE = re.compile(r"(常见问题导航|目\s*录)", re.IGNORECASE)
_QUESTION_ITEM_RE = re.compile(r"^\s*\d+\.\d+\s*")


def _looks_like_nav_page(text: str) -> bool:
    """
    识别“常见问题导航/目录型”页面：这类页常没有点线，但会密集出现 “2.1 ...” 的条目行。

    经验规则（偏保守）：满足任一条件即可判为导航页
    - 命中目录点线/页码目录行达到阈值（由外层统计触发）
    - 或命中“常见问题导航/目录”提示词，且问题条目行非常密集
    """
    if not text:
        return False
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return False

    hint = any(_NAV_PAGE_HINT_RE.search(ln) for ln in lines[:15])
    q_items = sum(1 for ln in lines if _QUESTION_ITEM_RE.match(ln))

    # 防误杀：如果页面里存在明显“正文/答案”特征，就不要按导航页跳过
    # - 平均行长偏大，或存在较长行（常见于解释句/答案）
    avg_len = sum(len(ln) for ln in lines) / max(1, len(lines))
    max_len = max((len(ln) for ln in lines), default=0)
    has_long_line = max_len >= 45
    has_sentence = any(("。" in ln) or ("：" in ln) for ln in lines)

    # 这份 PDF 的导航页通常会出现大量 2.x/3.x/... 条目，但行普遍很短、缺少解释句
    if (hint and q_items >= 8) or (q_items >= 14):
        if avg_len < 24 and not has_long_line and not has_sentence:
            return True
    return False


def _merge_lines(lines: List[str]) -> str:
    """
    以“尽量还原段落”的方式合并断行：
    - 如果上一行以句末标点结束，则换段
    - 否则倾向拼接为同一段（中文不强制加空格）
    """
    out: List[str] = []
    buf = ""
    for ln in lines:
        if not buf:
            buf = ln
            continue

        prev = buf.rstrip()
        # 规则 1：正常句末标点断句
        if prev and prev[-1] in _SENT_END:
            out.append(buf)
            buf = ln
            continue

        # 规则 2：下一行是新的标题，断开当前段落
        if re.match(r"^\s*(\d+(\.\d+)+)\s+", ln):
            out.append(buf)
            buf = ln
            continue

        # 规则 3（新增）：如果当前缓冲区的文本已经是一个完整的标题，强制断开。
        # 防止像 "2.5 封禁规则" 这样无标点结尾的标题把正文给吸附进去。
        if re.match(r"^\s*(\d+\.\d+)\s+", prev) and len(prev) < 100:
            out.append(buf)
            buf = ln
            continue

        # 默认拼接：中文优先直接拼，英文/参数名之间补空格
        if re.search(r"[A-Za-z0-9]$", prev) and re.match(r"^[A-Za-z0-9]", ln):
            buf = prev + " " + ln
        else:
            buf = prev + ln

    if buf:
        out.append(buf)
    return "\n\n".join(out)


def _tables_to_kv_text(tables: List[List[List[Optional[str]]]]) -> str:
    """
    将 pdfplumber 的 tables 转成稳定的 key-value 文本块。
    - 2 列表格：col1: col2
    - 多列表格：若首行像表头，则表头=值; ...；否则按 "col1=...; col2=..." 输出
    """
    if not tables:
        return ""

    def norm_cell(v: Optional[str]) -> str:
        s = (v or "").strip()
        s = re.sub(r"\s+", " ", s)
        return s

    out_lines: List[str] = []
    for t in tables:
        if not t or not any(row and any((c or "").strip() for c in row) for row in t):
            continue

        # 清理空行/空列的噪声
        rows = [[norm_cell(c) for c in (row or [])] for row in t if row]
        rows = [r for r in rows if any(c for c in r)]
        if not rows:
            continue

        # 统一列宽
        max_cols = max(len(r) for r in rows)
        rows = [r + [""] * (max_cols - len(r)) for r in rows]

        # 2 列：优先认为是字段-值
        if max_cols == 2:
            for k, v in rows:
                if k and v:
                    out_lines.append(f"{k}: {v}。")
                elif k and not v:
                    out_lines.append(f"{k}:。")
                elif v and not k:
                    out_lines.append(f"{v}。")
            continue

        # 多列：判断首行是否为表头（非空比例高、且较短）
        header = rows[0]
        header_nonempty = sum(1 for c in header if c)
        looks_like_header = header_nonempty >= max(2, int(max_cols * 0.6)) and all(
            len(c) <= 24 for c in header if c
        )

        data_rows = rows[1:] if looks_like_header else rows
        if looks_like_header:
            for r in data_rows:
                parts = []
                for h, v in zip(header, r):
                    if not h and not v:
                        continue
                    if h and v:
                        parts.append(f"【{h}】: {v}")
                    elif h and not v:
                        parts.append(f"【{h}】:")
                    elif v and not h:
                        parts.append(v)
                if parts:
                    out_lines.append(" | ".join(parts) + "。")
        else:
            # 没有表头：按列序号输出，尽量保住映射关系
            for r in data_rows:
                parts = []
                for idx, v in enumerate(r, start=1):
                    if not v:
                        continue
                    parts.append(f"col{idx}={v}")
                if parts:
                    out_lines.append("; ".join(parts) + "。")

    if not out_lines:
        return ""
    # 用一个明显分隔符，防止与正文段落混淆
    return "表格\n\n" + "\n".join(out_lines)


# -----------------------------
# 抽取 FAQ 结构
# -----------------------------


_QUESTION_START_RE = re.compile(r"^\s*(\d+\.\d+)\s*(.+?)\s*$")
# 章节标题：既可能是 "3 计费相关"，也可能是 "3计费相关"（PDF 抽取常丢空格）
_SECTION_TITLE_RE = re.compile(r"^\s*(\d+)\s*(.+?)\s*$")

# 纯标题行（无编号），例如："产品咨询类"、"计费相关"
_BARE_SECTION_TITLE_RE = re.compile(r"^\s*[\u4e00-\u9fffA-Za-z0-9（）()、，,·&\-\s]{2,60}\s*$")

_SECTION_NOISE_RE = re.compile(
    r"(常见问题导航|常见问题|目\s*录|语音通话\s*/\s*常见问题|语音通话\s+常见问题)",
    re.IGNORECASE,
)


def normalize_section_title(title: str) -> str:
    """
    章节标题归一化：去掉导航/页眉噪声，只保留真正分类名。
    例如：
    - "常见问题 1 常见问题导航常见问题导航产品咨询类" -> "产品咨询类"
    """
    t = re.sub(r"\s+", "", title or "")
    if not t:
        return ""
    t = _SECTION_NOISE_RE.sub("", t)
    t = re.sub(r"^\d+", "", t)
    # 去掉重复拼接（例如：API&代码样例API&代码样例）
    if len(t) >= 4 and len(t) % 2 == 0:
        half = len(t) // 2
        if t[:half] == t[half:]:
            t = t[:half]
    m = re.search(r"([^\d]{2,20}(类|相关))$", t)
    if m:
        return m.group(1)
    return t.strip()


_PARSE_PREFIX_RE = re.compile(
    # 注意：不要误删 “2.1 ...” 这种问题编号的前导数字
    # 这里的数字只匹配章号（纯整数，且后面不能紧跟小数点）
    # 同时要求章号后面必须紧跟空白，避免 '10.1' 被回溯成只吃掉 '1' 进而变成 '0.1'
    r"^\s*(语音通话\s*)?(常见问题\s*)?(\d+(?!\.)\s+)?(常见问题导航\s*)?(目\s*录\s*)?",
    re.IGNORECASE,
)


def normalize_line_for_parse(line: str) -> str:
    """
    解析前的行归一化：
    - 剥离常见页眉前缀（如：'语音通话 常见问题 7 API&代码样例' -> '7 API&代码样例'）
    - 保留正文内容，不做润色
    """
    s = (line or "").strip()
    if not s:
        return ""
    # 只剥离行首前缀一次，避免误删正文
    s2 = _PARSE_PREFIX_RE.sub("", s, count=1).strip()
    return s2 or s


@dataclass
class FaqRecord:
    section_id: str
    section_title: str
    question: str
    answer: str
    page_start: int
    page_end: int
    urls: List[str]

    def to_dict(self) -> Dict:
        return {
            "section_id": self.section_id,
            "section_title": self.section_title,
            "question": self.question,
            "answer": self.answer,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "urls": self.urls,
        }


_SECTION_TITLE_BY_CHAPTER: Dict[str, str] = {
    "2": "产品咨询类",
    "3": "计费相关",
    "4": "服务开通相关",
    "5": "号码相关",
    "6": "放音文件及语音模板配置",
    "7": "API&代码样例",
    "8": "录音&收号&TTS相关问题",
    "9": "呼叫状态和话单通知",
    "10": "故障排除",
}


def section_title_from_section_id(section_id: str) -> str:
    """
    按用户指定规则：section_id 的章号决定 section_title。
    - 2.* -> '二 产品咨询类'
    - 3.* -> '计费相关'
    - ...
    - 10.* -> '故障排除'
    """
    sid = (section_id or "").strip()
    if not sid:
        return ""
    chapter = sid.split(".", 1)[0]
    return _SECTION_TITLE_BY_CHAPTER.get(chapter, "")


def extract_faq_records(pdf_path: str) -> Tuple[Dict, List[Dict]]:
    """
    从 FAQ PDF 抽取结构化记录，并返回统计信息与 JSON-friendly 结构。
    """
    pages = extract_text_by_page(pdf_path)

    cleaned_pages: List[Dict] = []
    removed_counts = {
        "url_lines": 0,
        "page_num_lines": 0,
        "toc_lines": 0,
        "header_footer_lines": 0,
        "dot_leader_lines": 0,
        "toc_pages_skipped": 0,  # 新增：记录跳过的目录页数
        "nav_pages_skipped": 0,  # 新增：记录跳过的导航页数（无点线目录）
    }

    for p in pages:
        raw = p["text"] or ""
        toc_lines_in_page = 0
        
        # 统计：粗略估算（按规则命中计数）
        for ln in raw.splitlines():
            s = ln.strip()
            if not s:
                continue
            if _is_url_only_line(s):
                removed_counts["url_lines"] += 1
            elif _PAGE_NUM_ONLY_RE.match(s):
                removed_counts["page_num_lines"] += 1
            elif _looks_like_toc_line(s):
                toc_lines_in_page += 1
                removed_counts["toc_lines"] += 1
            elif any(pat.search(s) for pat in _KILL_LINE_PATTERNS):
                removed_counts["header_footer_lines"] += 1
            elif _DOT_LEADER_RE.search(s):
                removed_counts["dot_leader_lines"] += 1

        cleaned, urls = clean_page_text(raw)

        # 只在“页面几乎没有正文”时才整页跳过，避免误杀像 5.1 这种“标题+表格”的紧凑页面
        body_len = len((cleaned or "").strip())

        # 如果一页里有 3 行以上符合“...... 12”特征的目录线，且正文极少，才认为是目录页并跳过
        if toc_lines_in_page >= 3 and body_len < 160:
            removed_counts["toc_pages_skipped"] += 1
            continue

        # 跳过“常见问题导航/目录型”页面：同样要求正文极少，否则保留给解析器处理
        if _looks_like_nav_page(raw) and body_len < 200:
            removed_counts["nav_pages_skipped"] += 1
            continue

        cleaned_pages.append(
            {"page_num": p["page_num"], "cleaned_text": cleaned, "urls": urls, "raw": raw}
        )

    records = _parse_records_from_pages(cleaned_pages)
    records = _dedupe_merge_records(records)

    stats = {
        "pdf_path": str(pdf_path),
        "removed_noise": removed_counts,
        "faq_count": len(records),
        "duplicates_merged": sum(1 for r in records if r.get("_merged_from", 0) > 0),
    }

    # 输出不携带内部字段
    out = []
    for r in records:
        r.pop("_merged_from", None)
        out.append(r)
    return stats, out


def _parse_records_from_pages(cleaned_pages: List[Dict]) -> List[Dict]:
    section_title = ""
    current: Optional[Dict] = None
    records: List[Dict] = []
    chapter_first_page: Dict[str, int] = {}

    def flush():
        nonlocal current
        if not current:
            return
        current["answer"] = current["answer"].strip()
        current["question"] = current["question"].strip()
        current["urls"] = list(dict.fromkeys(current["urls"]))
        records.append(current)
        current = None

    for page in cleaned_pages:
        page_num = int(page["page_num"])
        text = (page.get("cleaned_text") or "").strip()
        raw = page.get("raw") or ""
        page_urls: List[str] = page.get("urls") or []

        if current:
            current["page_end"] = max(current["page_end"], page_num)

        if not text and not page_urls:
            continue

        if current and page_urls:
            current["urls"].extend(page_urls)
            current["page_end"] = max(current["page_end"], page_num)

        for para in text.split("\n\n"):
            line = normalize_line_for_parse(para)
            if not line:
                continue

            # 章节标题判断
            m_sec = _SECTION_TITLE_RE.match(line)
            if m_sec:
                sec_no, sec_title = m_sec.group(1), m_sec.group(2)
                if (
                    "." not in sec_no
                    and len(sec_title) <= 30
                    and not sec_title.endswith(("？", "?", "。"))
                    and not _QUESTION_START_RE.match(line)
                ):
                    normalized = normalize_section_title(sec_title)
                    if normalized:
                        section_title = normalized
                        chapter_first_page.setdefault(section_title, page_num)
                    continue

            # 纯标题行（无编号）判断
            # 防止把正文步骤/操作描述误识别为标题：这里仅放行“像标题”的短语
            title_like = bool(
                re.search(r"(类$|相关$|样例$|配置$|相关问题$|故障排除$)", line)
                or ("API" in line and "样例" in line)
            )
            if (
                _BARE_SECTION_TITLE_RE.match(line)
                and not _QUESTION_START_RE.match(line)
                and not line.endswith(("？", "?", "。", ".", "！", "!", "；", ";", "：", ":"))
                and title_like
            ):
                normalized = normalize_section_title(line)
                if normalized:
                    section_title = normalized
                    chapter_first_page.setdefault(section_title, page_num)
                continue

            # 问题开始：形如 "2.3 语音通话是否支持录音功能？"
            m_q = _QUESTION_START_RE.match(line)
            if m_q:
                flush()
                q_id = m_q.group(1).strip()
                q_text = m_q.group(2).strip()
                forced_section_title = section_title_from_section_id(q_id) or section_title
                current = {
                    "section_id": q_id,
                    "section_title": forced_section_title,
                    "question": q_text,
                    "answer": "",
                    "page_start": page_num,
                    "page_end": page_num,
                    "urls": list(page_urls),
                    "_merged_from": 0,
                }
                continue

            # 答案正文
            if current:
                # 章标题/节标题不要吸进上一条答案里（尤其是跨章边界时）
                # 例如：上一条是 6.11，下一段出现 '7 API&代码样例'，应被识别为标题而不是答案。
                m_title_guard = _SECTION_TITLE_RE.match(line)
                if m_title_guard and "." not in (m_title_guard.group(1) or ""):
                    sec_title_guard = normalize_section_title(m_title_guard.group(2))
                    if sec_title_guard:
                        section_title = sec_title_guard
                        chapter_first_page.setdefault(section_title, page_num)
                        continue

                # 【核心修复 2】：处理跨行的多行问题
                # 如果目前答案还是空，且问题还没以正常标点结尾
                if not current["answer"] and not re.search(r'[？?。！!]\s*$', current["question"]):
                    # 如果当前段落以问号结尾，或者长度较短，说明它是问题的后半截
                    if re.search(r'[？?]\s*$', line) or (len(line) < 30 and not _QUESTION_START_RE.match(line)):
                        current["question"] += line
                        continue

                # 正常拼接答案
                if current["answer"]:
                    current["answer"] += "\n\n" + line
                else:
                    current["answer"] = line
                current["page_end"] = max(current["page_end"], page_num)
            else:
                continue

    flush()
    return _backfill_records_with_chapter_pages(records, chapter_first_page)


def _backfill_records_with_chapter_pages(
    records: List[Dict], chapter_first_page: Dict[str, int]
) -> List[Dict]:
    """
    兜底修复 page_start / section_title：
    - 有些章标题会以“答案第一行”的形式残留（例如上一条答案末尾拼进了下一章标题）。
    - 有些记录在目录/导航页被误触发后，page_start 会偏早。
    """
    if not records or not chapter_first_page:
        return records

    known_titles = set(chapter_first_page.keys())

    for r in records:
        sec = (r.get("section_title") or "").strip()
        ans = (r.get("answer") or "").strip()
        if not ans:
            continue

        first_line = ans.splitlines()[0].strip() if ans else ""

        # 情况 1：section_title 已经正确，但 page_start 早于该章首次出现页
        if sec in known_titles:
            first_page = chapter_first_page.get(sec)
            if first_page and isinstance(r.get("page_start"), int) and r["page_start"] < first_page:
                r["page_start"] = first_page

        # 情况 2：答案第一行就是某个章标题（强信号），说明 section_title 可能没切过去
        if first_line in known_titles and first_line != sec:
            r["section_title"] = first_line
            first_page = chapter_first_page.get(first_line)
            if first_page:
                # 只向后回填，避免把本来更靠后的页码拉小
                if isinstance(r.get("page_start"), int):
                    r["page_start"] = max(r["page_start"], first_page)
                else:
                    r["page_start"] = first_page

    return records

def _dedupe_merge_records(records: List[Dict]) -> List[Dict]:
    """
    如果同一条 FAQ 被分页/重复切到，合并为一条。
    """
    by_q: Dict[str, Dict] = {}
    for r in records:
        # 归一化问题字符串（去掉空格和标点），解决全角半角、换行导致的匹配失败
        q_norm = re.sub(r'[^\w\u4e00-\u9fff]', '', r["question"])
        # 兜底：如果问题文本在抽取时发生乱码/缺字导致归一化为空，用 section_id 做去重键，避免误合并丢记录
        if not q_norm:
            q_norm = f"__sid__{r.get('section_id','')}"

        if q_norm not in by_q:
            by_q[q_norm] = r
            continue

        exist = by_q[q_norm]
        exist["_merged_from"] = int(exist.get("_merged_from", 0)) + 1

        ans_exist = exist.get("answer", "").strip()
        ans_new = r.get("answer", "").strip()

        # 关键修复：处理 page_start / page_end 被目录项拉低的问题
        if not ans_exist and ans_new:
            # 如果已有记录没答案（大概率是前面的目录项），完全沿用新正文记录的页码
            exist["page_start"] = r["page_start"]
            exist["page_end"] = r["page_end"]
        elif ans_exist and not ans_new:
            # 如果新记录没答案（文档末尾的目录残留），忽略其页码
            pass
        else:
            # 如果两者都有内容，则扩大页码范围
            exist["page_start"] = min(exist["page_start"], r["page_start"])
            exist["page_end"] = max(exist["page_end"], r["page_end"])

        # 合并答案
        if ans_new and ans_new not in ans_exist:
            if ans_exist:
                exist["answer"] = exist["answer"].rstrip() + "\n\n" + ans_new
            else:
                exist["answer"] = ans_new

        # 优化显示：取较长（较完整）的原始问题字符串作为最终展示
        if len(r["question"]) > len(exist["question"]) and ans_new:
            exist["question"] = r["question"]
            exist["section_title"] = r["section_title"]

        exist["urls"] = list(dict.fromkeys((exist.get("urls") or []) + (r.get("urls") or [])))

    # 最终清洗：把只有标题完全没有答案的记录（如无法合并的纯目录项）过滤掉
    return [r for r in by_q.values() if r["answer"].strip()]


# -----------------------------
# CLI
# -----------------------------


def _print_stats(stats: Dict):
    removed = stats.get("removed_noise", {})
    print("清洗统计：")
    print(f"- 删除噪声（粗略计数）: {removed}")
    print(f"- 抽取 FAQ 条数: {stats.get('faq_count')}")
    print(f"- 合并重复/跨页条数: {stats.get('duplicates_merged')}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract structured FAQ records from PDF.")
    parser.add_argument("pdf_path", help="Path to FAQ PDF file")
    parser.add_argument(
        "--out",
        default=None,
        help="Output JSON path (default: <pdf_stem>.json in same directory)",
    )
    args = parser.parse_args()

    pdf_path = args.pdf_path
    out_path = args.out
    if out_path is None:
        p = Path(pdf_path)
        out_path = str(p.with_suffix(".json"))

    stats, records = extract_faq_records(pdf_path)
    _print_stats(stats)

    Path(out_path).write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已输出 JSON: {out_path}")


if __name__ == "__main__":
    main()

