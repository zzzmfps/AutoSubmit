import json
import os
from typing import List, Dict


class JsonUtil:
    ''' A util class for dealing with load, save and convert on json.
    '''
    @staticmethod
    def save(filename: str, data: List[str], sort_keys: bool = True):
        ''' @return None\n
        Just save `data` as a json file.
        '''
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, sort_keys=sort_keys)

    @staticmethod
    def load(filename: str) -> Dict[object]:
        ''' @return Dict[object] - dict read from json\n
        Just load json files and return.
        '''
        if not os.path.exists(filename): return {}
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def convert_txt_to_json(src: str, dst: str):
        ''' @return None\n
        Convert and re-arrange data stored in txt to json format.
        Using `bank_map.json` to correct some special bank names.
        '''
        # read lines as a list
        with open(src, 'r', encoding='utf-8') as f:
            raw = f.read().strip().split('\n')
        bank_map = JsonUtil.load('assets/bank_map.json')
        # rearrange, in original layout
        data1, raw_n = [[] for _ in range(5)], 0
        for rg in range(1, 5):  # 4 rank groups
            nums = input(f'Nums in rank group {rg} (press enter to skip): ').split(' ')
            if len(nums) == 1 and nums[0] == '': continue
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
        assert raw_n == len(raw), f'convert failed: {(len(raw)-raw_n)>>1} items left not processed'
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


if __name__ == "__main__":
    pass
