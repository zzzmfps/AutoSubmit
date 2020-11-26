from ui.basic import BasicDialog


class AboutWindow(BasicDialog):
    ''' Define behaviour of help->about window.
    '''
    def __init__(self) -> None:
        super().__init__()
        self.ui_path = 'assets/ui/about.ui'


class AboutQtWindow(BasicDialog):
    ''' Define behaviour of help->about_qt window.
    '''
    def __init__(self) -> None:
        super().__init__()
        self.ui_path = 'assets/ui/about_qt.ui'


if __name__ == "__main__":
    pass
