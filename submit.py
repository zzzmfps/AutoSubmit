import time
from typing import Dict, List, Set
from uuid import uuid4

import requests as rq

from jsonio import JsonUtil


class BondChain:
    ''' Auto submit table data.
    '''
    def __init__(self):
        self.conf = JsonUtil.load('assets/conf.json')
        self.user = JsonUtil.load('assets/user.json')
        self.rmap = JsonUtil.load('assets/bank_rank.json')
        self.session_id = uuid4().__str__()

    def login(self):
        ''' @return None\n
        Login to get session id.
        '''
        headers = self.__make_header()
        resp = rq.post(self.conf['login'], json=self.user, headers=headers)
        resp.raise_for_status()
        self.session_id = resp.json()['data']['sessionId']

    def submit_offers(self, banks: List[List[str]], prune: bool = True) -> List[List[str]]:
        ''' @return List[List[str]] - list of failed offers\n
        Add all offers and return failed ones. If `prune` is True, it will
        remove banks of which offers already exist.
        '''
        failed = []
        if prune:
            exists = self.__get_existing_set()
            banks = [v for v in banks if v[0] not in exists]
        for bank in banks:
            print(f'Adding offer of bank {bank[0]}: ', end='')
            bank_id = self.__get_bank_id(bank[0])
            bank_rank = self.__get_rank_by_id(bank_id)
            resp = self.__submit_one_offer(bank_id, bank_rank, bank)
            if resp == '新增报价成功':  # success
                print('SUCCESS')
            else:
                failed.append(f'{bank[0]}: {resp}')
                print('FAILED')
        return failed

    def __make_header(self) -> Dict[str, str]:
        ''' @return Dict[str, str] - request headers\n
        Generate headers of request and return it.
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

    def __get_existing_set(self) -> Set[str]:
        ''' @return Set[str] - set of names of existing banks\n
        Pull all existing offers and convert them into a name set.
        '''
        headers = self.__make_header()
        payload = {
            "orgIssuerId": "",
            "noticeDate": int(1000 * time.time()),
            "sbjRtg": "",
            "startPrice": "",
            "endPrice": "",
            "startAssetSize": "",
            "endAssetSize": "",
            "provinceList": [],
            "nonBankSign": "",
            "openSign": ""
        }
        resp = rq.post(self.conf['offerList'], json=payload, headers=headers)
        return set([
            offer['organizationShortName'] for rg in resp.json()['data'] for tg in rg['sbjRtgList']
            for offer in tg['offerDtlList']
        ])

    def __get_deal_date(self) -> str:
        ''' @return str - next deal date
        '''
        headers = self.__make_header()
        payload = {'dealDate': time.strftime('%Y-%m-%d', time.localtime()), 'market': '1'}
        resp = rq.post(self.conf['nextDealDate'], json=payload, headers=headers)
        return resp.json()['data']

    def __get_bank_id(self, bank_name: str) -> str:
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

    def __get_rank_by_id(self, bank_id: str) -> str:
        ''' @return str - corresponding rank of the institution id
        '''
        headers = self.__make_header()
        payload = {'institutionId': bank_id}
        resp = rq.post(self.conf['getRankById'], json=payload, headers=headers)
        return resp.json()['data']

    def __submit_one_offer(self, bank_id: str, bank_rank: str, bank: List[str]) -> str:
        ''' @return str - message of this offer-adding operation\n
        '''
        headers = self.__make_header()
        template = {
            'issueTermNcd': '',  # duration 1~5: 1M, 3M, 6M, 9M, 1Y
            'refYield': '',
            'amount': '',
            'nonBankSign': 0,
            'openSign': 0,
            'refYieldBulletin': '',  # offer value
            'issuerId': bank_id,
            'issuerCredit': str(['', 'AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+'].index(bank_rank))
        }
        # check validation
        if template['issuerId'] is None: return '未找到该银行（要求名称精确匹配）'
        if template['issuerId'] == '': return '无发行机构 ID'
        if template['issuerCredit'] == '0': template['issuerCredit'] = self.rmap.setdefault(bank[0], '0')
        if template['issuerCredit'] == '0': return '无评级信息'
        # construct payload and submit it
        payload = {'noticeDate': int(1000 * time.time()), 'offerDtlList': []}
        for i, val in enumerate(bank[1:], 1):
            if not val: continue
            offer = template.copy()
            offer['issueTermNcd'] = str(i)
            offer['refYieldBulletin'] = val
            payload['offerDtlList'].append(offer)
        resp = rq.post(self.conf['addOffer'], json=payload, headers=headers)
        return resp.json()['msg']


if __name__ == '__main__':
    pass
