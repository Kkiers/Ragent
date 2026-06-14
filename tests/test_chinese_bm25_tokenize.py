import unittest

from app.infra.vector_store_search.chinese_bm25_tokenize import tokenize_for_bm25
"""
只测 BM25 用的中文分词函数jieba  tokenize_for_bm25
对 "语音通话支持录音吗" 能切出至少 2 个 token，
且某个 token 里包含 "录音"（保证 jieba 分词对关键词有用）。
"""

class TestChineseBm25Tokenize(unittest.TestCase):
    def test_non_empty_chinese(self) -> None:
        toks = tokenize_for_bm25("为什么我的号码被拦截了？")
        self.assertGreaterEqual(len(toks), 2)
        self.assertTrue(any("拦截" in t for t in toks))

    def test_empty(self) -> None:
        self.assertEqual(tokenize_for_bm25(""), [])
        self.assertEqual(tokenize_for_bm25("   "), [])


if __name__ == "__main__":
    unittest.main()
