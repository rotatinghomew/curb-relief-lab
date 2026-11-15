import json
import unittest
from pathlib import Path
from curb_relief.partner import operate, parse_time


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(Path('data/release.json').read_text())

    def test_existing_domain_contract(self):
        short=next(row for row in self.data['tables']['trips'] if row['left'] and (parse_time(row['left'])-parse_time(row['entered'])).total_seconds()==900)
        result=operate('/v1/quote',{'trip_id':short['trip_id'],'policy_id':'current','free_available':True},self.data)
        self.assertEqual(result['cents'],0)
        result=operate('/v1/quote',{'trip_id':short['trip_id'],'policy_id':'current','free_available':False},self.data)
        self.assertGreater(result['cents'],0)
        self.assertEqual(result['cents'],sum(row['cents'] for row in result['parts']))


if __name__=='__main__':
    unittest.main()
