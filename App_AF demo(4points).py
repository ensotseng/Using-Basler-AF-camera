import numpy as np
from pypylon import pylon
import pypylon.pylon as py
import time
import cv2
from tkinter import ttk
from ttkthemes import ThemedTk
import tkinter as tk
from PIL import Image, ImageTk
import threading
import tkinter.messagebox

def grab():

    camera.ExecuteSoftwareTrigger()

    with cam.RetrieveResult(1500) as res:
        img = np.copy(res.Array).astype(np.int16)


    return img

def defineposition(event, x, y, flags, param):
    global point1

    if event == cv2.EVENT_LBUTTONDOWN:  # 左鍵點擊

        point1 = (x, y)
        points.append(point1)

def on_mouse(event, x, y, flags, param):
    global point1

    if event == cv2.EVENT_LBUTTONDOWN:  # 左鍵點擊

        point1 = (x, y)
        print(point1)
        x = point1[0]
        y = point1[1]
        global ROI
        ROI = 128
        camera.AutoFunctionROISelector.SetValue("AutoFocusROI")

        camera.AutoFunctionROIOffsetX.SetValue(4 * int((x / 4)))
        camera.AutoFunctionROIOffsetY.SetValue(2 * int((y / 2)))
    if event == cv2.EVENT_LBUTTONDBLCLK:
        point1 = (x, y)
        x = point1[0]
        y = point1[1]
        camera.AutoFunctionROISelector.SetValue("AutoFocusROI")
        camera.AutoFunctionROIOffsetX.SetValue(4 * int((x / 4)))
        camera.AutoFunctionROIOffsetY.SetValue(2 * int((y / 2)))
        focus()





def mouseclick_thread():
    t = threading.Thread(target=on_mouse)
    t.start()

def focus():

    camera.FocusAuto.SetValue("Once")
    t2 = threading.Thread(target=updateFP)
    t2.start()

def updateFP():
    time.sleep(1)
    val = camera.LensOpticalPower.GetValue()
    FP.set(val)







def search_peak(data):
    count = 0
    max_temp = 0
    max_index = 0
    for ii in range(data.shape[0] - 1):
        count += 1
        if data[ii, 1] > max_temp:
            max_temp = data[ii, 1]
            max_index = count - 1

    # y=ax^2+bx+c
    x1, y1 = data[max_index, 0], data[max_index, 1]
    x2, y2 = data[max_index + 1, 0], data[max_index + 1, 1]
    x3, y3 = data[max_index - 1, 0], data[max_index - 1, 1]

    a = np.array([[x1 ** 2, x1, 1], [x2 ** 2, x2, 1], [x3 ** 2, x3, 1]])
    b = np.array([y1, y2, y3])
    x = linalg.solve(a, b)
    print("x0 = {}, x1 ={}".format(x[0],x[1]))
    peak = (-1) * x[1] / x[0] / 2
    print(peak)
    return peak,max_index,x




def grabbingend():
    cam.StopGrabbing()
