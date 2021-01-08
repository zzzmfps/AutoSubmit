from util.const import Const
from PySide2.QtCore import Signal
from util.data import JsonUtil

from ui.basic import BasicWidget


class CommonWindow(BasicWidget):
    ''' Define behaviour of config->common window.
    '''
    conf_status = Signal(bool, str, str)

    def __init__(self) -> None:
        super().__init__(Const.FILE_UI_COMMON)
        self.conf_path = Const.FILE_JSON_USER_CONF

    def set_handlers(self) -> None:
        self.win.enable_multi_thread.clicked.connect(self.__handle_enable_multi_thread)
        self.win.btn_save.clicked.connect(self.__handle_save)
        self.win.btn_cancel.clicked.connect(self.win.close)

    def set_init_values(self) -> None:
        try:
            self.user, self.comm = JsonUtil.load(self.conf_path)
            if not isinstance(self.user, dict) or not isinstance(self.comm, dict): raise TypeError
            self.conf_status.emit(True, self.conf_path, '')
        except Exception as ex:
            self.user = {
                Const.CONF_USERNAME: '',
                Const.CONF_PASSWORD: '',
                Const.CONF_LOGIN_TERMINAL: 10,
                Const.CONF_CARRY_ON: 1
            }
            self.comm = {Const.CONF_SKIP_EXISTING: False, Const.CONF_MULTI_THREAD: False, Const.CONF_MAX_WORKERS: 1}
            JsonUtil.save(self.conf_path, [self.user, self.comm])
            self.conf_status.emit(False, self.conf_path, ex.__str__())
        if self.user[Const.CONF_USERNAME]: self.win.username.setText(self.user[Const.CONF_USERNAME])
        if self.user[Const.CONF_PASSWORD]: self.win.password.setText(self.user[Const.CONF_PASSWORD])
        if self.comm[Const.CONF_SKIP_EXISTING]: self.win.skip_existing.click()
        if self.comm[Const.CONF_MULTI_THREAD]: self.win.enable_multi_thread.click()
        self.win.max_workers.setValue(self.comm[Const.CONF_MAX_WORKERS])

    # handlers
    def __handle_enable_multi_thread(self, enabled: bool) -> None:
        self.win.max_workers.setEnabled(enabled)

    def __handle_save(self) -> None:
        add_msg = []
        self.__update_and_msg(add_msg, self.user, Const.CONF_USERNAME, self.win.username.text())
        self.__update_and_msg(add_msg, self.user, Const.CONF_PASSWORD, self.win.password.text())
        self.__update_and_msg(add_msg, self.comm, Const.CONF_SKIP_EXISTING, self.win.skip_existing.isChecked())
        self.__update_and_msg(add_msg, self.comm, Const.CONF_MULTI_THREAD, self.win.enable_multi_thread.isChecked())
        self.__update_and_msg(add_msg, self.comm, Const.CONF_MAX_WORKERS, self.win.max_workers.value())
        if add_msg:
            JsonUtil.save(self.conf_path, [self.user, self.comm])
            self.conf_status.emit(True, self.conf_path, '; '.join(add_msg))
        self.win.close()

    # helpers
    def __update_and_msg(self, add_msg, origin_dict, field_name, new_value):
        if origin_dict[field_name] != new_value:
            add_msg.append(f'{field_name}: <i>{origin_dict[field_name]}</i> -> <i>{new_value}</i>')
            origin_dict[field_name] = new_value


if __name__ == '__main__':
    pass
