class Const:
    ''' A utility class contains neccessary constants.
    '''
    # field
    LOCAL = 'local'
    NETWORK = 'network'

    # log levels
    LOG_INFO = 'INFO'
    LOG_INFO_COLOR = 'green'
    LOG_WARN = 'WARN'
    LOG_WARN_COLOR = 'orange'
    LOG_ERRO = 'ERRO'
    LOG_ERRO_COLOR = 'red'

    # user config
    CONF_USERNAME = 'loginName'
    CONF_PASSWORD = 'loginPassword'
    CONF_LOGIN_TERMINAL = 'loginTerminalType'
    CONF_CARRY_ON = 'isCarryOn'

    # common config
    CONF_SKIP_EXISTING = 'skipExisting'
    CONF_MULTI_THREAD = 'enableMultiThread'
    CONF_MAX_WORKERS = 'maxWorkers'

    # json files
    FILE_JSON_BANK_MAP = 'assets/json/bank_map.json'
    FILE_JSON_BANK_RANK = 'assets/json/bank_rank.json'
    FILE_JSON_URL_RULE = 'assets/json/url.json'
    FILE_JSON_USER_CONF = 'assets/json/user.json'

    # ui files
    FILE_UI_MAIN = 'assets/ui/main.ui'
    FILE_UI_JUMP = 'assets/ui/jump.ui'
    FILE_UI_CREATE = 'assets/ui/create.ui'
    FILE_UI_CONVERT = 'assets/ui/convert.ui'
    FILE_UI_QUIT = 'assets/ui/quit.ui'
    FILE_UI_ABOUT = 'assets/ui/about.ui'
    FILE_UI_ABOUT_QT = 'assets/ui/about_qt.ui'
    FILE_UI_COMMON = 'assets/ui/common.ui'
