import sys,time,threading
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication,QSystemTrayIcon,QMenu,QAction
import psutil

app = QApplication(sys.argv)

#猫猫托盘图标类
class CatTrayIcon:
    #标记，选择显示总体利用率(0)还是每个逻辑处理器的利用率(1)
    mode_flag = 0
    def __init__(self):
        #加载图标文件
        self.icon_list = [QIcon(f'dark_cat_{i}.ico') for i in range(5)]
        #管理托盘图标的变量
        self.tray = None
        #显示图标，初始默认为显示总体利用率，单个图标
        self.show_icon()

    #退出函数
    def exit_app(self):
        if CatTrayIcon.mode_flag == 0:
            #隐藏图标，防止刷新不及时
            self.tray.hide()
        else:
            for i in self.tray:
                i.hide()
        sys.exit()

    def change_mode(self):
        #隐藏图标，然后self.tray置空
        if CatTrayIcon.mode_flag == 0:
            self.tray.hide()
        else:
            for i in self.tray:
                i.hide()
        self.tray = None
        #修改标记，重新显示
        CatTrayIcon.mode_flag = not CatTrayIcon.mode_flag
        time.sleep(0.3)
        self.show_icon()

    #托盘右键菜单
    def set_menu(self,tray_obj):
        self.tray_menu = QMenu()
        self.exit_action = QAction("退出(exit)",triggered=self.exit_app)
        self.tray_menu.addAction(self.exit_action)
        self.change_mode_action = QAction("切换显示模式(change mode)",triggered=self.change_mode)
        self.tray_menu.addAction(self.change_mode_action)
        tray_obj.setContextMenu(self.tray_menu)

    #根据模式显示图标
    def show_icon(self):
        if CatTrayIcon.mode_flag == 0:
            #设置托盘图标
            self.tray = QSystemTrayIcon()
            self.tray.setIcon(QIcon(self.icon_list[0]))
            self.tray.show()
            self.set_menu(self.tray)
            #新开一个线程显示单个图标
            threading.Thread(target=self.show_single_icon).start()
        else:
            #每个逻辑处理器都显示，先初始化成空列表
            self.tray=[]
            for i in range(len(cpu_percent)):
                #填入对应数量的托盘图标对象
                self.tray.append(QSystemTrayIcon())
                self.tray[i].setIcon(QIcon(self.icon_list[0]))
                self.tray[i].show()
                self.set_menu(self.tray[i])
                #每个图标都开一个线程去显示
                threading.Thread(target=self.show_all_icon,args=(i,)).start()

    #显示单个图标（总体利用率）
    def show_single_icon(self):
        try:
            #循环更新图标
            while True:
                #根据CPU使用率计算延迟时间，计算方法由用户自由修改
                delay = 0.38-0.78*cpu_percent/100+0.42*cpu_percent/100*cpu_percent/100
                #print(delay)    
                for i in range(5):
                    self.tray.setIcon(QIcon(self.icon_list[i]))
                    self.tray.setToolTip(f'CPU: {cpu_percent}%')
                    time.sleep(delay)
        except Exception:
            return 0

    #显示逻辑处理器的图标，num:逻辑处理器序号
    def show_all_icon(self,num):
        try:
            while True:
                #根据CPU使用率计算延迟时间，计算方法由用户自由修改
                delay = 0.38-0.78*cpu_percent[num]/100+0.42*cpu_percent[num]/100*cpu_percent[num]/100
                for i in range(5):
                    self.tray[num].setIcon(QIcon(self.icon_list[i]))
                    self.tray[num].setToolTip(f'CPU{num}: {cpu_percent[num]}%')
                    time.sleep(delay)
        except Exception:
            return 0

#CPU的利用率
cpu_percent = 0
#每隔0.2s获取CPU的利用率，分为总体利用率和每个逻辑处理器的利用率
def get_cpu_percent():
    global cpu_percent
    while True:
        if CatTrayIcon.mode_flag == 0:
            #总体利用率
            cpu_percent = psutil.cpu_percent()
        else:
            #每个逻辑处理器的利用率，此时返回列表
            cpu_percent = psutil.cpu_percent(percpu=True)
        time.sleep(0.2)

#单独创建一个线程执行
threading.Thread(target=get_cpu_percent).start()

time.sleep(0.2)
cat = CatTrayIcon()

sys.exit(app.exec_())