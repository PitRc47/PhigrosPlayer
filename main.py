from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import platform
import os

# 通用接口定义
class WebViewInterface:
    def load_url(self, url):
        raise NotImplementedError("This method should be overridden by platform-specific implementations.")

# PC端WebView实现（使用cefpython3）
class PCWebView(WebViewInterface):
    def __init__(self):
        # 导入cefpython3库
        import cefpython3.cefpython as cef
        settings = {}
        cef.Initialize(settings)
    
    def load_url(self, url):
        import cefpython3.cefpython as cef
        browser = cef.CreateBrowserSync(url=url)
        cef.MessageLoop()
        cef.Shutdown()

# Android端WebView实现（使用plyer）
class AndroidWebView(WebViewInterface):
    def __init__(self):
        from jnius import autoclass, cast
        from android.runnable import run_on_ui_thread

        self.WebView = autoclass('android.webkit.WebView')
        self.WebViewClient = autoclass('android.webkit.WebViewClient')
        self.activity = autoclass('org.kivy.android.PythonActivity').mActivity

    @run_on_ui_thread
    def load_url(self, url):
        webview = self.WebView(self.activity)
        webview.getSettings().setJavaScriptEnabled(True)
        wvc = self.WebViewClient()
        webview.setWebViewClient(wvc)
        self.activity.setContentView(webview)
        webview.loadUrl(url)

# 主应用类
class WebViewApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        # 根据平台选择WebView实现
        if platform.system() in ['Windows', 'Linux', 'Darwin']:
            self.webview = PCWebView()
        elif platform.system() == 'Java':
            # 检查是否在Android环境中运行
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                if PythonActivity.mActivity:
                    self.webview = AndroidWebView()
                else:
                    raise Exception("Not running on Android")
            except Exception as e:
                print(f"Error: {e}")
                return None
        else:
            return None

        button = Button(text="Load Website", on_release=self.load_website)
        layout.add_widget(button)
        return layout

    def load_website(self, instance):
        if hasattr(self, 'webview'):
            self.webview.load_url("https://www.example.com")

if __name__ == '__main__':
    # 确保在Android环境中运行时正确设置环境变量
    if platform.system() == 'Java':
        os.environ['KIVY_WINDOW'] = 'sdl2'
        os.environ['KIVY_BCM_DISPMANX_ID'] = '0'

    WebViewApp().run()