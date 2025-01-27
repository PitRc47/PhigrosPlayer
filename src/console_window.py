import checksys

if checksys.main == 'Windows':
    from ctypes import windll

    ConsoleWindowHwnd = windll.kernel32.GetConsoleWindow()

    def Hide():
        if ConsoleWindowHwnd != 0:
            windll.user32.ShowWindow(ConsoleWindowHwnd, 0)

    def Show():
        if ConsoleWindowHwnd != 0:
            windll.user32.ShowWindow(ConsoleWindowHwnd, 1)

else:
    def Hide():
        pass
    
    def Show():
        pass