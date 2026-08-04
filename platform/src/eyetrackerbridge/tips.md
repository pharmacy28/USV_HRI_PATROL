###数据传输流程

##先启动 linux 端接收桥：Windows Unity UDP -> Linux LSL
#cd /home/cyz/vrx_ws
#source .TobiiBridge/bin/activate
python src/eyetrackerbridge/gaze_lsl_bridge.py

##如果要让 operator_console 的注意力热力图工作，必须再开一个终端：
##LSL -> ROS /tobii/gaze
#cd /home/cyz/vrx_ws
#source /opt/ros/humble/setup.bash
#source install/setup.bash
#source .TobiiBridge/bin/activate
python src/eyetrackerbridge/gaze_receiver.py

##注意：不要加 --no-ros，否则只会打印 LSL 数据，不会发布 /tobii/gaze
##控制台热力图会一直显示 WAITING /tobii/gaze

##只测试 LSL 接收、不发 ROS
python src/eyetrackerbridge/gaze_receiver.py --no-ros

##检查 ROS 是否真的有眼动数据
ros2 topic list | grep tobii
ros2 topic info /tobii/gaze -v
ros2 topic echo /tobii/gaze --once

##正常应该看到 /tobii/gaze 的 Publisher count: 1
##如果 Publisher count: 0，说明 gaze_receiver.py 没有运行或没有成功初始化 ROS

##Windows 端打包后启动 exe 时，把 gaze 发到 Linux IP
EyeTrackerBridge.exe --gaze-host=Linux电脑IP --gaze-port=15555

##同一个局域网时
“”“
1、Linux 查 IP：ip -4 addr
2、Windows 查 IP：ipconfig
3、Windows ping Linux：ping Linux电脑IP
4、Linux 先跑 gaze_lsl_bridge.py
5、Windows 再启动 exe
6、Linux 终端看到 [STREAM] ... from=Windows_IP 就说明 UDP -> LSL 已通
7、再跑 gaze_receiver.py，看到 /tobii/gaze Publisher count: 1，才说明 LSL -> ROS 已通
”“”

##网线直连时
“”“
1、Linux 网卡手动设：192.168.50.1/24
2、Windows 网卡手动设：192.168.50.2，子网掩码 255.255.255.0，网关可空
3、Windows 测：ping 192.168.50.1
4、LinuxWindows exe 用：
EyeTrackerBridge.exe --gaze-host=192.168.50.1 --gaze-port=15555
5、注意 Linux 防火墙放行 UDP 15555，Windows 也别拦 Unity exe 出站
”“”

！！！关于校准和数据传输物理含义！！！
1、坐标参考对象
当前传输的 x_norm/y_norm 不是相对于 Linux 桌面，也不是相对于 ROS 可视化窗口，而是相对于 Windows 端 Unity 程序运行时的渲染窗口，也即：
screen_w = Unity Screen.width
screen_h = Unity Screen.height
归一化计算含义:
x_norm = 注视点 x 像素 / Unity 窗口宽度
y_norm = 注视点 y 像素 / Unity 窗口高度
坐标系已经统一为：
左上角 = (0, 0)
右下角 = (1, 1)
如果 Unity 是全屏运行，那么 screen_w/screen_h 就是 Windows 上 Unity 所在显示器的分辨率
如果 Unity 是窗口模式，那么 screen_w/screen_h 就是 Unity 游戏窗口内容区域的大小
2、传输数据的物理含义
当前传输的是 Tobii 计算出的 屏幕注视点 gaze point，也就是用户视线与显示屏平面相交的位置
LSL 输出通道为：
x_norm, y_norm, x_px, y_px, valid；物理含义：
x_norm：注视点在 Unity 窗口中的横向归一化位置，范围 0~1
y_norm：注视点在 Unity 窗口中的纵向归一化位置，范围 0~1
x_px：注视点在 Unity 窗口中的横向像素位置
y_px：注视点在 Unity 窗口中的纵向像素位置
valid：该帧 gaze 数据是否有效，1 有效，0 无效
3、校准需要屏幕保持一致！
