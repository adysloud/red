import os
import random
import sys
import win32api
import win32con
from PyQt5.Qt import QCursor
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QPainter, QImage, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QAction, QMenu


class MainWindows(QWidget):
    def __init__(self):
        # 调用父类初始化函数
        super(MainWindows, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # 当前宠物
        self.resource='red'

        # 设置窗口的尺寸
        self.resize(3000, 3000)

        # 初始化托盘
        self.tray_init()

        # 当前图片位置(左上角)
        self.position_x = 700
        self.position_y = 0

        # flag
        self.end_drop_flag=False  # 落地
        self.relax_flag=False  # relax
        self.the_coffin_board_of_Newton_flag=False  # 飞出去
        self.Geocentric_travel_notes=False  # 人为拖下去
        self.Poke_flag=False  # 戳一戳
        self.sit_flag=False
        self.sleep_flag=False

        # 当前加载的图片路径与第几张图与当前图片的第几个周期与...
        self.image_index=0  # 第几张图
        self.the_same_image=0  # 当前图片的第几个周期
        self.the_same_image_index=3  # 同一图组加载多少图
        self.path=os.path.join(self.resource,str(self.image_index)+'.jpg')

        # 扫描各图像包图像量
        self.relax_index=len(os.listdir(os.path.join(self.resource,'left','relax')))
        self.drop_index=len(os.listdir(os.path.join(self.resource,'left','drop')))
        self.run_index=len(os.listdir(os.path.join(self.resource,'left','move')))
        self.poke_index=len(os.listdir(os.path.join(self.resource,'left','poke')))
        self.sit_index=len(os.listdir(os.path.join(self.resource,'left','sit')))
        self.sleep_index=len(os.listdir(os.path.join(self.resource,'left','sleep')))

        # 图像刷新频率(ms)
        self.image_refresh_rate=20

        # 运动方向与长度
        self.run_diction='left'
        self.run_diction_index=0  # 1,-1
        self.run_length=0

        # 睡眠时间与坐下时间
        self.sleep_or_sit_nowtime=0
        self.sleep_or_sit_time=0

        # 步长
        self.step_length=2

        # 牛顿棺材板部分
        self.delta_x=0
        self.delta_y=0
        self.Gravity_velocity=0  # 当前加速度
        self.Gravitational_acceleration=1  # 重力加速度

        # 边界
        self.left_bound = -80
        self.right_bound = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)-70
        self.up_bound = -200
        self.down_bound = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)-266

        # 初始化一个定时器
        self.timer = QTimer()
        self.timer.start(self.image_refresh_rate)
        self.timer.timeout.connect(self.Central_processor)

    # 中心处理器
    # 优先级：
    # 是否坠落
    # 是否落地
    # 是否戳一戳
    # 是否relax
    # 是否run(move)
    # 是否sit
    # 是否sleep
    # 下一个动作判断
    def Central_processor(self):
        if self.the_coffin_board_of_Newton_flag==True or self.position_y<self.down_bound:
            if self.position_y>self.down_bound:
                self.Geocentric_travel_notes=True
            self.the_coffin_board_of_Newton()
        elif self.end_drop_flag==True:
            self.path=os.path.join(self.resource,self.run_diction,'drop',str(self.image_index)+'.png')
            self.the_same_image+=1
            self.the_same_image_index_check()
            if self.image_index>=self.drop_index:
                self.end_drop_flag=False
                self.image_index=0
        elif self.Poke_flag==True:
            self.path=os.path.join(self.resource,self.run_diction,'poke',str(self.image_index)+'.png')
            self.the_same_image += 1
            self.the_same_image_index_check()
            if self.image_index>=self.poke_index:
                self.path=os.path.join(self.resource,self.run_diction,'relax','0.png')
                self.position_y-=1
                self.Poke_flag=False
                self.image_index=0
                self.repaint()
        elif self.run_diction_index!=0 or self.relax_flag==True or self.sit_flag==True or self.sleep_flag==True:
            if self.relax_flag==True:  # relax
                self.path = os.path.join(self.resource, self.run_diction,'relax', str(self.image_index) + '.png')
                self.the_same_image += 1
                self.the_same_image_index_check()
                if self.image_index >= self.relax_index:
                    self.relax_flag = False
                    self.image_index = 0
            elif self.sit_flag==True:
                self.path=os.path.join(self.resource, self.run_diction, 'sit', str(self.image_index) + '.png')
                self.the_same_image += 1
                self.the_same_image_index_check()
                if self.image_index >= self.sit_index:
                    self.sleep_or_sit_nowtime+=1
                    if self.sleep_or_sit_nowtime>=self.sleep_or_sit_time:
                        self.sleep_or_sit_nowtime=0
                        self.relax_flag = False
                    self.image_index = 0
            elif self.sleep_flag==True:
                self.path=os.path.join(self.resource, self.run_diction, 'sleep', str(self.image_index) + '.png')
                self.the_same_image += 1
                self.the_same_image_index_check()
                if self.image_index >= self.sleep_index:
                    self.sleep_or_sit_nowtime+=1
                    if self.sleep_or_sit_nowtime>=self.sleep_or_sit_time:
                        self.sleep_or_sit_nowtime=0
                        self.relax_flag = False
                    self.image_index = 0
            else:
                self.position_x=self.position_x+self.step_length*self.run_diction_index
                self.path = os.path.join(self.resource, self.run_diction, 'move', str(self.image_index) + '.png')
                self.the_same_image += 1
                self.the_same_image_index_check()
                self.run_length-=self.step_length
                if self.position_x>=self.right_bound or self.position_x<=self.left_bound:
                    self.run_length=0
                if self.image_index>=self.run_index:
                    self.image_index=1
                if self.run_length<=0:
                    self.run_diction_index = 0
                    self.image_index = 0
        else:
            next_action_index=random.randint(1,113)
            if next_action_index<=70:  # relax
                self.relax_flag=True
            elif next_action_index<=100:  # run(move)
                if next_action_index<=85:
                    self.run_diction='left'
                    self.run_diction_index=-1
                else:
                    self.run_diction='right'
                    self.run_diction_index=1
                self.run_length = random.randint(1, 5) * (self.run_index-1) * self.step_length*self.the_same_image_index
            elif next_action_index<=110:  # sit
                self.sleep_or_sit_time=int((next_action_index-100)/2)
                self.sit_flag=True
            elif next_action_index<=113:  # sleep
                self.sleep_or_sit_time=(next_action_index-110)*2
                self.sleep_flag=True
        self.repaint()

    def the_coffin_board_of_Newton(self):
        self.position_x = self.position_x + self.delta_x
        self.position_y = self.position_y + self.delta_y + self.Gravity_velocity
        self.Gravity_velocity += self.Gravitational_acceleration
        if self.Geocentric_travel_notes==False:
            if self.position_y >= self.down_bound:
                self.position_y = self.down_bound
                self.end_drop_flag = True
                self.the_coffin_board_of_Newton_flag=False
                self.delta_x=0
                self.delta_y=0
                self.Gravity_velocity = 0
        else:
            if self.position_y>self.down_bound+300:
                self.position_y=self.up_bound
                self.Geocentric_travel_notes=False
        # 左右穿墙
        if self.position_x > self.right_bound:
            self.position_x = self.left_bound
        elif self.position_x < self.left_bound:
            self.position_x = self.right_bound


    # 鼠标相关代码
    # 一次性（检测鼠标按下）
    def mousePressEvent(self, event):
        self.timer.stop()
        self.image_index=0
        self.relax_flag=False
        self.sit_flag=False
        self.sleep_flag=False
        self.Poke_flag=True
        self.run_diction_index=0
        self.Gravity_velocity = 0
        self.mouse_drag_pos = event.globalPos() - self.pos()

    # 只要鼠标按下循环触发
    def mouseMoveEvent(self, event):
        self.Poke_flag=False
        self.delta_x=int((QCursor.pos().x()-75-self.position_x)/5)
        self.delta_y=int((QCursor.pos().y()-119-self.position_y)/5)
        self.position_x=QCursor.pos().x()-75
        self.position_y=QCursor.pos().y()-119
        if self.delta_x > 0:
            self.run_diction = 'right'
        else:
            self.run_diction = 'left'
        self.path=os.path.join(self.resource,self.run_diction,'drop','0.png')
        self.repaint()

    # 重写鼠标抬起事件
    def mouseReleaseEvent(self, event):
        if self.Poke_flag==False:
            self.the_coffin_board_of_Newton_flag = True
        else:
            self.the_coffin_board_of_Newton_flag = False
        if self.position_y==self.down_bound:
            self.position_y+=1
        else:
            self.Poke_flag=False
        self.timer.start(self.image_refresh_rate)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.begin(self)
        # 装载图像
        image = QImage(self.path)
        rect3 = QRect(self.position_x, self.position_y, image.width(), image.height())
        qp.drawImage(rect3, image)
        qp.end()

    def tray_init(self):
        # QAction https://hanhan.blog.csdn.net/article/details/113248533
        quit_action = QAction('退出', self, triggered=self.quit)  # 设置右键点开能看到的选项与相应功能
        # quit_action = QAction('退出',self)  # 设置右键点开能看到的选项与相应功能
        # quit_action.setShortcut('Ctrl+Alt+q')  # 设置快捷键(事实上没有任何效果）
        quit_action.setIcon(QIcon('red\\0.jpg'))  # 设置右键点开时左边的图片
        self.tray_icon_menu = QMenu(self)
        self.tray_icon_menu.addAction(quit_action)  # 添加功能（猜的）
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('red\\0.jpg'))  # 托盘图案
        self.tray_icon.setContextMenu(self.tray_icon_menu)  # 绑定功能
        self.tray_icon.show()  # show

    def the_same_image_index_check(self):
        if self.the_same_image>=self.the_same_image_index:
            self.image_index+=1
            self.the_same_image=0

    def quit(self):
        self.close()
        sys.exit()


if __name__=='__main__':
    app=QApplication(sys.argv)
    app.setWindowIcon(QIcon('red\\0.jpg'))

    main=MainWindows()
    main.show()
    # 进入程序主循环
    sys.exit(app.exec_())
