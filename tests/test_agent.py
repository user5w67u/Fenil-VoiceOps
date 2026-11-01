import unittest
from unittest.mock import patch
from src.agent import SupportAgent

class FakeRetriever:
    def search(self, query, k=5):
        return [{'source':'pol_returns_v4.md','section':'## [RET-2] Return windows','score':0.8,'text':'Returns are allowed according to category-specific windows.'}]

class AgentTests(unittest.TestCase):
    def setUp(self):
        self.agent=SupportAgent(FakeRetriever())
        self.agent._llm=lambda messages: 'I can help based on the available policy information.'

    @patch('src.agent.order_lookup', return_value={'verification_required':True})
    def test_order_id_never_reveals_data_before_verification(self, lookup):
        result=self.agent.respond('Please check order 12345678')
        lookup.assert_called_once_with('12345678')
        self.assertIn('AI support assistant',result['answer'])
        self.assertIn('verification_required',result['actions'][0]['stage'])
        self.assertNotIn('items',str(result))

    @patch('src.agent.order_lookup', return_value={'verified':False,'verification_required':True})
    def test_allows_only_one_retry(self, lookup):
        self.agent.respond('Order 12345678')
        first=self.agent.respond('9999')
        self.assertTrue(first['actions'][0]['retry_available'])
        second=self.agent.respond('8888')
        self.assertFalse(second['actions'][0]['retry_available'])
        self.assertIsNone(self.agent.pending_order_id)
        self.assertEqual(lookup.call_count,3)  # initial order-ID call plus two verification attempts

    @patch('src.agent.order_lookup', return_value={'found':True,'verified':True,'order_id':'12345678','status':'shipped','items':[]})
    def test_successful_verification_redacts_digits_from_history(self, lookup):
        self.agent.respond('Order 12345678')
        result=self.agent.respond('4321')
        self.assertTrue(any(a.get('verified') for a in result['actions']))
        self.assertNotIn('4321',str(self.agent.history))
        self.assertIn('shipped',str(self.agent.history))

    @patch('src.agent.ticket_create', return_value={'created':True,'ticket_id':'TKTTEST'})
    def test_handover_only_claims_created_after_success(self, create):
        result=self.agent.respond('I want to speak to a human agent')
        create.assert_called_once()
        self.assertIn('TKTTEST',result['answer'])
        self.assertTrue(result['actions'][0]['created'])

if __name__=='__main__': unittest.main(verbosity=2)
