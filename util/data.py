import json
import os


class JsonUtil:
    ''' An utility class for json I/O operations.
    '''
    @staticmethod
    def save(filename: str, data: object, sort_keys: bool = True) -> None:
        ''' @return None\n
        Just save `data` as a json file.
        '''
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, sort_keys=sort_keys)

    @staticmethod
    def load(filename: str) -> object:
        ''' @return object - dict read from json\n
        Just load json files and return.
        '''
        if not os.path.exists(filename): return None
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def convert(src: str, dst: str, division: list[list[int]]) -> None:
        ''' @return None\n
        Convert and re-arrange data stored in txt to json format.
        Using `bank_map.json` to correct some special bank names.
        Use no keyboard input.
        '''
        def simple_preprocess(bank_name: str) -> str:
            bank_name = bank_name.strip('l|')
            if bank_name.endswith('千'): bank_name = bank_name[:-1] + '行'
            return bank_name

        # read lines as a list
        with open(src, 'r', encoding='utf-8') as f:
            raw = [line for line in f.read().split('\n') if line]
        assert len(raw) & 1 == 0, 'Number of data rows is NOT even'
        bank_map = JsonUtil.load('assets/json/bank_map.json')
        # rearrange, in original layout
        data1, raw_n = [[] for _ in range(5)], 0
        for rg in range(4):  # 4 rank groups
            nums, j = division[rg], 0
            while sum(nums) > 0:
                if nums[j] > 0:
                    # some bank names need to be replaced
                    recog = simple_preprocess(raw[raw_n])
                    bank = recog if recog not in bank_map else bank_map[recog]
                    value = raw[raw_n + 1].rstrip('0%')
                    data1[j].append((bank, value))
                    nums[j] -= 1
                    raw_n += 2
                j = (j + 1) % 5
        assert raw_n == len(raw), f'{(len(raw)-raw_n)>>1} items left not processed'
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


class ValidateUtil:
    ''' An utility class for file validation checks.
    '''
    @staticmethod
    def validate_txt(txt_path: str = '', content: list[str] = []) -> tuple[bool, str]:
        ''' @return tuple[bool, str] - (is_valid, description)\n
        Pass either `txt_path` or `content` to this method.
        Returned description may be error message if is_valid is `False`;
        Or it is data info that parsed from the txt file/content.
        '''
        if not txt_path and not content:
            return False, 'Expected something to validate, but got nothing'
        if txt_path and content:
            return False, 'Confused on which value to use, do not pass both two parameters'
        if txt_path:
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = [x for x in f.read().split('\n') if x]
        if len(content) & 1 != 0:
            return False, 'Number of lines must be even'
        char_set1 = set('1234567890.%')  # chars used and only used in offer values
        char_set2 = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')  # should not appear
        for i in range(0, len(content), 2):  # bank names
            if set(content[i]).intersection(char_set1.union(char_set2)):
                return False, f'Expected a bank name at significant line {i}, but got {content[i]}'
        for i in range(1, len(content), 2):  # offer values
            if not set(content[i]).issubset(char_set1):
                return False, f'Expected a offer value at significant line {i}, but got {content[i]}'
        return True, f'Found {len(content)>>1} offers'

    @staticmethod
    def validate_json(json_path: str) -> tuple[bool, str]:
        ''' @return tuple[bool, str] - (is_valid, description)\n
        Returned description may be error message if is_valid is `False`;
        Or it is data info that parsed from the json file.
        '''
        try:
            content = JsonUtil.load(json_path)
        except json.JSONDecodeError as ex:
            return False, ex.__str__()
        if not isinstance(content, list):
            return False, f'Expected type list[list[str]] of json, not {content.__class__}'
        count = 0
        for i, elem in enumerate(content, 1):
            if not isinstance(elem, list):
                return False, f'Expected type list[str] at {i}th element, not {elem.__class__}'
            if len(elem) != 6:
                return False, f'Expected length 6 of {i}th element, but got {len(elem)}'
            if elem[0] == '':
                return False, f'Expected a bank name at {i}th element, but got an empty string'
            for j in range(6):
                if not isinstance(elem[j], str):
                    return False, f'Expected type str of all values in {i}th element, not {elem[j].__class__}'
                if j > 0 and elem[j]: count += 1
        return True, f'{len(content)} bank(s), {count} offer(s)'


if __name__ == '__main__':
    pass
