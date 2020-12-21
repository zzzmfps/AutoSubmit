from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Iterator
from uuid import uuid4

import requests as rq
from PySide2.QtCore import QObject, Signal
from tqdm import tqdm

from util.data import InputUtil, JsonUtil


class RequestUtil(QObject):
    ''' Auto submit table data.
    '''
    new_log = Signal(str)
    cur_percent = Signal(int)

    def __init__(self, use_signal: bool = False) -> None:
        super().__init__()
        self.conf = JsonUtil.load('assets/json/url.json')
        self.user, self.comm = JsonUtil.load('assets/json/user.json')
        self.rmap = JsonUtil.load('assets/json/bank_rank.json')
        self.session_id = uuid4().__str__()
        self.use_signal = use_signal

    def login(self) -> None:
        ''' @return None\n
        Login to get session id.
        '''
        self.__print_or_emit('\nTry to login...')
        try:
            resp = self.__post(self.conf['login'], self.user, timeout=10)
            if resp['status'] != '0': raise rq.exceptions.ConnectionError(resp['msg'])
        except rq.exceptions.RequestException as ex:
            self.__print_or_emit(' ! FAILED to login:', ex.__str__())
            self.__print_or_emit(' ! Exiting...\n')
            exit(1)
        self.session_id = resp['data']['sessionId']
        self.__print_or_emit(f'Received session id [{self.session_id}] from server')

    def add_offers(self, banks: list[list[str]], notice_date: int = None) -> list[list[str]]:
        ''' @return list[list[str]] - list of failed offers\n
        Add all offers and return failed ones.
        '''
        # set offset
        if notice_date is None: notice_date = InputUtil.input_offset()

        # exec one complete data submit operation
        def do_full_submit(bank: list[str]) -> tuple[list[str], str]:
            try:
                bank_id = self.__get_bank_id(bank[0])
                bank_rank = self.__get_rank_by_id(bank_id)
                resp = self.__submit_one_offer(bank_id, bank_rank, bank, notice_date)
            except rq.exceptions.Timeout:
                resp = '请求超时'
            return bank, resp

        # push all tasks into a thread pool
        def push_to_thread_pool(banks: list[list[str]], max_workers: int = 1) -> Iterator[Future]:
            executor = ThreadPoolExecutor(max_workers=max_workers)
            all_tasks = [executor.submit(do_full_submit, bank) for bank in banks]
            return as_completed(all_tasks)

        # try to skip existing offers
        if self.use_signal:
            prune = self.comm['skipExisting']
        else:
            prune = InputUtil.input_yes_or_no('Skip existing offers?')
        if prune:
            self.__print_or_emit('\nPruning offer set...')
            try:
                exists = self.__get_existing_set(notice_date)
            except rq.exceptions.Timeout as ex:
                self.__print_or_emit(' ! FAILED to exec prune:', ex.__str__())
                self.__print_or_emit(' ! SKIPPED...')
            else:
                for i in range(len(banks) - 1, -1, -1):
                    if banks[i][0] not in exists: continue
                    exist = exists[banks[i][0]]
                    for j in range(5):
                        if not banks[i][j + 1] or not exist[j]: continue
                        if banks[i][j + 1] == exist[j]: banks[i][j + 1] = ''
                        # pass (!=) to overwrite different offers
                    if not any(banks[i][1:]): banks.pop(i)  # remove banks with 5 empty offer-values
                self.__print_or_emit('COMPLETE')

        # traverse and submit
        if self.use_signal:
            max_workers = self.comm['maxWorkers'] if self.comm['enableMultiThread'] else 1
        else:
            max_workers = InputUtil.input_max_workers()
        all_count = len(banks)
        if not self.use_signal: print(f'\n{"*" * 64}')
        self.__print_or_emit(f'\nStart to add {all_count} offers...')
        failed = []

        all_tasks = push_to_thread_pool(banks, max_workers)
        if self.use_signal:
            for i, done in enumerate(all_tasks, 1):
                bank, resp = done.result()
                self.cur_percent.emit(int(100 * i / all_count))
                if resp != '新增报价成功':
                    failed.append(f'{str(bank)}: {resp}')
                else:
                    self.new_log.emit(f'{bank[0]} - SUCCESS')
        else:
            try:
                all_tasks = tqdm(all_tasks, 'Processing', total=all_count, dynamic_ncols=True)
                for done in all_tasks:
                    bank, resp = done.result()
                    all_tasks.set_postfix_str(f'{bank[0]}: {resp}')
                    if resp != '新增报价成功': failed.append(f'{str(bank)}: {resp}')
            finally:
                all_tasks.close()
        return failed

    def __get_existing_set(self, notice_date: int) -> dict[str, list[str]]:
        ''' @return dict[str, list[str]] - dict of existing offers\n
        Pull info of all existing offers and convert it into a dict.
        '''
        payload = {
            'orgIssuerId': '',
            'noticeDate': notice_date,
            'sbjRtg': '',
            'startPrice': '',
            'endPrice': '',
            'startAssetSize': '',
            'endAssetSize': '',
            'provinceList': [],
            'nonBankSign': '',
            'openSign': ''
        }
        resp = self.__post(self.conf['offerList'], payload, timeout=5)
        offer_dict = {}
        for rg in resp['data']:
            for i, item in enumerate(rg['sbjRtgList']):
                for offer in item['offerDtlList']:
                    offer_dict.setdefault(offer['organizationShortName'], ['' for _ in range(5)])[i] = offer['refYield']
        return offer_dict

    def __get_bank_id(self, bank_name: str) -> str:
        ''' @return str - institution id of the bank\n
        An empty id means the bank has no id yet; `None` means cannot find
        a bank that exactly match the given string `bank_name`.
        '''
        payload = {'enqrVal': bank_name, 'pageNum': 1, 'pageSize': 10}
        resp = self.__post(self.conf['fuzzyQuery'], payload, timeout=5)
        for bank in resp['data']['list']:
            if bank['organizationShortName'] == bank_name:
                return bank.setdefault('issuerId', '')
        return None

    def __get_rank_by_id(self, bank_id: str) -> str:
        ''' @return str - corresponding rank of the institution id
        '''
        payload = {'institutionId': bank_id}
        resp = self.__post(self.conf['getRankById'], payload, timeout=5)
        return resp['data']

    def __submit_one_offer(self, bank_id: str, bank_rank: str, bank: list[str], notice_date: int) -> str:
        ''' @return str - message of this offer-submitting operation\n
        '''
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
        payload = {'noticeDate': notice_date, 'offerDtlList': []}
        for i, val in enumerate(bank[1:], 1):
            if not val: continue
            offer = template.copy()
            offer['issueTermNcd'] = str(i)
            offer['refYieldBulletin'] = val
            payload['offerDtlList'].append(offer)
        resp = self.__post(self.conf['addOffer'], payload, timeout=5)
        return resp['msg']

    def __post(self, suffix: str, json: dict, **kwargs) -> dict:
        ''' @return dict - json content of response\n
        A simple wrapper to make a POST request.\n
        If `timeout` is set, a `requests.exceptions.Timeout` exception may be raised
        when request keeps timing out and number of retries exceeds `trials`.
        '''
        timeout = kwargs.setdefault('timeout', None)
        trials = kwargs.setdefault('trials', 3) if timeout is not None else 1
        for i in range(1, 1 + trials):
            url = self.__make_url(suffix)
            try:
                resp = rq.post(url, json=json, timeout=timeout, headers=self.__make_header())
                return resp.json()
            except rq.exceptions.Timeout:
                if i == trials: raise
                continue
        return None

    def __make_header(self) -> dict[str, str]:
        ''' @return dict[str, str] - request headers\n
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
            'Referer': self.__make_url(self.conf['Referer']),
            'User-Agent': self.conf['User-Agent']
        }

    def __make_url(self, suffix: str) -> str:
        ''' @return str - join an url
        '''
        return f'{self.conf["Origin"]}/{suffix}'

    def __print_or_emit(self, *logs: object) -> None:
        ''' @return None\n
        Print `logs` to terminal if `use_signal` is `False`, otherwise
        send `logs` outside using signal `new_log`.
        '''
        if self.use_signal:
            self.new_log.emit(' '.join(logs).strip())
        else:
            print(*logs)


if __name__ == '__main__':
    pass
