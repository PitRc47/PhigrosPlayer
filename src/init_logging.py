from checksys import checksys

if checksys != 'Android':
    import logging

    import webview.http

    logging.basicConfig(
        level = logging.INFO,
        format = "[%(asctime)s] %(levelname)s %(filename)s %(funcName)s: %(message)s",
        datefmt = "%H:%M:%S"
    )
    logging.getLogger("pywebview").disabled = True

    _wvsvStart = webview.http.BottleServer.start_server
    webview.http.BottleServer.start_server = lambda *args, **kwargs: (
        globals().update({"__dbg": webview._settings["debug"]}),
        webview._settings.update({"debug": False}),
        _wvsvStart(*args, **kwargs),
        webview._settings.update({"debug": globals()["__dbg"]}),
        globals().pop("__dbg")
    )[2]