import checksys

if checksys.main != 'Android':
    import sys
    import threading
    import traceback
    import time
    import os.path

    def excepthook(etype, value, tb):
        try:
            
            if isinstance(etype, KeyboardInterrupt) or KeyboardInterrupt in etype.mro():
                print("^C")
                sys.exit(0)
            
            errortext = "".join(traceback.format_exception(etype, value, tb))
            
            print(errortext, end="")
            
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            
            messagebox.showerror(
                "PhigrosPlayer 发生错误",
                f"很抱歉, PhigrosPlayer 发生了错误\n\n{errortext}\n\n请将错误信息发送给开发者以获得帮助\nhttps://github.com/qaqFei/PhigrosPlayer"
            )
            root.destroy()
            
            sys.exit(0)
        except (Exception, KeyboardInterrupt) as e:
            print(e)
            sys.exit(0)

    sys.excepthook = excepthook
    threading.excepthook = lambda x: excepthook(x.exc_type, x.exc_value, x.exc_traceback)