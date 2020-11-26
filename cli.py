import os

from util.data import JsonUtil, InputUtil
from util.request import RequestUtil

if __name__ == '__main__':
    ''' exec as cli
    '''
    src_text = InputUtil.input_path('plain-text', 'test/1.txt', True)
    dst_json = InputUtil.input_path('save converted Json', 'test/1.json')
    if not os.path.exists(src_text) and not os.path.exists(dst_json):
        print(f'\n ! CANNOT find or access any of:\n   - {src_text}\n   - {dst_json}')
    else:
        if os.path.exists(dst_json) and InputUtil.input_yes_or_no('Json already exists. Skip exec convertion?'):
            print(f'Skipped convertion. Using existing Json [{dst_json}] instead')
        else:
            JsonUtil.convert(src_text, dst_json)
        bc = RequestUtil()
        bc.login()
        data = JsonUtil.load(dst_json)
        failed = bc.add_offers(data)
        if not failed:
            print('\n* All Succeeded *')
        else:
            print(f'\n* Totally {len(failed)} fail(s):')
            for fail in failed:
                print(fail)
    input('\nPress any key to continue...')
