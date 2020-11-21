import json
import os
import time


class Utils:
    ''' An utility class dealing with necessary I/O operations.
    '''
    @staticmethod
    def save(filename: str, data: list[str], sort_keys: bool = True):
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
            raw = [line for line in f.read().strip().split('\n') if line]
        assert len(raw) & 1 == 0, '数据的行数必须为偶数'
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
                    recog = Utils.__simple_preprocess(raw[raw_n])
                    bank = recog if recog not in bank_map else bank_map[recog]
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
    def input_path(file_descr: str, default_path: str, require_exists: bool = False) -> str:
        ''' @return str - path that finally takes effect
        '''
        print()
        while True:
            val = input(f'Path to {file_descr} file: ')
            if not val: break
            if not require_exists or os.path.isfile(val): break
            print(f' * Given path [{val}] does not exist or cannot access, please try again')
        if not val:
            print(f' * Falls back to default path [{default_path}]')
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
            if slt in ['y', 'yes', '']: return True
            if slt in ['n', 'no']: return False

    @staticmethod
    def input_offset() -> int:
        ''' @return int - milliseconds with offset
        '''
        print()
        while True:
            raw = input('Date offset (must NOT be positive): ')
            if not raw:
                print(' * Falls back to default value [0 | today]')
                return 1000 * int(time.time())
            elif raw == '0' or raw.startswith('-') and raw[1:].isdecimal():
                offset = int(raw)
                sec = int(time.time()) + 86400 * offset
                print(f' * Offset set to [{offset} | {time.ctime(sec)}]')
                return 1000 * sec

    @staticmethod
    def __simple_preprocess(bank_name: str) -> str:
        ''' @return str - revised bank name
        Deal with some simple errors in recognization.
        '''
        bank_name = bank_name.strip('l|')
        if bank_name.endswith('千'): bank_name = bank_name[:-1] + '行'
        return bank_name


if __name__ == "__main__":
    pass
