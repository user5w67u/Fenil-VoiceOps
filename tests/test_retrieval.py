import unittest
from pathlib import Path
from src.config import DATASET_DIR
from src.retrieval import Retriever

class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retriever=Retriever(DATASET_DIR/'kb')
    def test_superseded_policy_excluded(self):
        sources={c['source'] for c in self.retriever.chunks}
        self.assertNotIn('pol_returns_v3_superseded.md',sources)
    def test_product_catalog_indexed(self):
        self.assertTrue(any(c['source']=='products.csv' for c in self.retriever.chunks))
    def test_return_query_retrieves_current_return_policy(self):
        hits=self.retriever.search('What is the return window for an opened product?',5)
        self.assertTrue(hits)
        self.assertTrue(any(h['source']=='pol_returns_v4.md' for h in hits))

if __name__=='__main__': unittest.main(verbosity=2)
