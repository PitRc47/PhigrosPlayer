import webview

if __name__ == '__main__':
    # 设置允许文件下载（如果需要）
    # 创建并显示一个 WebView 窗口
    webview.create_window('My PyWebView App', 'https://www.example.com')
    webview.start()