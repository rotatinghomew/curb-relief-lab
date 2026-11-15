import copy
import json
import threading
import unittest
from pathlib import Path
from curb_relief.provider import make_server
from curb_relief.partner import operate
from curb_relief.wire import call, RemoteFailure


class DomainHTTPTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(Path('data/release.json').read_text())
        self.source=make_server(('127.0.0.1',0),self.data)
        self.thread=threading.Thread(target=self.source.serve_forever,daemon=True)
        self.thread.start()
        self.base=f'http://127.0.0.1:{self.source.server_port}'
        self.payload={'trip_id': 't1', 'policy_id': 'current', 'free_available': True}

    def tearDown(self):
        self.source.shutdown()
        self.source.server_close()
        self.thread.join()

    def test_domain_protocol_matches_local_contract(self):
        result=call(self.base,'/v1/quote',{'revision':'release-1',**self.payload})
        expected=operate('/v1/quote',self.payload,self.data)
        self.assertEqual(result,expected)
        self.assertIn('cents',result)

    def test_domain_revision_is_required(self):
        with self.assertRaises(RemoteFailure):
            call(self.base,'/v1/quote',{'revision':'old-release',**self.payload})

    def test_query_does_not_rewrite_published_data(self):
        before=copy.deepcopy(self.data)
        operate('/v1/quote',self.payload,self.data)
        self.assertEqual(before,self.data)


if __name__=='__main__':
    unittest.main()
