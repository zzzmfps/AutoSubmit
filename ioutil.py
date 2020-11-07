import json
import os
from typing import List


class Utils:
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
    def load(filename: str) -> dict:
        ''' @return dict - dict read from json\n
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
        bank_map = Utils.load('assets/bank_map.json')
        # rearrange, in original layout
        data1, raw_n = [[] for _ in range(5)], 0
        print('\nDivide text into blocks...')
        for rg in range(1, 5):  # 4 rank groups
            nums = input(f'Nums in rank group {rg} of each column (press enter to skip): ').split(' ')
            if len(nums) == 1 and nums[0] == '': continue
            assert len(nums) == 5, 'Invalid input'  # 1M, 3M, 6M, 9M, 1Y
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
        assert raw_n == len(raw), f'Convert failed: {(len(raw)-raw_n)>>1} items left not processed'
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
        Utils.save(dst, data3)

    @staticmethod
    def input_with_default(file_descr: str, default_path: str, require_exists: bool = True) -> str:
        ''' @return str - path that finally takes effect
        '''
        while True:
            val = input(f'Path to {file_descr} file: ')
            if not val: break
            if not require_exists or os.path.isfile(val): break
            print(f' * Given path [{val}] does not exist or cannot access, please try again')
        if not val:
            print(f' * Fall back to default path [{default_path}]')
            return default_path
        print(f' * Using [{val}] as path of {file_descr} file')
        return val

    @staticmethod
    def input_yes_or_no(descr: str) -> bool:
        ''' @return bool - decide with input
        '''
        print()
        while True:
            slt = input(f'{descr} (y/n): ').lower()
            if slt in ['y', 'yes']: return True
            if slt in ['n', 'no']: return False
        return None


if __name__ == "__main__":
    pass
