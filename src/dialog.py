import checksys

if checksys.main != 'Android':
    import tkinter as tk
    from tkinter import filedialog

    def _base_dialog(
        bFileOpen: bool,
        Filter: str = "",
        fn: str = ""
    ) -> str:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口

        if bFileOpen:
            options = {
                'title': 'Open File',
                'filetypes': [(filter_desc, filter_pattern) for filter_desc, filter_pattern in [tuple(f.split('|')) for f in Filter.split(';')]],
                'initialfile': fn
            }
            path = filedialog.askopenfilename(**options)
        else:
            options = {
                'title': 'Save File',
                'filetypes': [(filter_desc, filter_pattern) for filter_desc, filter_pattern in [tuple(f.split('|')) for f in Filter.split(';')]],
                'initialfile': fn
            }
            path = filedialog.asksaveasfilename(**options)

        root.destroy()
        return path

else:
    import os
    import sys
    from jnius import autoclass # type: ignore
    from android import activity # type: ignore
    from android.permissions import request_permissions, Permission # type: ignore

    def _base_dialog(
        bFileOpen: bool,
        Filter: str = "",
        fn: str = ""
    ) -> str:
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

        if bFileOpen:
            intent = activity.chooseFile(Filter)
            result = activity.startActivityForResult(intent)
            if result:
                return result[0]
        else:
            intent = activity.chooseDirectory()
            result = activity.startActivityForResult(intent)
            if result:
                return os.path.join(result[0], fn)

        return ""

def openfile(**kwargs) -> str:
    return _base_dialog(True, **kwargs)

def savefile(**kwargs) -> str:
    return _base_dialog(False, **kwargs)
