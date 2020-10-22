import json
from typing import List


class JsonUtil:
    ''' A util class for dealing with load, save, convert on json
    '''
    @staticmethod
    def save(filename: str, data: List[str], sort_keys: bool = True):
        ''' @return None\n
        Just save `data` as a json file
        '''
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, sort_keys=sort_keys)

    @staticmethod
    def load(filename: str):
        ''' @return Object - object read from json\n
        Just load json files and return
        '''
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def convert_txt_to_json(src: str, dst: str, bmap: str = ''):
        ''' @return None\n
        Convert and re-arrange data stored in txt to json format. Using `bmap` as
        to correct some special bank names.
        '''
        # read lines as a list
        raw = open(src, 'r', encoding='utf-8').read().split('\n')
        bank_map = JsonUtil.load(bmap) if bmap else {}
        if not raw[-1]: raw.pop()
        # rearrange, in original layout
        data1, raw_n = [[] for _ in range(5)], 0
        for rg in enumerate(['AAA', 'AAA Others', 'AA+', 'AA']):  # 4 rank groups
            nums = input(f'Nums in rank group {rg}: ').split(' ')
            assert len(nums) == 5, 'invalid input'  # 1M, 3M, 6M, 9M, 1Y
            nums, j = [int(x) for x in nums], 0
            while sum(nums) > 0:
                if nums[j] > 0:
                    # some bank names need to be replaced
                    bank = raw[raw_n] if raw[raw_n] not in bank_map else bank_map[raw[raw_n]]
                    value = raw[raw_n + 1].rstrip('%')
                    data1[j].append((bank, value))
                    nums[j] -= 1
                    raw_n += 2
                j = (j + 1) % 5
        # check manually
        for d1 in data1:
            print(d1[:5])
        while True:
            answer = input('\nDoes data converting work right? (y/n): ')
            if answer.lower() == 'y': break
            if answer.lower() == 'n': exit(1)
        # from list to dict, by bank name
        data2 = dict()
        for i, col in enumerate(data1):
            for bank, value in col:
                data2.setdefault(bank, [''] * 5)[i] = value
        # from dict to list, for saving
        data3 = []
        for key in data2:
            data3.append([key, *data2[key]])
        # save it
        JsonUtil.save(dst, data3)
