import os
import sys
import subprocess
import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from qfluentwidgets import FluentWindow, NavigationItemPosition, NavigationAvatarWidget
from qfluentwidgets import FluentIcon
from qfluentwidgets import CheckBox, LineEdit, PrimaryPushButton, PushButton, Dialog, SplashScreen

import const

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.splash = SplashScreen(self.windowIcon(), self)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle("Phigros Player GUI Launcher")
        self.splash.raise_()
        self.show()
        self.initNav()
        self.initWindow()
        self.splash.finish()
        
    def initWindow(self):
        self.resize(1000, 800)
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(int((w - self.width()) / 2), int((h - self.height()) / 2))

    def initNav(self):
        self.startup = SettingsWindow()
        self.addSubInterface(self.startup, FluentIcon.HOME, "Startup")
        self.navigationInterface.addWidget(
            routeKey = "avatar",
            widget = NavigationAvatarWidget("Github Repository", "icon.ico"),
            onClick = lambda: webbrowser.open(const.REPO_URL),
            position = NavigationItemPosition.BOTTOM
        )
        self.navigationInterface.setExpandWidth(280)

class SettingsWindow(QWidget):
    chart = ""
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def openFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)", options=options)
        self.chart = fileName if fileName else ""
        return self.chart

    def messagebox_when_render_up(self):
        self.MessageBox1 = Dialog("注意", "要开始渲染谱面了，启动器可能会未响应。如果Windows弹出了未响应窗口，请无视。否则渲染和启动器一块闪退").exec_()
        
    def messagebox_when_render_off(self):
        self.MessageBox2 = Dialog("渲染结束", "渲染结束，请自行查看渲染结果。如遇到视频损坏或有改进建议，欢迎点击侧边栏的Github Repository来向qaqFei。(当然gui有问题来抽IrCat-Ninth位于natayark@outlook.com)").exec_()
  
    def render_chart(self):
        self.messagebox_when_render_up()
        check = lambda checkbox, command: command if checkbox.isChecked() else ""
        command = []
        command.append("main.exe" if os.path.isfile("main.exe") else "python main.py")
        
        if self.chart:
            command.append(self.chart)
        else:
            phira_id = self.phiraChartID.text().strip()
            command.extend(("--phira-chart", phira_id)) if phira_id else ""

        options = [
            check(self.low_quality, "--lowquality"),
            check(self.showFps, "--showfps"),
            check(self.moreRenderRange, "--render-range-more"),
            check(self.noautoplay, "--noautoplay"),
            check(self.loop, "--loop"),
            check(self.rtacc, "--rtacc"),
            check(self.checkBox_9, "--noclicksound"),
            check(self.checkBox_11, "--fullscreen"),
            check(self.checkBox_3, "--enable-jscanvas-bitmap"),
            check(self.checkBox_8, "--frameless"),
            f"--combotips {self.comboTip.text()}" if self.comboTip.text() else "",
            check(self.debug, "--debug"),
            check(self.hideConsle, "--hideconsle"),
            check(self.enableJsLog, "--enable-jslog"),
            check(self.nocleartmp, "--no-cleartemp"),
            check(self.enable_JIT, "ENABLE_JIT"),
            f"--rpe-texture-scalemethod {self.rpe_texture.text()}" if self.rpe_texture.text() else "",
            f"--lowquality-scale {self.lq_imjscale_x.text()}" if self.lq_imjscale_x.text() else "",
            f"--size {self.size_x.text()} {self.size_y.text()}" if self.size_x.text() or self.size_y.text() else "",
            self.own_argu.text()
        ]
        command.extend(filter(None, options))

        try:
            print(f"调用的命令 (出现错误的时候可以看看是不是命令出错了，是的话来抽IrCat-Ninth): {command}")
            subprocess.run(" ".join(map(lambda x: f"\"{x}\"", command)), shell=True, check=True)
        except subprocess.CalledProcessError as e:
            Dialog("错误", f"命令执行失败: {repr(e)}", self).exec()
        finally:
            self.messagebox_when_render_off()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        MainWindow.resize(974, 601)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 100, 571, 81))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.chooseFile = PushButton(self.groupBox)
        self.chooseFile.setGeometry(QtCore.QRect(10, 30, 181, 31))
        self.chooseFile.setObjectName("chooseFile")
        self.chooseFile.clicked.connect(self.openFile)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(210, 40, 54, 12))
        self.label.setObjectName("label")
        self.phiraChartID = LineEdit(self.groupBox)
        self.phiraChartID.setGeometry(QtCore.QRect(250, 30, 191, 31))
        self.phiraChartID.setObjectName("phiraChartID")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 449, 941, 91))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.pushButton_2 = PrimaryPushButton(self.groupBox_3)
        self.pushButton_2.setGeometry(QtCore.QRect(430, 10, 151, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(lambda: self.render_chart())
        self.render = CheckBox(self.groupBox_3)
        self.render.setGeometry(QtCore.QRect(430, 50, 271, 16))
        self.render.setObjectName("render")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(70, 10, 771, 81))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(36)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 180, 571, 271))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.scrollArea = QtWidgets.QScrollArea(self.groupBox_2)
        self.scrollArea.setGeometry(QtCore.QRect(10, 20, 541, 241))
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 522, 239))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.comboTip = LineEdit(self.scrollAreaWidgetContents)
        self.comboTip.setGeometry(QtCore.QRect(210, 10, 311, 20))
        self.comboTip.setClearButtonEnabled(True)
        self.comboTip.setObjectName("comboTip")
        self.low_quality = CheckBox(self.scrollAreaWidgetContents)
        self.low_quality.setGeometry(QtCore.QRect(10, 10, 301, 16))
        self.low_quality.setObjectName("low_quality")
        self.showFps = CheckBox(self.scrollAreaWidgetContents)
        self.showFps.setGeometry(QtCore.QRect(10, 50, 341, 16))
        self.showFps.setObjectName("showFps")
        self.moreRenderRange = CheckBox(self.scrollAreaWidgetContents)
        self.moreRenderRange.setGeometry(QtCore.QRect(180, 50, 111, 16))
        self.moreRenderRange.setObjectName("moreRenderRange")
        self.checkBox_9 = CheckBox(self.scrollAreaWidgetContents)
        self.checkBox_9.setGeometry(QtCore.QRect(10, 120, 121, 16))
        self.checkBox_9.setObjectName("checkBox_9")
        self.hideConsle = CheckBox(self.scrollAreaWidgetContents)
        self.hideConsle.setGeometry(QtCore.QRect(10, 200, 151, 16))
        self.hideConsle.setObjectName("hideConsle")
        self.loop = CheckBox(self.scrollAreaWidgetContents)
        self.loop.setGeometry(QtCore.QRect(380, 50, 71, 16))
        self.loop.setObjectName("loop")
        self.checkBox_3 = CheckBox(self.scrollAreaWidgetContents)
        self.checkBox_3.setGeometry(QtCore.QRect(280, 120, 201, 16))
        self.checkBox_3.setObjectName("checkBox_3")
        self.noautoplay = CheckBox(self.scrollAreaWidgetContents)
        self.noautoplay.setGeometry(QtCore.QRect(10, 80, 271, 16))
        self.noautoplay.setObjectName("noautoplay")
        self.rtacc = CheckBox(self.scrollAreaWidgetContents)
        self.rtacc.setGeometry(QtCore.QRect(280, 80, 121, 16))
        self.rtacc.setObjectName("rtacc")
        self.checkBox_11 = CheckBox(self.scrollAreaWidgetContents)
        self.checkBox_11.setGeometry(QtCore.QRect(140, 120, 71, 16))
        self.checkBox_11.setObjectName("checkBox_11")
        self.debug = CheckBox(self.scrollAreaWidgetContents)
        self.debug.setGeometry(QtCore.QRect(190, 160, 151, 16))
        self.debug.setAutoFillBackground(True)
        self.debug.setObjectName("debug")
        self.checkBox_8 = CheckBox(self.scrollAreaWidgetContents)
        self.checkBox_8.setGeometry(QtCore.QRect(10, 160, 141, 16))
        self.checkBox_8.setObjectName("checkBox_8")
        self.enableJsLog = CheckBox(self.scrollAreaWidgetContents)
        self.enableJsLog.setGeometry(QtCore.QRect(160, 200, 131, 16))
        self.enableJsLog.setObjectName("enableJsLog")
        self.nocleartmp = CheckBox(self.scrollAreaWidgetContents)
        self.nocleartmp.setGeometry(QtCore.QRect(290, 200, 171, 16))
        self.nocleartmp.setObjectName("nocleartmp")
        self.verticalWidget = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.verticalWidget.setGeometry(QtCore.QRect(350, 120, 171, 381))
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox_2 = QtWidgets.QCheckBox(self.verticalWidget)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout.addWidget(self.checkBox_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(590, 90, 361, 361))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox_4.setFont(font)
        self.groupBox_4.setObjectName("groupBox_4")
        self.scrollArea_3 = QtWidgets.QScrollArea(self.groupBox_4)
        self.scrollArea_3.setGeometry(QtCore.QRect(10, 20, 341, 331))
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName("scrollArea_3")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 339, 329))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.label_5 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        self.label_5.setGeometry(QtCore.QRect(10, 10, 271, 16))
        self.label_5.setObjectName("label_5")
        self.enable_JIT = CheckBox(self.scrollAreaWidgetContents_3)
        self.enable_JIT.setGeometry(QtCore.QRect(10, 40, 131, 16))
        self.enable_JIT.setObjectName("enable_JIT")
        self.own_argu = LineEdit(self.scrollAreaWidgetContents_3)
        self.own_argu.setGeometry(QtCore.QRect(10, 290, 271, 20))
        self.own_argu.setObjectName("own_argu")
        self.label_6 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        self.label_6.setGeometry(QtCore.QRect(10, 230, 271, 41))
        self.label_6.setObjectName("label_6")
        self.rpe_texture = LineEdit(self.scrollAreaWidgetContents_3)
        self.rpe_texture.setGeometry(QtCore.QRect(10, 70, 311, 20))
        self.rpe_texture.setText("")
        self.rpe_texture.setObjectName("rpe_texture")
        self.lq_imjscale_x = LineEdit(self.scrollAreaWidgetContents_3)
        self.lq_imjscale_x.setGeometry(QtCore.QRect(10, 110, 311, 20))
        self.lq_imjscale_x.setObjectName("lq_imjscale_x")
        self.groupBox_5 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_3)
        self.groupBox_5.setGeometry(QtCore.QRect(10, 140, 321, 61))
        self.groupBox_5.setObjectName("groupBox_5")
        self.size_x = LineEdit(self.groupBox_5)
        self.size_x.setGeometry(QtCore.QRect(10, 20, 101, 31))
        self.size_x.setText("")
        self.size_x.setObjectName("size_x")
        self.size_y = LineEdit(self.groupBox_5)
        self.size_y.setGeometry(QtCore.QRect(170, 20, 121, 31))
        self.size_y.setObjectName("size_y")
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)
        # self.setCentralWidget(self.centralwidget)
        # self.menubar = QtWidgets.QMenuBar(MainWindow)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 974, 23))
        # self.menubar.setObjectName("menubar")
        # self.menuGithub_Repository = QtWidgets.QMenu(self.menubar)
        # #self.menuGithub_Repository.setObjectName("menuGithub_Repository")
        # MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        # MainWindow.setStatusBar(self.statusbar)
        # self.menubar.addAction(self.menuGithub_Repository.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Launcher"))
        self.groupBox.setTitle(_translate("MainWindow", "谱面文件"))
        self.chooseFile.setText(_translate("MainWindow", "在电脑上选择一个文件"))
        self.label.setText(_translate("MainWindow", "或者"))
        self.phiraChartID.setPlaceholderText(_translate("MainWindow", "输入一个Phira谱面ID"))
        self.groupBox_3.setTitle(_translate("MainWindow", "渲染"))
        self.pushButton_2.setText(_translate("MainWindow", "开始渲染！"))
        self.render.setText(_translate("MainWindow", "将渲染结果保存为视频"))
        self.label_2.setText(_translate("MainWindow", "Phigros Player GUI Launcher"))
        self.groupBox_2.setTitle(_translate("MainWindow", "渲染设置"))
        self.comboTip.setPlaceholderText(_translate("MainWindow", "COMBO文字，不填为AUTOPLAY"))
        self.low_quality.setText(_translate("MainWindow", "低分辨率"))
        self.showFps.setText(_translate("MainWindow", "显示帧率"))
        self.moreRenderRange.setText(_translate("MainWindow", "更多的渲染范围"))
        self.checkBox_9.setText(_translate("MainWindow", "无点击音效"))
        self.hideConsle.setText(_translate("MainWindow", "隐藏控制台窗口"))
        self.loop.setText(_translate("MainWindow", "循环谱面"))
        self.checkBox_3.setText(_translate("MainWindow", "启用渲染时的 BitmapImage"))
        self.noautoplay.setText(_translate("MainWindow", "禁用奥托普雷先生（Autoplay）"))
        self.rtacc.setText(_translate("MainWindow", "显示实时准度"))
        self.checkBox_11.setText(_translate("MainWindow", "全屏窗口"))
        self.debug.setText(_translate("MainWindow", "显示Webview调试窗"))
        self.checkBox_8.setText(_translate("MainWindow", "无边框窗口"))
        self.enableJsLog.setText(_translate("MainWindow", "保留渲染Js"))
        self.nocleartmp.setText(_translate("MainWindow", "不清理临时文件"))
        self.checkBox_2.setText(_translate("MainWindow", "CheckBox"))
        self.groupBox_4.setTitle(_translate("MainWindow", "高级选项"))
        self.label_5.setText(_translate("MainWindow", "如果不是真的会用，我建议你别动。"))
        self.enable_JIT.setText(_translate("MainWindow", "启用JIT(不建议）"))
        self.label_6.setText(_translate("MainWindow", "使用自己的命令行参数：我们稍后会将其添加到控制台。"))
        self.rpe_texture.setPlaceholderText(_translate("MainWindow", "设置RPE谱面纹理缩放方法"))
        self.lq_imjscale_x.setPlaceholderText(_translate("MainWindow", "设置低画质渲染缩放"))
        self.groupBox_5.setTitle(_translate("MainWindow", "窗口大小"))
        self.size_x.setPlaceholderText(_translate("MainWindow", "长"))
        self.size_y.setPlaceholderText(_translate("MainWindow", "宽"))
        
QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()
