import os

from ioutil import Utils
from submit import BondChain


def start():
    ''' @return None
    Start a submit execution.
    '''
    # decide paths and convert data to json
    src_text = Utils.input_path('plain-text', 'test/1.txt', True)
    dst_json = Utils.input_path('save converted Json', 'test/1.json')
    if not os.path.exists(src_text) and not os.path.exists(dst_json):
        print(f'\n ! CANNOT find or access any of:\n   - {src_text}\n   - {dst_json}')
    else:
        if os.path.exists(dst_json) and Utils.input_yes_or_no('Json already exists. Skip exec convertion?'):
            print(f'Skipped convertion. Using existing Json [{dst_json}] instead')
        else:
            # create or overwrite
            Utils.convert_txt_to_json(src_text, dst_json)
        # initialize
        bc = BondChain()
        # login
        bc.login()
        # load data from json
        data = Utils.load(dst_json)
        # traverse data and submit them
        failed = bc.add_offers(data)
        # print failed offers
        if not failed:
            print('\n* All Succeeded *')
        else:
            print(f'\n* Totally {len(failed)} fail(s):')
            for fail in failed:
                print(fail)
    # end
    input('\nPress any key to continue...')


if __name__ == '__main__':
    start()
