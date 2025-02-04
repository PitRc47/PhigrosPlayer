# -*- coding: utf-8 -*-


import os
import tkinter as tk
import tkinter.messagebox as tkmsgbox
#我也不知道我为什么要用tkinter，谁知道呢（笑


from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QApplication,QFileDialog


from PyQt5.QtCore import QUrl,Qt

from PyQt5.QtGui import QDesktopServices,QIcon

from functools import partial

from qfluentwidgets import FluentWindow,NavigationItemPosition,NavigationAvatarWidget

from qfluentwidgets import FluentIcon as FIF


from qfluentwidgets import CheckBox, LineEdit, PrimaryPushButton, PushButton,Dialog,SplashScreen


class mainw(FluentWindow):
    def openrespository(self):
        url = "https://github.com/qaqfei/PhigrosPlayer"
        QDesktopServices.openUrl(QUrl(url))
    def initWindow(self):
        self.resize(1000,600)
    

       

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)



    def __init__(self):
        super().__init__()
        self.splash = SplashScreen(self.windowIcon(),self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint | Qt.CustomizeWindowHint)
        self.resize(800,600)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle("Phigros Player GUI Launcher")
        self.splash.raise_()
        self.show()

        self.initNav()
        self.initWindow()


        self.splash.finish()

    def initNav(self):
        
        self.startup = Ui_MainWindow()
        self.addSubInterface(self.startup, FIF.HOME ,"Startup")
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget('Github Repository','icon.ico'),
            onClick=self.openrespository,
            position=NavigationItemPosition.BOTTOM,
        )
        self.navigationInterface.setExpandWidth(280)




