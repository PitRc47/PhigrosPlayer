import platform

checksys = 'Linux'
if platform.system() == "Windows":
    checksys = 'Windows'
else:
    try:
        from kivy.utils import platform as kivy_platform
        if kivy_platform == 'android':
            checksys = 'Android'
    except:
        pass