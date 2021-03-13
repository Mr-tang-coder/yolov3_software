from PyQt5.QtWidgets import QMainWindow,QDesktopWidget,QMessageBox,QFileDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *
from designer.visualization import *
from PyQt5 import QtGui
import sys
import os
from PIL import Image
from yolo import YOLO,detect_video
from PyQt5.QtGui import QIcon
import glob



class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

class MainWindow(QMainWindow,Ui_Form):
    def __init__(self):
        super(MainWindow, self).__init__()
        # self.setWindowTitle("目标检测")

        self.yolo = YOLO()

        self.setupUi(self)
        self.center()

        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        # sys.stder = EmittingStream(textWritten=self.normalOutputWritten)

        # 设置窗口
        self.setWindowTitle("目标检测")
        self.setWindowIcon(QIcon("../logo/yolo.jpg"))

        # 系统参数初始化
        self.sys_parameter_initialization()

        self.pb_quit.clicked.connect(self.set_quit)

        self.load_model.clicked.connect(self.load_model_fun)
        self.load_class.clicked.connect(self.load_class_fun)

        self.btn_img.clicked.connect(self.load_img)
        self.btn_batch_img.clicked.connect(self.load_batch_img)
        self.btn_v.clicked.connect(self.load_video)

        self.refresh.clicked.connect(self.refresh_fun)

        self.OpenDirBtn.clicked.connect(self.OpenOutImgDir)
        self.PreImBtn.clicked.connect(self.PreIm)
        self.NextImBtn.clicked.connect(self.NextIm)

        self.recognize_img.clicked.connect(self.recongnition_fun)
        self.v_det_btn.clicked.connect(self.recongnition_v_fun)



        # 窗口居中

    def center(self):
        # 获得窗口
        framePos = self.frameGeometry()
        # 获得屏幕中心点
        scPos = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        framePos.moveCenter(scPos)
        self.move(framePos.topLeft())

        # 窗口关闭事件

    def set_quit(self):
        reply = QMessageBox.question(self, '提示',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            QCoreApplication.instance().quit()
        else:
            pass

    # 参数初始化
    def sys_parameter_initialization(self):
        self.te_screen_display.clear()
        print("系统初始化为空.........")
        self.flag = 0
        self.flag_batch = 0
        self.rec_pic_path = ""
        self.recongnit_batchs_path = ""
        self.rec_v_path = ''
        self.model_path = ""
        self.class_path = ''
        self.label_img_show.clear()

        self.ImFolder = ''
        self.ImNameSet = ""
        self.CurImId = 0

        self.output_v_path = '../video'

        # 设置输入文件路径
        self.img_path.setText(self.rec_pic_path)
        self.batch_img_path.setText(self.recongnit_batchs_path)
        self.video_path.setText(self.rec_v_path)
        self.load_model_path.setText(self.model_path)
        self.load_class_path.setText(self.class_path)
        return

    # 刷新识别区域
    def refresh_fun(self):
        self.sys_parameter_initialization()

    def load_model_fun(self):

        self.load_model_path.clear()
        model_path, model_type = QFileDialog.getOpenFileNames(self, "选择权重文件", "../", "Text Files (*.h5)")

        if len(model_path):

            for each_path in model_path:
                if ".h5" not in each_path or not os.path.exists(each_path):
                    QMessageBox.warning(self, "提示", "文件选择错误，请重新选择！")
                    return

            self.model_path = model_path[0]
            self.load_model_path.setText(self.model_path)
            print("加载模型文件:", self.model_path)
            return

        else:
            return
        pass

    # 加载类别文件
    def load_class_fun(self):

        self.load_class_path.clear()

        classes_path, dir_type = QFileDialog.getOpenFileNames(self, "选择分类文件","../", "Text Files (*.txt)")
        # print("11111",input_dir_path)
        # 判断文件合法性
        if len(classes_path):
            for each_path in classes_path:
                if ".txt" not in each_path or not os.path.exists(each_path):
                    QMessageBox.warning(self, "提示", "文件选择错误，请重新选择！")
                    return

            self.class_path = classes_path[0]
            self.load_class_path.setText(self.class_path)
            print("输入训练文件:", self.class_path)
            return
        else:
            return
        pass

    # 加载单张图片
    def load_img(self):
        if self.flag_batch and self.batch_img_path.text():
            QMessageBox.warning(self, "提示", "批量图片已加载，不能再加载单张图片！")
            return
        else:
            self.flag=1
            self.img_path.clear()

            recong_img_path, dir_type = QFileDialog.getOpenFileNames(self, "选择图片文件","../","*.jpg;;*.png;;*.bmp;;*.jpeg")
            # print("11111",input_dir_path)
            # 判断文件合法性
            if len(recong_img_path):
                for each_path in recong_img_path:
                    temp=each_path.split(".")[-1]
                    if temp not in ["jpg","bmp","JPG","jpeg","BMP"] and not os.path.exists(each_path):
                        QMessageBox.warning(self, "提示", "文件选择错误，请重新选择！")
                        return
                    self.rec_pic_path = recong_img_path[0]
                    self.img_path.setText(self.rec_pic_path)
                    print("识别图片:", self.rec_pic_path)
                    return
            else:
                self.flag=0
                return
            pass

    def load_batch_img(self):
        if self.flag and self.img_path.text():
            QMessageBox.warning(self, "提示", "已加载单张图片，不能再批量加载")
            return
        else:
            self.flag_batch=1
            self.batch_img_path.clear()
            temp_recongnit_path = QFileDialog.getExistingDirectory(self, "输入文件路径", "../")
            if not os.path.exists(temp_recongnit_path):
                QMessageBox.warning(self, "提示", "输入文件目录不存在，请重新选择")
                self.flag_batch=0
                return
            self.recongnit_batchs_path = temp_recongnit_path
            self.batch_img_path.setText(self.recongnit_batchs_path)
            print("识别的图片文件夹:", self.recongnit_batchs_path)

    def load_video(self):
        self.video_path.clear()
        recong_video_path, dir_type = QFileDialog.getOpenFileNames(self, "选择视频文件", "../",
                                                                 "*.mp4")
        # print("11111",input_dir_path)
        # 判断文件合法性
        if len(recong_video_path):
            for each_path in recong_video_path:
                temp = each_path.split(".")[-1]
                if temp not in ["mp4", "avi"] and not os.path.exists(each_path):
                    QMessageBox.warning(self, "提示", "请重新选择！")
                    return
                self.rec_v_path = recong_video_path[0]
                self.video_path.setText(self.rec_v_path)
                print("识别图片:", self.rec_v_path)
                return


    def get_paths(self, single_pic_path,bach_path, weights_path, classes_path):
        self.img_path = single_pic_path
        self.batch_img_path = bach_path
        self.load_model_path = weights_path
        self.load_class_path = classes_path
        return

    def get_path_v(self,video_path,weights_path,classes_path):
        self.video_path=video_path
        self.load_model_path = weights_path
        self.load_class_path = classes_path
        return

    def detect_single_pic(self):
        img = Image.open(self.img_path)
        # yolo1 = YOLO()
        self.yolo.get_path(self.load_model_path, self.load_class_path)
        img = self.yolo.detect_image(img)
        # 保存图片
        spl = self.img_path.split(".")

        outdir = spl[0] + "_result" + "." + spl[-1]
        img.save(outdir)
        self.yolo.close_session()
        # yolo1.close_session()
        return (img, outdir)

    def args_test(self):
        (img, outdir) = self.detect_single_pic()
        return (img, outdir)

    def detect_img(self):
        path = self.batch_img_path + "/*.jpg"
        # outdir = "VOC2007/SegmentationClass"
        outdir = self.batch_img_path + "/Result"
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        # yolo2 = YOLO()
        print(self.load_model_path)
        self.yolo.get_path(self.load_model_path, self.load_class_path)
        for jpgfile in glob.glob(path):
            # print("imgfile",jpgfile)
            img = Image.open(jpgfile)
            img = self.yolo.detect_image(img)
            img.save(os.path.join(outdir, os.path.basename(jpgfile)))
        self.yolo.close_session()
        return

    def args(self):
        self.detect_img()
        return

        # 识别图片
    def recongnition_fun(self):
            self.label_img_show.clear()
            model_path = self.load_model_path.text()
            classes_path = self.load_class_path.text()
            sigle_pic_path = self.img_path.text()
            batchs_pics_path = self.batch_img_path.text()


            # 判断加载文件的合法性
            if not model_path:
                QMessageBox.warning(self, "提示", "请加载模型！")
                return
            elif not classes_path:
                QMessageBox.warning(self, "提示", "请选择类型！")
                return
            elif not sigle_pic_path and not batchs_pics_path:
                QMessageBox.warning(self, "提示", "请选择识别图片！")
                return
            else:
                pass
            # 识别单张图并显示
            if len(sigle_pic_path):
                self.get_paths(sigle_pic_path,batchs_pics_path,model_path,classes_path)
                (img, outdir) = self.args_test()
                image = QtGui.QPixmap(outdir).scaled(self.label_img_show.width(), self.label_img_show.height())
                self.label_img_show.setPixmap(image)
                return

            if len(batchs_pics_path):
                self.get_paths(sigle_pic_path, batchs_pics_path, model_path, classes_path)
                self.args()
                return
            pass

    def detect_v(self):
        self.yolo.get_path(self.load_model_path, self.load_class_path)
        detect_video(self.yolo,self.video_path,self.output_v_path)

    def args_test_v(self):
        self.detect_v()
        return

    def recongnition_v_fun(self):
        model_path = self.load_model_path.text()
        classes_path = self.load_class_path.text()
        video_path = self.video_path.text()


        # 判断加载文件的合法性
        if not model_path:
            QMessageBox.warning(self, "提示", "请加载模型！")
            return
        elif not classes_path:
            QMessageBox.warning(self, "提示", "请选择类型！")
            return
        elif not video_path:
            QMessageBox.warning(self, "提示", "请选择识别的视频！")
            return
        else:
            pass
        # 识别单张图并显示
        if len(video_path):
            self.get_path_v(video_path, model_path, classes_path)
            self.args_test_v()
            return



    def OpenOutImgDir(self):
        ImFolder = QFileDialog.getExistingDirectory(self, "输入文件路径",  "../")
        if ImFolder!='':
            self.label_img_show.clear()
            ImNameSet = os.listdir(ImFolder)
            ImNameSet.sort()
            ImPath = os.path.join(ImFolder, ImNameSet[0])
            pix = QtGui.QPixmap(ImPath).scaled(self.label_img_show.width(), self.label_img_show.height())
            self.label_img_show.setPixmap(pix)

            self.ImFolder = ImFolder
            self.ImNameSet = ImNameSet
            return
        else:
            QMessageBox.warning(self, "提示", "请重新选择文件！")
            return

    def NextIm(self):
        if self.flag or self.flag_batch or self.ImFolder!='':
            ImFolder = self.ImFolder
            ImNameSet = self.ImNameSet
            CurImId = self.CurImId
            ImNum = len(ImNameSet)
            # print(ImNum)
            if CurImId<ImNum-1:
                self.label_img_show.clear()
                ImPath = os.path.join(ImFolder, ImNameSet[CurImId + 1])
                pix = QtGui.QPixmap(ImPath).scaled(self.label_img_show.width(), self.label_img_show.height())
                self.label_img_show.setPixmap(pix)
                print(ImNameSet[CurImId - 1])
                self.CurImId = CurImId + 1
                return
            else:
                QMessageBox.information(self, "提示", "已是最后一张")
                return
        else:
            QMessageBox.information(self, "提示", "请加载图片")
            return
            pass


    def PreIm(self):
        if self.flag or self.flag_batch or self.ImFolder!='':
            ImFolder = self.ImFolder
            ImNameSet = self.ImNameSet
            CurImId = self.CurImId
            ImNum = len(ImNameSet)
            if self.CurImId < 0:
                self.CurImId = 0
            if CurImId>0:
                self.label_img_show.clear()
                ImPath = os.path.join(ImFolder, ImNameSet[CurImId - 1])
                pix = QtGui.QPixmap(ImPath).scaled(self.label_img_show.width(), self.label_img_show.height())
                self.label_img_show.setPixmap(pix)
                print(ImNameSet[CurImId - 1])
                self.CurImId = CurImId - 1
                return
            else:
                QMessageBox.information(self, "提示", "已是第一张")
                return
        else:
            QMessageBox.information(self, "提示", "请加载图片")
            return
            pass


    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.te_screen_display.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.te_screen_display.setTextCursor(cursor)
        self.te_screen_display.ensureCursorVisible()

    # def jump_to_video_dialog(self):        #这一块注意，是重点从主界面跳转到Demo1界面，主界面隐藏，如果关闭Demo界面，主界面进程会触发self.form.show()会再次显示主界面
    #          self.hide()            #如果没有self.form.show()这一句，关闭Demo1界面后就会关闭程序
    #          form= QtWidgets.QDialog()
    #          ui = video_dialog.Ui_Dialog()
    #          ui.setupUi(form)
    #          form.show()
    #          form.exec_()
    #          self.show()





if __name__ == "__main__":
    app = QApplication(sys.argv)
    Gui = MainWindow()
    Gui.show()
    # app.exec_()
    sys.exit(app.exec_())