class Ui_MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        
    def openFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)", options=options)
        if fileName:
            print(f"选择的文件：{fileName}")
            self.chart = fileName
            return fileName
        else:
            return ""

    def messagebox_when_render_up(self):
        tkmsgbox.showwarning("注意", "我们亲爱的qaqFei要开始为你渲染谱面了，启动器可能会未响应，但你千万别去动他，要是不小心关掉了那你刚才渲染的谱面就全部没有啦！")
        #w = Dialog("注意", "我们亲爱的qaqFei要开始为你渲染谱面了，启动器可能会未响应，但你千万别去动他，要是不小心关掉了那你刚才渲染的谱面就全部没有啦！", self)
            

    def messagebox_when_render_off(self):
        tkmsgbox.showinfo("哦呼！", "渲染结束了！如果渲染了谱面那就赶快看看吧！如果损坏欢迎来GitHub给qaqFei提Issue!(当然我不知道qaqFei会怎么想，可能他看到这段文字会删掉的吧)")
        #w = Dialog("哦呼", "渲染结束了！如果渲染了谱面那就赶快看看吧！如果损坏欢迎来GitHub给我提Issue!", self)



    def run(self, checkbox,command):
        if checkbox.isChecked():
            return command
        else:
            return ""
    def render(self,run):
        self.combotips = self.lineEdit.text()
        self.messagebox_when_render_up()
        command1 =run(self.checkBox," --lowquality")
        command2 = run(self.checkBox_2," --showfps")
        command3 = run(self.checkBox_3," --enable-jscanvas-bitmap")
        command4 = run(self.checkBox_4," --debug")
        command5 = run(self.checkBox_6," --render-range-more")
        #command6 = run(self.checkBox_5,"  --lfdaot --lfdaot-file --lfdaot-render-video")
        command7 = run(self.checkBox_7," --noautoplay")
        command8 = run(self.checkBox_8," --frameless")
        command9 = run(self.checkBox_9," --noclicksound")
        command10 = run(self.checkBox_10," --loop")
        command11 = run(self.checkBox_11," --fullscreen")
        command13 = " --combotips "+ self.combotips if self.combotips else ""
        command14 = " "+self.lineEdit_3.text()
        if self.chart:
            command12 = " \""+self.chart+"\""
        else:
            command12 = " --phira-chart "+ self.lineEdit_2.text()
        command = "py main.py" +command12+command1+command2+command3+command4+command5+command7+command8+command9+command10+command11+command13+command14
        print(command)
        os.system(command)
        self.messagebox_when_render_off()
    
    def openrespository(self):
        url = "https://github.com/qaqfei/PhigrosPlayer"
        QDesktopServices.openUrl(QUrl(url))


    def setupUi(self, MainWindow):
        self.chart = None
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 100, 471, 81))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.pushButton = PushButton(self.groupBox)
        self.pushButton.setGeometry(QtCore.QRect(10, 30, 181, 31))
        self.pushButton.setObjectName("pushButton")
        chart = self.pushButton.clicked.connect(self.openFile)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(210, 40, 54, 12))
        self.label.setObjectName("label")
        chart = self.lineEdit_2 = LineEdit(self.groupBox)
        self.lineEdit_2.setGeometry(QtCore.QRect(250, 30, 191, 31))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 180, 471, 251))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.checkBox = CheckBox(self.groupBox_2)
        self.checkBox.setGeometry(QtCore.QRect(20, 20, 301, 16))
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = CheckBox(self.groupBox_2)
        self.checkBox_2.setGeometry(QtCore.QRect(20, 60, 341, 16))
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_3 = CheckBox(self.groupBox_2)
        self.checkBox_3.setGeometry(QtCore.QRect(140, 60, 201, 16))
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_4 = CheckBox(self.groupBox_2)
        self.checkBox_4.setGeometry(QtCore.QRect(320, 100, 151, 16))
        self.checkBox_4.setAutoFillBackground(True)
        self.checkBox_4.setObjectName("checkBox_4")
        self.lineEdit = LineEdit(self.groupBox_2)
        self.lineEdit.setGeometry(QtCore.QRect(140, 20, 311, 20))
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setObjectName("lineEdit")
        self.checkBox_6 = CheckBox(self.groupBox_2)
        self.checkBox_6.setGeometry(QtCore.QRect(20, 100, 111, 16))
        self.checkBox_6.setObjectName("checkBox_6")
        self.checkBox_7 = CheckBox(self.groupBox_2)
        self.checkBox_7.setGeometry(QtCore.QRect(140, 100, 271, 16))
        self.checkBox_7.setObjectName("checkBox_7")
        self.checkBox_8 = CheckBox(self.groupBox_2)
        self.checkBox_8.setGeometry(QtCore.QRect(320, 60, 141, 16))
        self.checkBox_8.setObjectName("checkBox_8")
        self.checkBox_9 = CheckBox(self.groupBox_2)
        self.checkBox_9.setGeometry(QtCore.QRect(20, 140, 121, 16))
        self.checkBox_9.setObjectName("checkBox_9")
        self.checkBox_10 = CheckBox(self.groupBox_2)
        self.checkBox_10.setGeometry(QtCore.QRect(140, 140, 71, 16))
        self.checkBox_10.setObjectName("checkBox_10")
        self.checkBox_11 = CheckBox(self.groupBox_2)
        self.checkBox_11.setGeometry(QtCore.QRect(230, 140, 71, 16))
        self.checkBox_11.setObjectName("checkBox_11")
        self.checkBox_12 = CheckBox(self.groupBox_2)
        self.checkBox_12.setGeometry(QtCore.QRect(320, 140, 121, 16))
        self.checkBox_12.setObjectName("checkBox_12")
        self.checkBox_13 = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox_13.setGeometry(QtCore.QRect(20, 180, 71, 16))
        self.checkBox_13.setObjectName("checkBox_13")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 460, 771, 80))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.pushButton_2 = PrimaryPushButton(self.groupBox_3)
        self.pushButton_2.setGeometry(QtCore.QRect(300, 20, 151, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(partial(self.render, self.run))

        self.checkBox_5 = CheckBox(self.groupBox_3)
        self.checkBox_5.setGeometry(QtCore.QRect(300, 50, 271, 16))
        self.checkBox_5.setObjectName("checkBox_5")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(70, 10, 771, 81))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(36)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(490, 100, 291, 331))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        self.groupBox_4.setFont(font)
        self.groupBox_4.setObjectName("groupBox_4")
        self.label_3 = QtWidgets.QLabel(self.groupBox_4)
        self.label_3.setGeometry(QtCore.QRect(10, 20, 271, 16))
        self.label_3.setObjectName("label_3")
        self.lineEdit_3 = LineEdit(self.groupBox_4)
        self.lineEdit_3.setGeometry(QtCore.QRect(10, 290, 271, 20))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox_4)
        self.label_4.setGeometry(QtCore.QRect(10, 245, 271, 41))
        self.label_4.setObjectName("label_4")
        self.checkBox_14 = CheckBox(self.groupBox_4)
        self.checkBox_14.setGeometry(QtCore.QRect(10, 40, 131, 16))
        self.checkBox_14.setObjectName("checkBox_14")
        MainWindow.setCentralWidget(self.centralwidget)
        #self.menubar = QtWidgets.QMenuBar(MainWindow)
        #self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        #self.menubar.setObjectName("menubar")
        #self.menuGithub_Repository = QtWidgets.QMenu(self.menubar)
        #self.menuGithub_Repository.setObjectName("menuGithub_Repository")
        #self.action = self.menuGithub_Repository.addAction("Open")
        #self.action.triggered.connect(self.openrespository)
       # MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        #MainWindow.setStatusBar(self.statusbar)
        #self.menubar.addAction(self.menuGithub_Repository.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Launcher"))
        self.groupBox.setTitle(_translate("MainWindow", "谱面文件"))
        self.pushButton.setText(_translate("MainWindow", "在电脑上选择一个文件"))
        self.label.setText(_translate("MainWindow", "或者"))
        self.lineEdit_2.setPlaceholderText(_translate("MainWindow", "输入一个Phira谱面ID"))
        self.groupBox_2.setTitle(_translate("MainWindow", "渲染设置"))
        self.checkBox.setText(_translate("MainWindow", "低分辨率"))
        self.checkBox_2.setText(_translate("MainWindow", "显示帧率"))
        self.checkBox_3.setText(_translate("MainWindow", "启用渲染时的 BitmapImage"))
        self.checkBox_4.setText(_translate("MainWindow", "显示Webview调试窗"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "COMBO文字，不填为AUTOPLAY"))
        self.checkBox_6.setText(_translate("MainWindow", "更多的渲染范围"))
        self.checkBox_7.setText(_translate("MainWindow", "禁用奥托普雷先生（Autoplay）"))
        self.checkBox_8.setText(_translate("MainWindow", "无边框窗口"))
        self.checkBox_9.setText(_translate("MainWindow", "无点击音效"))
        self.checkBox_10.setText(_translate("MainWindow", "循环谱面"))
        self.checkBox_11.setText(_translate("MainWindow", "全屏窗口"))
        self.checkBox_12.setText(_translate("MainWindow", "显示实时准度"))
        self.checkBox_13.setText(_translate("MainWindow", "CheckBox"))
        self.groupBox_3.setTitle(_translate("MainWindow", "渲染"))
        self.pushButton_2.setText(_translate("MainWindow", "开始渲染！"))
        self.checkBox_5.setText(_translate("MainWindow", "将渲染结果保存为视频"))
        self.label_2.setText(_translate("MainWindow", "Phigros Player GUI Launcher"))
        self.groupBox_4.setTitle(_translate("MainWindow", "高级选项"))
        self.label_3.setText(_translate("MainWindow", "如果不是真的会用，我建议你别动。"))
        self.label_4.setText(_translate("MainWindow", "使用自己的命令行参数：我们稍后会将其添加到\n"
"控制台。"))
        self.checkBox_14.setText(_translate("MainWindow", "启用JIT(不建议）"))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    

    w = mainw()
    w.show()
    app.exec_()
