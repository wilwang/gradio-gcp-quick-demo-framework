class StateBag:
    def __init__(self, 
                active_tab: str | None = "", 
                ocr_text: str | None = "", 
                engine_id: str | None = "", 
                project_id: str | None = ""):
        self._active_tab = active_tab
        self._ocr_text = ocr_text
        self._engine_id = engine_id
        self._project_id = project_id

    @property
    def active_tab(self):
        return self._active_tab

    @active_tab.setter
    def active_tab(self, value: str):
        print(f"set active_tab to {value}")
        self._active_tab = value

    @property
    def ocr_text(self):
        return self._ocr_text

    @ocr_text.setter
    def ocr_text(self, value: str):
        print(f"set ocr_text to {value}")
        self._ocr_text = value

    @property
    def engine_id(self):
        return self._engine_id

    @engine_id.setter
    def engine_id(self, value: str):
        print(f"set engine_id to {value}")
        self._engine_id = value

    @property
    def project_id(self):
        return self._project_id

    @project_id.setter
    def project_id(self, value: str):
        print(f"set project_id to {value}")
        self._project_id = value        
