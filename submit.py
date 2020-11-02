import time
from typing import Dict, List
from uuid import uuid4

import requests as rq

from jsonio import JsonUtil


class BondChain:
    ''' Auto submit table data to bondchain.io
    '''
    def __init__(self):
        self.conf = JsonUtil.load('assets/conf.json')
        self.user = JsonUtil.load('assets/user.json')
        self.rmap = JsonUtil.load('assets/bank_rank.json')
        self.session_id = uuid4().__str__()

    def login(self):
        ''' @return None\n
        Login to get session id
        '''
        headers = self.__make_header()
        resp = rq.post(self.conf['login'], json=self.user, headers=headers)
        resp.raise_for_status()
        self.session_id = resp.json()['data']['sessionId']

    def add_offers(self, banks: List[List[str]]) -> List[List[str]]:
        ''' @return List[List[str]] - list of failed offers\n
        Add all offers and return failed ones
        '''
        failed = []
        for bank in banks:
            print(f'Adding offer of bank {bank[0]}: ', end='')
            bank_id = self.fuzzy_query(bank[0])
            bank_rank = self.get_rank_by_id(bank_id)
            resp = self.try_to_add_offer(bank_id, bank_rank, bank)
            if resp['status'] == '0':  # success
                print('SUCCESS')
            else:
                failed.append(f'{bank[0]}: {resp["msg"]}')
                print('FAILED')
        return failed

    def __make_header(self) -> Dict[str, str]:
        ''' @return Dict[str, str] - request headers\n
        Generate headers of request and return it
        '''
        return {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'DNT': '1',
            'Host': self.conf['Host'],
            'lid': self.session_id,
            'Origin': self.conf['Origin'],
            'Referer': self.conf['Referer'],
            'User-Agent': self.conf['User-Agent']
        }

    def next_deal_date(self) -> str:
        ''' @return str - next deal date
        '''
        headers = self.__make_header()
        payload = {'dealDate': time.strftime('%Y-%m-%d', time.localtime()), 'market': '1'}
        resp = rq.post(self.conf['nextDealDate'], json=payload, headers=headers)
        return resp.json()['data']

    def fuzzy_query(self, bank_name: str) -> str:
        ''' @return str - institution id of the bank\n
        An empty id means the bank has no id yet; `None` means cannot find
        a bank that exactly match the given string `bank_name`.
        '''
        headers = self.__make_header()
        payload = {'enqrVal': bank_name, 'pageNum': 1, 'pageSize': 10}
        resp = rq.post(self.conf['fuzzyQuery'], json=payload, headers=headers)
        for bank in resp.json()['data']['list']:
            if bank['organizationShortName'] == bank_name:
                return bank.setdefault('issuerId', '')
        return None

    def get_rank_by_id(self, bank_id: str) -> str:
        ''' @return str - corresponding rank of the institution id
        '''
        headers = self.__make_header()
        payload = {'institutionId': bank_id}
        resp = rq.post(self.conf['getRankById'], json=payload, headers=headers)
        return resp.json()['data']

    def try_to_add_offer(self, bank_id: str, bank_rank: str, bank: List[str]) -> bool:
        ''' @return bool - whether this offer had been submitted successfully\n
        '''
        headers = self.__make_header()
        offer_template = {
            'issueTermNcd': '',  # duration 1~5: 1M, 3M, 6M, 9M, 1Y
            'refYield': '',
            'amount': '',
            'nonBankSign': 0,
            'openSign': 0,
            'refYieldBulletin': '',  # offer value
            'issuerId': bank_id,
            'issuerCredit': str(['', 'AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+'].index(bank_rank))
        }
        payload = {'noticeDate': int(1000 * time.time()), 'offerDtlList': []}
        for i, val in enumerate(bank[1:], 1):
            if not val: continue
            offer = offer_template.copy()
            offer['issueTermNcd'] = str(i)
            offer['refYieldBulletin'] = val
            payload['offerDtlList'].append(offer)
        resp = rq.post(self.conf['addOffer'], json=payload, headers=headers)
        return resp.json()


if __name__ == '__main__':
    pass
