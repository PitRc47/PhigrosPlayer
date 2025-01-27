import webview
import webcv

root = webcv.WebCanvas(
    width = 1, height = 1,
    x = 0, y = 0,
    title = "PhigrosPlayer - Simulator",
    debug = True,
    resizable = False,
    frameless = False,
    renderdemand = False,
    renderasync = False,
    jslog = True,
    jslog_path = "./ppr-jslog-nofmt.js"
)
while True:
    root.run_js_code("console.log('Hello, World!');")