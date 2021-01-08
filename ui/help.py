from util.const import Const

from ui.basic import BasicDialog


class AboutWindow(BasicDialog):
    ''' Define behaviour of help->about window.
    '''
    def __init__(self) -> None:
        super().__init__(Const.FILE_UI_ABOUT)


class AboutQtWindow(BasicDialog):
    ''' Define behaviour of help->about_qt window.
    '''
    def __init__(self) -> None:
        super().__init__(Const.FILE_UI_ABOUT_QT)


if __name__ == '__main__':
    pass
