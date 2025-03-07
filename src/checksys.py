import platform

checksys = 'Linux'
if platform.system() == "Windows":
    checksys = 'Windows'
else:
    try:
        checksys = 'Android'
    except:
        pass