def mouseclickAF():
    while cam.IsGrabbing():

        grabResult = cam.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)


        if grabResult.GrabSucceeded():
            # Access the image data
            image = converter.Convert(grabResult)
            img = image.GetArray()
            fps = camera.ResultingFrameRate.GetValue()


            cv2.namedWindow('Autofocus', cv2.WINDOW_NORMAL)
            # #
            cv2.setMouseCallback('Autofocus', on_mouse)

            cv2.circle(img, point1, 64, (10, 50, 255), 10)
            cv2.putText(img,"fps = {:.0f} ".format(fps), (0, 50), cv2.FONT_HERSHEY_DUPLEX,2, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.resizeWindow("Autofocus",1600,1200)
            cv2.imshow('Autofocus', img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        grabResult.Release()

    # Releasing the resource
    cam.StopGrabbing()
    cv2.destroyAllWindows()
def AFdemo():
    count = 0
    pointcount = 0



    while cam.IsGrabbing():

        points = [(int(pos1x.get()), int(pos1y.get())), (int(pos2x.get()),int(pos2y.get())),  (int(pos3x.get()),int(pos3y.get())),  (int(pos4x.get()),int(pos4y.get()))]
        grabResult = cam.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        count +=1


        if grabResult.GrabSucceeded():
            # Access the image data
            image = converter.Convert(grabResult)
            img = image.GetArray()
            fps = camera.ResultingFrameRate.GetValue()

            cv2.namedWindow('Autofocus', cv2.WINDOW_NORMAL)
            # #
            # cv2.setMouseCallback('Autofocus', on_mouse)
            point1 = points[pointcount%4]
            for ii in range(4):
                cv2.circle(img, points[ii], 64, (230, 240, 255), 5)
            cv2.circle(img, points[pointcount % 4 - 1], 64, (106, 106, 255), 20)

            if count % int(fps*float(waittime.get()))==0 :
                count =0
                point1 = points[pointcount%4]
                camera.BslFocusXOffset.SetValue(4*int(point1[0]/4))
                camera.BslFocusYOffset.SetValue(4*int(point1[1]/4))
                pointcount+=1
                focus()


            cv2.putText(img,"fps = {:.0f} ; focal power = {:.3f} [dpt]".format(fps,FP.get()), (0, 50), cv2.FONT_HERSHEY_DUPLEX,2, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.resizeWindow("Autofocus", 1600, 1200)
            cv2.imshow('Autofocus', img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        grabResult.Release()

        # Releasing the resource
    cam.StopGrabbing()
    cv2.destroyAllWindows()
def AFdemo_Thread():


    t =threading.Thread(target=AFdemo)
    t.start()
def on_closing():
    cam.StopGrabbing()
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        win.quit()
        win.destroy()

def show(img):
    img =Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)
    panel.imgtk =imgtk
    panel.config(image = imgtk)
    win.after(1,show)

devices = py.TlFactory.GetInstance().EnumerateDevices()
camera = py.InstantCamera(py.TlFactory.GetInstance().CreateDevice(devices[0]))
camera.Open()
cam = camera
converter = pylon.ImageFormatConverter()
# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
try:
    camera.FocusAutoReset.Execute()
except:
    pass
try:
    camera.FocusInitialize.Execute()
except:
    pass

camera.LensConnection.SetValue("Connect")
camera.TriggerMode.SetValue("Off")

def setexposure(val): #一定要內含變數
    val = int(exposure.get())
    camera.ExposureTime.SetValue(val)
def setgain(val):
    val = float(gain.get())
    camera.Gain.SetValue(val)

def setFP(val):
    val = float(FP.get())
    camera.LensOpticalPower.SetValue(val)
def setstepper(val):
    val = float(stepper.get())
    camera.FocusStepper.SetValue(val)
def setLowlimit(val):
    val = float(Lowlimit.get())
    if val > camera.FocusStepperUpperLimit.GetValue():
        val = camera.FocusStepperUpperLimit.GetValue() - 1
        if val < -3.5:
            val = -3.5
    camera.FocusStepperLowerLimit.SetValue(val)
    Lowlimit.set(val)
def setUplimit(val):
    val = float(Uplimit.get())
    if val < camera.FocusStepperLowerLimit.GetValue():
        val = camera.FocusStepperLowerLimit.GetValue() + 1
        if val >4:
            val =4
    camera.FocusStepperUpperLimit.SetValue(val)
    Uplimit.set(val)




try:
    camera.PixelFormat = "BayerRG8"

except:
    pass




try:
    current_bandwidth_control_mode = camera.GetNodeMap().GetNode('DeviceLinkThroughputLimitMode')
    # Set the bandwidth control mode to 'On'
    current_bandwidth_control_mode.SetValue('On')

    # Set the desired bandwidth
    desired_bandwidth = 380000000
    camera.GetNodeMap().GetNode('DeviceLinkThroughputLimit').SetValue(int(desired_bandwidth))
except:
    pass



# exposure = input("exposure time = ?")
# camera.ExposureTime.SetValue(int(exposure))
# gain = input("gain = ?")
# camera.Gain.SetValue(float(gain))
# stepper = input("Stepper = ?")
# camera.FocusStepper.SetValue(float(stepper))
# upperlimit = input("UpperLimit = ?")
# camera.FocusStepperUpperLimit.SetValue(float(upperlimit))
# try:
#     lowerlimit = input("lowerlimit = ?")
#     camera.FocusStepperLowerLimit.SetValue(float(lowerlimit))
# except:
#     pass



try:
    camera.FocusAutoForceStop.Execute()
except:
    pass



win = ThemedTk(themebg=True)
win.set_theme('breeze')
win.title('AF demo')  # 更改視窗的標題
win.geometry('210x560')  # 修改視窗大小(寬x高)
win.resizable(False, False)  # 如果不想讓使用者能調整視窗大小的話就均設為False
win.iconbitmap('basler_icon.ico')  # 更改左上角的icon圖示
win.configure(background='#F0F0F0')

style = ttk.Style()
style.configure('TButton',font=('microsoft yahei', 9,'bold'))


tabControl = ttk.Notebook(win)          # Create Tab Control
tab2 = ttk.Frame(tabControl)  # Add a second tab


converter = pylon.ImageFormatConverter()
# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned


try:
    camera.PixelFormat = "BayerRG8"

except:
    pass







cam.StopGrabbing()
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)


try:
    camera.FocusAutoForceStop.Execute()
except:
    pass






tabControl = ttk.Notebook(win)          # Create Tab Control
tab2 = ttk.Frame(tabControl)
tab3 = ttk.Frame(tabControl) # Add a second tab
tabControl.add(tab2, text='Camera setting')
tabControl.place(x=10, y =60)
tabControl.add(tab3, text='Positions')
tabControl.place(x=10, y =60)




#
camera.ExposureTime.SetValue(8333)
exposure = tk.IntVar(None, '8333')
exposure_label = tk.Label(tab2, text="exposure [us]:",font=('Corbel',10))
exposure_label.grid()
exposure_entry = tk.Entry(tab2, foreground="#0080FF", textvariable=exposure,width=10,)
exposure_entry.grid()
exposure_scale = ttk.Scale(tab2, from_=5000, to=20000, variable = exposure,orient="horizontal",command = setexposure,length = 150)
exposure_scale.grid()

camera.Gain.SetValue(0)
gain = tk.IntVar(None, '0')
gain_label = tk.Label(tab2, text="Gain [dB]:",font=('Corbel',10))
gain_label.grid()
gain_entry = tk.Entry(tab2, foreground="#0080FF", textvariable=gain,width=10,)
gain_entry.grid()
gain_scale = ttk.Scale(tab2, from_=0, to=24, variable = gain,orient="horizontal",command = setgain,length = 150)
gain_scale.grid()

FP = tk.DoubleVar(None, '0')
FP_label = tk.Label(tab2, text="Focal power [dpt]:",font=('Corbel',10))
FP_label.grid()
FP_entry = tk.Entry(tab2, foreground="#0080FF", textvariable=FP,width=10,)
FP_entry.grid()
FP_scale = ttk.Scale(tab2, from_=-3.5, to=4, variable = FP,orient="horizontal",command = setFP,length = 150)
FP_scale.grid()

stepper = tk.DoubleVar(None, '0.2')
stepper_label = tk.Label(tab2, text="Focal power stepper [dpt]:",font=('Corbel',10))
stepper_label.grid()
stepper_entry = tk.Entry(tab2, foreground="#0080FF", textvariable=stepper,width=10,)
stepper_entry.grid()
stepper_scale = ttk.Scale(tab2, from_=0.1, to=0.4, variable = stepper,orient="horizontal",command = setstepper,length = 150)
stepper_scale.grid()


Lowlimit = tk.DoubleVar(None, '0')
Lowlimit_label = tk.Label(tab2, text="Focal power LowerLimit [dpt]:",font=('Corbel',10))
Lowlimit_label.grid()
Lowlimit_entry = tk.Entry(tab2, foreground="#0080FF", textvariable=Lowlimit,width=10,)
Lowlimit_entry.grid()
Lowlimit_scale = ttk.Scale(tab2, from_=-3.5, to=4, variable = Lowlimit,orient="horizontal",command = setLowlimit,length = 150)
Lowlimit_scale.grid()

Uplimit = tk.DoubleVar(None, '3.6')
Uplimit_label = tk.Label(tab2, text="Focal power UpperLimit [dpt]:",font=('Corbel',10))
Uplimit_label.grid()
Uplimit_entry = tk.Entry(tab2, foreground="#0080FF", textvariable=Uplimit,width=10,)
Uplimit_entry.grid()
Uplimit_scale = ttk.Scale(tab2, from_=-3.5, to=4, variable = Uplimit,orient="horizontal",command = setUplimit,length = 150)
Uplimit_scale.grid()

waittime = tk.DoubleVar(None, '2')
waittime_label = tk.Label(tab3, text="AF period",font=('Corbel',10))
waittime_label.grid(column=0, row=0)
waittime_entry = tk.Entry(tab3, foreground="#0080FF", textvariable=waittime,width=4,)
waittime_entry.grid(column=2, row=0)
waittime_scale = ttk.Scale(tab3, from_=1, to=10, variable = waittime,orient="horizontal",length = 85)
waittime_scale.grid(column=1, row=0)

x = int((camera.SensorWidth.GetValue()/4))
y = int(camera.SensorHeight.GetValue()/4)
pos1x = tk.DoubleVar(None, '{:.0f}'.format(x))
pos1x_label = tk.Label(tab3, text="pos1_x",font=('Corbel',10))
pos1x_label.grid(column=0, row=3)
pos1x_scale = ttk.Scale(tab3, from_=64, to=camera.BslFocusXOffset.GetMax(), variable = pos1x,orient="horizontal",length = 85)
pos1x_scale.grid(column=1, row=3)
pos1x_entry = tk.Entry(tab3, foreground="#0080FF", textvariable=pos1x,width=4,)
pos1x_entry.grid(column=2, row=3)

pos1y = tk.DoubleVar(None, '{:.0f}'.format(y))
pos1y_label = tk.Label(tab3, text="pos1_y",font=('Corbel',10))
pos1y_label.grid(column=0, row=4)
pos1y_scale = ttk.Scale(tab3, from_=64, to=camera.BslFocusYOffset.GetMax(), variable = pos1y,orient="horizontal",length = 85)
pos1y_scale.grid(column=1, row=4)
pos1y_entry = tk.Entry(tab3, foreground="#0080FF", textvariable=pos1y,width=4,)
pos1y_entry.grid(column=2, row=4)

pos2x = tk.DoubleVar(None, '{:.0f}'.format(3*x))
pos2x_label = tk.Label(tab3, text="pos2_x",font=('Corbel',10))
pos2x_label.grid(column=0, row=6)
pos2x_scale = ttk.Scale(tab3, from_=64, to=camera.BslFocusXOffset.GetMax(), variable = pos2x,orient="horizontal",length = 85)
pos2x_scale.grid(column=1, row=6)
pos2x_entry = tk.Entry(tab3, foreground="#0080FF", textvariable=pos2x,width=4,)
pos2x_entry.grid(column=2, row=6)
pos2y = tk.DoubleVar(None, '{:.0f}'.format(y))
pos2y_label = tk.Label(tab3, text="pos2_y",font=('Corbel',10))
pos2y_label.grid(column=0, row=7)
pos2y_scale = ttk.Scale(tab3, from_=64, to=camera.BslFocusYOffset.GetMax(), variable = pos2y,orient="horizontal",length = 85)
pos2y_scale.grid(column=1, row=7)
pos2y_entry = tk.Entry(tab3, foreground="#0080FF", textvariable=pos2y,width=4,)
pos2y_entry.grid(column=2, row=7)

pos3x = tk.DoubleVar(None, '{:.0f}'.format(x))
pos3x_label = tk.Label(tab3, text="pos3_x",font=('Corbel',10))
pos3x_label.grid(column=0, row=9)
pos3x_scale = ttk.Scale(tab3, from_=64, to=camera.BslFocusXOffset.GetMax(), variable = pos3x,orient="horizontal",length = 85)
pos3x_scale.grid(column=1, row=9)
pos3x_entry = tk.Entry(tab3, foreground="#0080FF", textvariable=pos3x,width=4,)
pos3x_entry.grid(column=2, row=9)
pos3y = tk.DoubleVar(None, '{:.0f}'.format(y*3))
pos3y_label = tk.Label(tab3, text="pos3_y",font=('Corbel',10))
pos3y_label.grid(column=0, row=10)
pos3y_scale = ttk.Scale(tab3, from_=64, to=camera.BslFocusYOffset.GetMax(), variable = pos3y,orient="horizontal",length = 85)
pos3y_scale.grid(column=1, row=10)
pos3y_entry = tk.Entry(tab3, foreground="#0080FF", textvariable=pos3y,width=4,)
pos3y_entry.grid(column=2, row=10)

pos4x = tk.DoubleVar(None, '{:.0f}'.format(3*x))
pos4x_label = tk.Label(tab3, text="pos4_x",font=('Corbel',10))
pos4x_label.grid(column=0, row=12)
pos4x_scale = ttk.Scale(tab3, from_=64, to=camera.BslFocusXOffset.GetMax(), variable = pos4x,orient="horizontal",length = 85)
pos4x_scale.grid(column=1, row=12)
pos4x_entry = tk.Entry(tab3, foreground="#0080FF", textvariable=pos4x,width=4,)
pos4x_entry.grid(column=2, row=12)
pos4y = tk.DoubleVar(None, '{:.0f}'.format(y*3))
pos4y_label = tk.Label(tab3, text="pos4_y",font=('Corbel',10))
pos4y_label.grid(column=0, row=13)
pos4y_scale = ttk.Scale(tab3, from_=64, to=camera.BslFocusYOffset.GetMax(), variable = pos4y,orient="horizontal",length = 85)
pos4y_scale.grid(column=1, row=13)
pos4y_entry = tk.Entry(tab3, foreground="#0080FF", textvariable=pos4y,width=4,)
pos4y_entry.grid(column=2, row=13)


panel = tk.Label(win)
panel.grid()
win.config(cursor ="arrow")
# text_FFC = tk.Text(tab2, width=50, height=5, undo=True, autoseparators=False)
# text_FFC.grid(row=4,column=0)
# text_FFC.tag_config('warning', foreground="#FF5151")
# text_FFC.tag_config('setting', foreground="#0080FF")
# text_FFC.tag_config('processing', foreground="#00A600")
def AWB():
    camera.BalanceWhiteAuto.SetValue("Once")
    # camera.BalanceWhiteAuto.SetValue("Off")
def reconnectLL():
    camera.LensConnection.SetValue("NotConnect")
    time.sleep(0.2)
    camera.LensConnection.SetValue("Connect")
    Lowlimit.set(camera.FocusStepperLowerLimit.GetValue())
    Uplimit.set(camera.FocusStepperUpperLimit.GetValue())

buttonAWB = ttk.Button(win, text="Auto White blance", command=AWB, style="TButton")
buttonAWB.place(x=25,y=460)
buttonLL = ttk.Button(win, text="Reconnect to Lens", command=reconnectLL, style="TButton")
buttonLL.place(x=25,y=495)
# buttonFFC_cal = ttk.Button(tab2, text="FFC calculation", command=thread_FFC_cal, style="TButton")
# buttonFFC_cal.grid(row=1,column=0,sticky=tk.W)
# buttonAFstart = ttk.Button(win, text="AF demo", command=AFdemo_Thread, style="TButton")
# buttonAFstart.place(x=25,y=525)

# t =threading.Thread(target=mouseclickAF)
# t.start()
AFdemo_Thread()

Basler=Image.open('logo_basler.png')
Basler=ImageTk.PhotoImage(Basler.resize((100,50)))


BaslerLabel_2=tk.Label(win,image=Basler)
BaslerLabel_2.place(x=10,y=0)





win.protocol("WM_DELETE_WINDOW", on_closing)
win.mainloop()





