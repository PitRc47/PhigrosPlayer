import platform

main = 'Linux'
if platform.system() == "Windows":
    main = 'Windows'
else:
    try:
        from kivy.utils import platform as kivy_platform
        if kivy_platform == 'android':
            main = 'Android'
    except:
        pass