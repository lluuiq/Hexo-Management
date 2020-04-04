# !/usr/bin/env python3
# _*_coding:utf-8 _*_
# @Author : lluuiq
# @File : run.py.py
# @project : Hexo-Management
# @Time : 2020/4/3 12:13

import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import webbrowser
import subprocess
import types
import time
import os


class Window():
    def __init__(self):
        # 加载界面文件
        self.window = uic.loadUi("ui/window.ui")
        # 创建settings，用于保存和初始化信息
        self.settings = QSettings("config.ini", QSettings.IniFormat)
        ########## 初始化
        self.blog_root = "None"
        self.username = "None"
        self.password = "None"
        self.git_path = "None"
        self.branch = "None"
        self.initInfo()
        # 创建线程用于存储调试时的线程
        self.thread_server = QThread()
        self.mutex = QMutex()
        # 更改os目录
        os.chdir(self.blog_root)

        '''关闭登录功能'''
        self.window.lineEdit_username.setDisabled(True)
        self.window.lineEdit_password.setDisabled(True)
        self.window.pushButton_login.setDisabled(True)

        ########## 绑定事件
        self.window.pushButton_clear.clicked.connect(self.clear)
        # 设置界面
        self.window.toolButton_blog_root.clicked.connect(self.getBlogRoot)  # 获取博客根目录
        # self.window.pushButton_login.clicked.connect(self.logIn) # 登录用户（用不到）

        # 博客操作界面
        self.window.pushButton_back_up.clicked.connect(self.backUp)  # 备份
        self.window.pushButton_open_blog.clicked.connect(self.openBlog)  # 打开博客根目录
        self.window.pushButton_server.clicked.connect(self.server)  # hexo s
        self.window.pushButton_server_close.clicked.connect(self.serverClose)  # 关闭hexo s
        self.window.pushButton_open_server.clicked.connect(self.openServer)  # 打开调试网页
        self.window.pushButton_clean.clicked.connect(self.clean)  # hexo clean
        self.window.pushButton_generate.clicked.connect(self.generate)  # hexo g
        self.window.pushButton_deploy.clicked.connect(self.deploy)  # hexo d
        self.window.pushButton_c_g_d.clicked.connect(self.cleanGenerateDeploy)  # clean + g +d

        # 文章管理界面
        self.window.pushButton_new_post.clicked.connect(self.newPost)

    # 初始化数据函数
    def initInfo(self):
        self.blog_root = self.settings.value("blog_root")
        # self.username = self.settings.value("username")
        # self.password = self.settings.value("password")
        self.git_path = self.settings.value("git_path")
        self.branch = self.settings.value("branch")
        self.message = self.settings.value("message")
        self.window.label_blog_root.setText(self.blog_root)
        # self.window.label_username.setText(self.username)
        # self.window.label_password.setText(self.password)
        self.window.lineEdit_git_path.setText(self.git_path)
        self.window.lineEdit_branch.setText(self.branch)
        self.window.lineEdit_message.setText(self.message)

        os.chdir(self.blog_root)
        self.window.plainTextEdit.appendPlainText("=" * 100 + "\n" + "当前博客根目录为: " + os.getcwd() + "\n" + "=" * 100)

    # 获取博客根目录
    def getBlogRoot(self):
        # 获取路径
        self.blog_root = QFileDialog.getExistingDirectory(self.window,
                                                          "选取文件夹", "D:/")  # 起始路径
        # 更改标签路径
        self.window.label_blog_root.setText(self.blog_root)
        # 更改os目录
        os.chdir(self.blog_root)
        # 保存路径
        self.settings.setValue("blog_root", self.window.label_blog_root.text())
        # 输出路径
        self.window.plainTextEdit.appendPlainText("更改博客根目录为: " + os.getcwd())

    # 登录用户
    '''
    写完发现备份用不到用户名和密码。
    '''

    # def logIn(self):
    #     # 获取数据
    #     self.username = self.window.lineEdit_username.text()
    #     self.password = self.window.lineEdit_password.text()
    #     # 更改标签数据
    #     self.window.label_username.setText(self.username)
    #     self.window.label_password.setText(self.password)
    #     # 保存数据
    #     self.settings.setValue("username", self.username)
    #     self.settings.setValue("password", self.password)
    #     # 输出信息
    #     self.window.plainTextEdit.appendPlainText("登录用户名为: " + self.username + '\n' + "密码为:" + self.password)

    # 备份博客
    def backUp(self):
        # 执行备份函数
        def execute(args):
            self.window.progressBar.setMaximum(0)
            cmd = "git add . && git commit -m " + '\"' + self.message + '\"' + " && git push -f origin " + self.branch
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=1)
            # 输出信息
            self.window.plainTextEdit.appendPlainText(
                str(p.stdout.read(), encoding='utf-8') + '*' * 30 + ' 备份完毕 ' + '*' * 30)
            # 关闭stdout
            p.stdout.close()
            self.window.progressBar.setMaximum(100)

        # 定义初始化函数，用于没有.git时实现初始化
        def init(args):
            self.window.progressBar.setMaximum(0)
            # path = 'https://' + self.username + ':' + self.password + '@' + self.git_path[8:]
            cmd = "git init && git remote add origin " + self.git_path + " && git pull origin master"
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=1)
            # 输出信息
            self.window.plainTextEdit.appendPlainText(
                str(p.stderr.read(), encoding='utf-8') + '*' * 30 + ' 初始化完毕 ' + '*' * 30)
            # 关闭stdout
            p.stderr.close()
            self.window.progressBar.setMaximum(100)

        # 获取文本框内容并保存到配置信息
        self.git_path = self.window.lineEdit_git_path.text()
        self.settings.setValue("git_path", self.git_path)
        self.branch = self.window.lineEdit_branch.text()
        self.settings.setValue("branch", self.branch)
        self.message = self.window.lineEdit_message.text()
        self.settings.setValue("message", self.message)

        # 创建线程
        thread_backUp = QThread()
        # 若没有.git文件夹，则初始化仓库
        if not os.path.isdir(".git"):
            self.window.plainTextEdit.appendPlainText("检测到本地没有.git目录，初始化仓库，请等待完成")
            thread_backUp.run = types.MethodType(init, thread_backUp)
            thread_backUp.start()
        else:
            thread_backUp.run = types.MethodType(execute, thread_backUp)
            thread_backUp.start()

    # 打开博客根目录
    def openBlog(self):
        def threadRun(args):
            path = self.blog_root.replace("/", "\\")
            subprocess.Popen("start explorer " + path, shell=True)

        thread = QThread()
        thread.run = types.MethodType(threadRun, thread)
        thread.start()

    # 启动调试页面
    def openServer(self):
        # 若本地调试线程正在运行，则启动页面，否则输出警告
        if self.thread_server.isRunning():
            webbrowser.open_new("http://localhost:4000")
        else:
            self.window.plainTextEdit.appendPlainText("本地调试未开启，请先开启调试模式再启动网页")

    # 启动 hexo s
    def server(self):
        # 线程执行函数必须要有一个参数，这个参数可以无意义
        def threadRun(arg):
            self.mutex.lock()
            time.sleep(1)
            # self.window.progressBar.setMaximum(0)
            os.system("hexo s")

        # 若线程已启动，则输出警告
        if self.thread_server.isRunning():
            self.window.plainTextEdit.appendPlainText("调试模式已经启动，请勿重复")
        else:
            # 将thread_server方法强制设置为run方法
            self.thread_server.run = types.MethodType(threadRun, self.thread_server)
            # 输出信息
            self.window.plainTextEdit.appendPlainText(
                '=' * 100 + '\n' + '调试模式启动，若要执行其他hexo指令请先关闭调试模式再执行，关闭工具会自动关闭调试。\n' + 'tip:调试模式下可以进行主题相关的修改')
            ### 启动线程
            self.thread_server.start()

    # 关闭hexo s
    '''
    直接kill进程后 监听端口不会关闭... 采用查询监听然后通过PID来kill进程
    '''

    def serverClose(self):
        # 查询监听4000端口的进程
        log = os.popen(r'netstat -ano | findstr 4000', "r")
        # 若返回信息不为空，则根据PID来kill进程，否则输出警告
        lines = log.readlines()
        if lines:
            # 获取pid
            pid = lines[0].split(' ')[-1]
            log.close()
            # 若pid不为0，则执行 taskkill /F /PID 【PID】，然后结束hexo s的线程
            if (pid.strip() != '0'):
                os.system('taskkill /F /PID ' + pid)
                self.thread_server.terminate()
                self.thread_server.wait()
                # self.window.progressBar.setMaximum(100)
                # 输出信息
                self.window.plainTextEdit.appendPlainText("关闭调试模式")
            else:
                self.window.plainTextEdit.appendPlainText("调试模式未开启")
        else:
            log.close()
            self.window.plainTextEdit.appendPlainText("调试模式未开启")

    '''
    因为clean、generate、deploy的指令代码类似，故将执行部分封装为一个函数
    '''

    def hexoCmd(self, cmd, thread):
        def threadRun(args):
            self.mutex.lock()
            self.window.progressBar.setMaximum(0)
            # 执行命令
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=1)
            # 输出信息
            self.window.plainTextEdit.appendPlainText(
                str(p.stdout.read(), encoding='utf-8') + '*' * 30 + ' 指令执行完毕 ' + '*' * 30)
            # 关闭stdout
            p.stdout.close()
            self.window.progressBar.setMaximum(100)
            self.mutex.unlock()

        # 方法添加为run方法中然后启动线程
        thread.run = types.MethodType(threadRun, thread)
        thread.start()

    def clean(self):
        # 创建一个线程
        thread_clean = QThread()
        # 通过hexoCmd函数来执行指令
        self.hexoCmd("hexo clean", thread_clean)

    def generate(self):
        thread_generate = QThread()
        self.hexoCmd("hexo g", thread_generate)

    def deploy(self):
        thread_deploy = QThread()
        self.hexoCmd("hexo d", thread_deploy)

    def cleanGenerateDeploy(self):
        thread_all = QThread()
        self.hexoCmd("hexo clean && hexo g && hexo d", thread_all)

    def newPost(self):
        title = self.window.lineEdit_post_title.text()
        thread_newPost = QThread()
        self.hexoCmd("hexo new " + '\"' + title + '\"', thread_newPost)

    def modifyPost(self):


    # 清除输出信息
    def clear(self):
        self.window.plainTextEdit.clear()


if __name__ == '__main__':
    # 创建QApplication类的实例
    app = QApplication(sys.argv)

    stats = Window()
    stats.window.show()
    stats.window.tableWidget_post.
    sys.exit(app.exec_())
