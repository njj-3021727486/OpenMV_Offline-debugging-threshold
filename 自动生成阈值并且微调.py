import sensor, image, display, time
from pyb import UART

# 初始化摄像头
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA2)  # 128x160 for LCD Shield
Range=(0,0,160,120)        #设定感兴趣区域(正式识别需要对整个画面进行识别)
sensor.skip_frames(500)

# 初始化LCD
lcd = display.SPIDisplay()

# 初始化串口 (UART3, 波特率9600)
uart = UART(3, 9600, timeout_char=200)

# LAB阈值设置
threshold_min = 0
threshold_max = 255

# 默认LAB阈值



adjust_mode = False  # 阈值调整模式标志

'''  for循环200次，对感兴趣区域画边框，并且统计，最后返回LAB   '''
for i in range(200):
    img=sensor.snapshot()
    img.draw_rectangle(65,50,30,20,color=(255,0,0))     #一开始先画一个矩形框（起始x,起始y，宽度，高度）
    Statistics= img.get_statistics(roi=(65,50,30,20))   #get_statistics统计信息，得到阈值（参数roi为感兴趣区域的范围，在这个范围内，才会进行统计和赋值）
    Threshold = [Statistics.l_min(),Statistics.l_max(),
                Statistics.a_min(),Statistics.a_max(),
                Statistics.b_min(),Statistics.b_max()]
    lcd.write(img)
    print (Threshold)           #把刚刚统计得到的阈值打印出来

l_min = Threshold[0]
l_max = Threshold[1]
a_min = Threshold[2]
a_max = Threshold[3]
b_min = Threshold[4]
b_max = Threshold[5]

def draw_lab_thresholds(img, l_min, l_max, a_min, a_max, b_min, b_max):
    """显示LAB阈值数值（不显示滑块）"""
    # 显示位置参数
    start_y = 20
    line_spacing = 10
    bar_x = 20

    # 显示标题
    img.draw_string(bar_x+5, 5, "LAB Thresholds", color=(255, 255, 255))

    # L通道阈值
    img.draw_string(0, start_y, "L", color=(0, 255, 0))#第一行
    img.draw_string(0, start_y + line_spacing, "Min:%d" % l_min, color=(0, 255, 0))#第二行
    img.draw_string(70 , start_y + line_spacing, "Max:%d" % l_max, color=(0, 255, 0))#第二行

    # A通道阈值
    img.draw_string(0, start_y + 2 * line_spacing, "A", color=(255, 0, 0))
    img.draw_string(0, start_y + 3 * line_spacing, "Min:%d" % a_min, color=(255, 0, 0))
    img.draw_string(70, start_y + 3 *line_spacing, "Max:%d" % a_max, color=(255, 0, 0))

    # B通道阈值
    img.draw_string(0, start_y + 4 * line_spacing, "B", color=(0, 0, 255))
    img.draw_string(0, start_y + 5 * line_spacing, "Min:%d" % b_min, color=(0, 0, 255))
    img.draw_string(70, start_y + 5 * line_spacing, "Max:%d" % b_max, color=(0, 0, 255))

print("初始化成功！！")

while True:
    # 检查串口数据
    if uart.any():
        data = uart.read(1)  # 读取1字节数据

        if data == b'\x30':  # 进入阈值调整模式
            adjust_mode = True
            print("Enter LAB adjust mode")

        elif data == b'\x31':  # 保存并退出阈值调整模式
            adjust_mode = False
            print("Exit and save LAB thresholds:")
            print("L: [%d, %d]" % (l_min, l_max))
            print("A: [%d, %d]" % (a_min, a_max))
            print("B: [%d, %d]" % (b_min, b_max))


        elif adjust_mode:  # 在调整模式下处理LAB值调整
            if data == b'\x01':   # L_min+
                l_min = min(l_min + 1, l_max-1)
                print("L_min +1:", l_min)

            elif data == b'\x02':  # L_min-
                l_min = max(l_min - 1, threshold_min)
                print("L_min -1:", l_min)

            elif data == b'\x03':  # L_max+
                l_max = min(l_max + 1, threshold_max)
                print("L_max +1:", l_max)

            elif data == b'\x04':  # L_max-
                l_max = max(l_max - 1, l_min+1)
                print("L_max -1:", l_max)

            elif data == b'\x05':  # A_min+
                a_min = min(a_min + 1, a_max-1)
                print("A_min +1:", a_min)

            elif data == b'\x06':  # A_min-
                a_min = max(a_min - 1, -128)
                print("A_min -1:", a_min)

            elif data == b'\x07':  # A_max+
                a_max = min(a_max + 1, 127)
                print("A_max +1:", a_max)

            elif data == b'\x08':  # A_max-
                a_max = max(a_max - 1, a_min+1)
                print("A_max -1:", a_max)

            elif data == b'\x09':  # B_min+
                b_min = min(b_min + 1, b_max-1)
                print("B_min +1:", b_min)

            elif data == b'\x10':  # B_min-
                b_min = max(b_min - 1, -128)
                print("B_min -1:", b_min)

            elif data == b'\x11':  # B_max+
                b_max = min(b_max + 1, 127)
                print("B_max +1:", b_max)

            elif data == b'\x12':  # B_max-
                b_max = max(b_max - 1, b_min+1)
                print("B_max -1:", b_max)

    # 捕获图像
    img = sensor.snapshot()

    if adjust_mode:
        # LAB调整模式：显示原始图像和阈值数值
        binary = img.binary([(l_min, l_max, a_min, a_max, b_min, b_max)])
        lcd.write(binary)
        rgb_binary = binary.to_rgb565()
        draw_lab_thresholds(img, l_min, l_max, a_min, a_max, b_min, b_max)
        img.draw_string(100, 5, "ADJUST MODE", color=(255, 255, 0))
        lcd.write(rgb_binary)

    else:
        # 正常模式：使用LAB阈值处理图像
        # 转换为LAB颜色空间
        # 应用LAB阈值

        for blob in img.find_blobs([Threshold],roi=Range,pixels_threshold=100,area_threshold=100,merge=True,margin=10):
            img.draw_rectangle(blob.rect())     #draw_rectangle画矩形边框，位置由参数blob.rect()决定，其中参数blob.rect()是返回一个元组，（起始x,起始y，宽度，高度）
            img.draw_cross(blob.cx(),blob.cy())#draw_cross画十字架，参数（blob.cx(),blob.cy()），色块中心的x坐标和y坐标
            print(blob.cx(),blob.cy())          #打印x和y坐表
            lcd.write(img)
        lcd.write(img)
    time.sleep_ms(50)
