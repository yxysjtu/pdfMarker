from PyQt5 import QtCore, QtWidgets, QtGui
from win32api import GetSystemMetrics
import fitz
from MyWidgets import *
import math
from lib import windowCapture, docManager, sqlManager, pdfProcessor
import threading


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.width = GetSystemMetrics(0)
        self.height = GetSystemMetrics(1)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(self.width/2, self.height/2)

        self.groupBox = QtWidgets.QGroupBox(MainWindow)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, self.width, self.height//24))

        self.add_btn = MyButton(self.groupBox,
                          name="add_btn",
                          pos=(0, 0, self.groupBox.height(), self.groupBox.height()),
                          img=(r'./icon/add_btn.bmp',
                               r'./icon/add_btn_click.bmp',
                               r'./icon/add_btn_hover.bmp'),
                          clickfunc=self.add_btn_click)
        self.home_btn = MyButton(self.groupBox,
                          name="home_btn",
                          pos=(self.groupBox.height()+5, 0, self.groupBox.height(), self.groupBox.height()),
                          img=(r'./icon/home_btn.bmp',
                               r'./icon/home_btn_click.bmp',
                               r'./icon/home_btn_hover.bmp'),
                          clickfunc=self.home_btn_click)

        self.tabWidget = QtWidgets.QTabWidget(self.groupBox)
        self.tabWidget.setGeometry(QtCore.QRect(self.groupBox.height()*2+10, 0, self.groupBox.width()-self.groupBox.height()*2-10, self.groupBox.height()))
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested[int].connect(self.remove_tab)
        tab = QtWidgets.QTabWidget()
        self.tabWidget.insertTab(0, tab, "home")
        self.tabWidget.setTabVisible(0, False)
        self.tabs = []

        self.tableWidget = QtWidgets.QTableWidget(MainWindow)
        self.tableWidget.setGeometry(QtCore.QRect(0, self.groupBox.height(), self.width, self.height-self.groupBox.height()))
        self.c = 8
        self.r = 3
        self.tableWidget.setRowCount(self.r)
        self.tableWidget.setColumnCount(self.c)
        for i in range(self.c):
            self.tableWidget.setColumnWidth(i, self.tableWidget.width()//self.c)
        for i in range(self.r):
            self.tableWidget.setRowHeight(i, self.tableWidget.height()//self.r)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        #self.tableWidget.setShowGrid(False)
        # menu
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.generateMenu)
        self.tableWidget.clicked.connect(self.tableClick)

        #book layout
        self.groupBox2 = QtWidgets.QGroupBox(MainWindow)
        self.groupBox2.setGeometry(QtCore.QRect(0, self.groupBox.height(), self.width, self.height//20))
        self.groupBox2.setStyleSheet("background-color: #303030")
        self.bookmark_btn = MyButton(self.groupBox2,
                          name="bookmark_btn",
                          pos=(self.width-self.groupBox2.height()-5, self.groupBox2.height()/6, self.groupBox2.height()*3/4, self.groupBox2.height()*3//4),
                          img=(r'./icon/bookmark_btn.bmp',
                               r'./icon/bookmark_btn_click.bmp',
                               r'./icon/bookmark_btn_hover.bmp'),
                          clickfunc=self.bookmark_btn_click)
        self.pageEdit = QtWidgets.QLineEdit(self.groupBox2)
        self.pageEdit.setGeometry(QtCore.QRect(self.groupBox2.width()//2-self.width//30, self.groupBox2.height()/6, self.width//30, self.groupBox2.height()//3*2))
        self.pageEdit.setStyleSheet("""background-color: black; 
                                       font-size: 20px;
                                       font-family: 微软雅黑;
                                       border:0px solid red;
                                       color: white""")
        self.pageEdit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        labelStyle = """font-size: 20px;
                        font-family: 微软雅黑;
                        border:0px solid red;
                        color: white"""
        self.pageLabel = QtWidgets.QLabel(self.groupBox2)
        self.pageLabel.setGeometry(QtCore.QRect(self.groupBox2.width()//2, self.groupBox2.height()/6, self.width//10, self.groupBox2.height()//3*2))
        self.pageLabel.setText(" / ")
        self.pageLabel.setStyleSheet(labelStyle)
        self.bookName = QtWidgets.QLabel(self.groupBox2)
        self.bookName.setGeometry(QtCore.QRect(self.groupBox2.width()//30, self.groupBox2.height()/6, self.width//3, self.groupBox2.height()//3*2))
        self.bookName.setStyleSheet(labelStyle)
        self.editbox_btn = MyStateButton(self.groupBox2,
                          name="editbox_btn",
                          pos=(self.width-self.groupBox2.height()*2-10, self.groupBox2.height()/6, self.groupBox2.height()*3/4, self.groupBox2.height()*3//4),
                          img=(r'./icon/editbox_btn.bmp',
                               r'./icon/editbox_btn_click.bmp'),
                          clickfunc=self.editbox_btn_click)
        self.textEdit_btn = MyStateButton(self.groupBox2,
                          name="textEdit_btn",
                          pos=(self.width-self.groupBox2.height()*3-15, self.groupBox2.height()/6, self.groupBox2.height()*3/4, self.groupBox2.height()*3//4),
                          img=(r'./icon/textEdit_btn.bmp',
                               r'./icon/textEdit_btn_click.bmp'),
                          clickfunc=self.textEdit_btn_click)

        self.graphicView = QtWidgets.QGraphicsView(MainWindow)
        self.graphicView.setGeometry(QtCore.QRect(0,self.groupBox2.y()+self.groupBox2.height(),self.width,self.height-self.groupBox2.y()-self.groupBox2.height()-100))
        self.graphicView.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.graphicView.setSceneRect(0,0,self.graphicView.width(),self.graphicView.height())
        self.graphicView.setStyleSheet("""background-color: #808080;
                              padding: 0px; 
                              border: 0px;""")
        self.graphicView.setMouseTracking(True)
        self.graphicView.mouseMoveEvent = self.cursorMoveEvent

        self.area = QtWidgets.QGraphicsScene()
        self.pdfScreen = QtWidgets.QGraphicsPixmapItem()
        self.pdfScreen2 = QtWidgets.QGraphicsPixmapItem()
        self.area.addItem(self.pdfScreen)
        self.area.addItem(self.pdfScreen2)
        self.mouseBox = MyGroup(widget=self)
        self.mouseBox2 = MyGroup2(widget=self)
        self.textEdit = QtWidgets.QTextEdit(self.graphicView)
        self.textEdit.setStyleSheet("""background-color: transparent; 
                                       font-size: 20px;
                                       font-family: 微软雅黑;
                                       border:2px dashed blue;
                                       color: black""")
        self.textEdit.setText("")
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit.hide()
        self.editMode = 0
        
        self.area.addItem(self.mouseBox)
        self.area.addItem(self.mouseBox2)
        self.area.mousePressEvent = self.myMousePressEvent
        self.area.mouseReleaseEvent = self.myMouseReleaseEvent
        self.graphicView.setScene(self.area)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical, self.graphicView)
        self.slider.setGeometry(QtCore.QRect(self.width-self.width//80,0,self.width//80,self.graphicView.height()))
        self.slider.valueChanged.connect(self.valChange)
        self.slider.setStyleSheet("background-color: transparent;")
        self.slider2 = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal, self.graphicView)
        self.slider2.setGeometry(QtCore.QRect(0,self.graphicView.height()-self.width//80,self.graphicView.width(),self.width//80))
        self.slider2.valueChanged.connect(self.valChange2)
        self.slider2.setStyleSheet("background-color: transparent;")
        self.slider2.hide()
        self.bookmark =QtWidgets.QTreeWidget(self.graphicView)
        self.bookmark.setGeometry(QtCore.QRect(self.graphicView.width()*2//3, 0, self.graphicView.width()//3-20, self.graphicView.height()//2))
        self.bookmark.setColumnCount(2)
        self.bookmark.setHeaderLabels(['','page'])
        self.bookmark.setColumnWidth(0, self.bookmark.width()*5//6)
        self.bookmark.setColumnWidth(1, self.bookmark.width()//10)
        self.bookmark.setStyleSheet("background-color: white")
        self.bookmark.clicked.connect(self.bookmark_click)
        self.bookmark.hide()
        self.plus_btn = MyButton(self.graphicView,
                          name="plus_btn",
                          pos=(self.graphicView.width()*19//20, self.graphicView.height()*3//4, self.groupBox2.height(), self.groupBox2.height()),
                          img=(r'./icon/plus_btn.png',
                               r'./icon/plus_btn_click.png',
                               r'./icon/plus_btn_click.png'),
                          clickfunc=self.plus_btn_click)
        self.minus_btn = MyButton(self.graphicView,
                          name="minus_btn",
                          pos=(self.plus_btn.x(), self.plus_btn.height()+self.plus_btn.y()+10, self.groupBox2.height(), self.groupBox2.height()),
                          img=(r'./icon/minus_btn.png',
                               r'./icon/minus_btn_click.png',
                               r'./icon/minus_btn_click.png'),
                          clickfunc=self.minus_btn_click)
        self.editToolbar = QtWidgets.QToolBar(self.graphicView)
        copy_img = QtWidgets.QAction(QtGui.QIcon(r'./icon/copy_img_btn.bmp'), "copy_img", self.editToolbar)
        self.editToolbar.addAction(copy_img)
        copy_text = QtWidgets.QAction(QtGui.QIcon(r'./icon/copy_text_btn.bmp'), "copy_text", self.editToolbar)
        self.editToolbar.addAction(copy_text)
        save = QtWidgets.QAction(QtGui.QIcon(r'./icon/save_btn.bmp'), "save", self.editToolbar)
        self.editToolbar.addAction(save)
        copy = QtWidgets.QAction(QtGui.QIcon(r'./icon/copy_btn.bmp'), "copy", self.editToolbar)
        self.editToolbar.addAction(copy)
        self.editToolbar.actionTriggered[QtWidgets.QAction].connect(self.editToolbar_click)
        self.editToolbar.setStyleSheet("background-color: transparent;")
        self.editToolbar.hide()
        self.editToolbar2 = QtWidgets.QToolBar(self.graphicView)
        self.editToolbar2.setStyleSheet("background-color: transparent;")
        ok = QtWidgets.QAction(QtGui.QIcon(r'./icon/copy_btn.bmp'), "ok", self.editToolbar2)
        self.editToolbar2.addAction(ok)
        self.editToolbar2.actionTriggered[QtWidgets.QAction].connect(self.editToolbar2_click)
        self.editToolbar2.hide()
        self.textBrowser = QtWidgets.QTextBrowser(self.graphicView)
        self.textBrowser.setStyleSheet("""background-color: white;
                                       font-size: 20px;
                                       font-family: 微软雅黑;""")
        self.textBrowser.hide()

        #find layout
        self.findGroup = QtWidgets.QGroupBox(self.graphicView)
        self.findGroup.setGeometry(QtCore.QRect(self.width*3//4, 0, self.width//4, self.height//20))
        self.findGroup.setStyleSheet("background-color: white; border: 2px solid grey")
        self.up_btn = MyButton(self.findGroup,
                          name="up_btn",
                          pos=(self.findGroup.width()-self.findGroup.height()*3, self.findGroup.height()//6, self.findGroup.height()*3//4, self.findGroup.height()*3//4),
                          img=(r'./icon/up_btn.bmp',
                               r'./icon/up_btn_click.bmp',
                               r'./icon/up_btn_click.bmp'),
                          clickfunc=self.up_btn_click)
        self.down_btn = MyButton(self.findGroup,
                          name="down_btn",
                          pos=(self.findGroup.width()-self.findGroup.height()*2, self.findGroup.height()//6, self.findGroup.height()*3//4, self.findGroup.height()*3//4),
                          img=(r'./icon/down_btn.bmp',
                               r'./icon/down_btn_click.bmp',
                               r'./icon/down_btn_click.bmp'),
                          clickfunc=self.down_btn_click)
        self.cross_btn = MyButton(self.findGroup,
                          name="cross_btn",
                          pos=(self.findGroup.width()-self.findGroup.height(), self.findGroup.height()//6, self.findGroup.height()*3//4, self.findGroup.height()*3//4),
                          img=(r'./icon/cross_btn.bmp',
                               r'./icon/cross_btn_click.bmp',
                               r'./icon/cross_btn_click.bmp'),
                          clickfunc=self.cross_btn_click)
        self.findEdit = QtWidgets.QLineEdit(self.findGroup)
        self.findEdit.setGeometry(QtCore.QRect(10, self.findGroup.height()/6, self.findGroup.width()//3, self.findGroup.height()//3*2))
        self.findEdit.setStyleSheet("""background-color: white; 
                                       font-size: 20px;
                                       font-family: 微软雅黑;
                                       border:0px solid red;
                                       color: black""")
        labelStyle2 = """font-size: 20px;
                        font-family: 微软雅黑;
                        border:0px solid red;
                        color: grey"""
        self.findLabel = QtWidgets.QLabel(self.findGroup)
        self.findLabel.setGeometry(QtCore.QRect(self.findEdit.x()+self.findEdit.width(), self.groupBox2.height()/6, self.up_btn.x()-self.findEdit.x()-self.findEdit.width(), self.groupBox2.height()//3*2))
        self.findLabel.setText("0/0")
        self.findLabel.setStyleSheet(labelStyle2)
        self.findLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.findGroup.hide()

        self.div = 1000
        self.dx = 20
        self.scale = 2
        self.graphicView.hide()
        self.groupBox2.hide()
        self.w = 0
        self.h = 0
        self.page = None
        self.page1 = None
        self.words = None
        self.words1 = None
        self.mousePressed = False

        #database
        db = sqlManager.SqlManager("./data/bookshelf.db")
        db.createTable(name="bookshelf", field={"path":sqlManager.FieldType.text,"page":sqlManager.FieldType.integer})
        self.bookshelf = db.select(field=("path","page"))
        db.close()
        
        i = 0
        while i < len(self.bookshelf):
            try:
                self.setCover(i)
                i += 1
            except BaseException:
                self.bookshelf.pop(i)

        self.mode = 0
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "pdfMarker"))

    def editToolbar2_click(self, a):
        index = self.inPdfScreen(self.mouseBox.x(),self.mouseBox.y())
        page = None
        if index == 1:
            page = self.page
        elif index == 2:
            page = self.page1
        if a.text() == "ok" and page != None:
            text = self.textEdit.toPlainText()
            if len(text) > 0:
                page.insert_textbox(fitz.Rect(self.mouseBox.rx,self.mouseBox.ry-40,self.mouseBox.rx1,self.mouseBox.ry1-40), buffer=text,fontsize=11)

                zoom_matrix = fitz.Matrix(self.scale, self.scale)
                pagePixmap = page.get_pixmap(matrix = zoom_matrix, alpha=False) 
                pageQImage = QtGui.QImage(pagePixmap.samples, pagePixmap.width, pagePixmap.height, pagePixmap.stride, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap()
                pixmap.convertFromImage(pageQImage)

                if index == 1:
                    self.pdfScreen.setPixmap(pixmap)
                elif index == 2:
                    self.pdfScreen2.setPixmap(pixmap)

                self.tabs[self.tabWidget.currentIndex()][3] = True

                tocName = None
                doc = self.tabs[self.tabWidget.currentIndex()][2]
                docx = self.tabs[self.tabWidget.currentIndex()][4]
                for toc in doc.get_toc():
                    if toc[2] > self.mouseBox2.page:
                        tocName = toc[1]
                        break
                if tocName != None:
                    docx.add_text("[" + text + "]    ----(P" + str(self.mouseBox.page+1) + " in " + tocName +")", style="Intense Quote")
                else:
                    docx.add_text("[" + text + "]    ----(P" + str(self.mouseBox.page+1) + ")", style="Intense Quote")
                self.reset()

    def editToolbar_click(self, a):
        index = self.inPdfScreen(self.mouseBox.x(),self.mouseBox.y())
        pixmap2 = None
        
        if a.text() == "copy_text":
            str = []
            for i in range(len(self.mouseBox.blockRects)):
                b = self.mouseBox.blockRects[i]
                if len(b[1][4]) > 6:
                    if b[1][4][:6] == "<image":
                        continue
                #str.append([s0.rstrip("-") for s0 in b[1][4].split("\n")])
                str.append(b[1][4].replace("\n-", "").replace("-\n", "").replace("\n", " "))
            str1 = "".join(str)
            str2 = " ".join(str1.split())
            windowCapture.copystr(str2)
            
        elif a.text() == "copy_img":
            page = None
            doc = self.tabs[self.tabWidget.currentIndex()][2]
            pageNum = self.tabs[self.tabWidget.currentIndex()][1] + index - 1
            page = doc.load_page(pageNum)
            
            img_xref = []
            img_info = page.get_image_info(False, True)
            for b in self.mouseBox.blockRects:
                if len(b[1][4]) > 6:
                    if b[1][4][:6] == "<image":
                        brect = b[1][:4]
                        for img in img_info:
                            if img['bbox'][0] == brect[0] and img['bbox'][1] == brect[1] and img['bbox'][2] == brect[2] and img['bbox'][3] == brect[3]:
                                if img['xref'] != 0:
                                    img_xref.append(img['xref'])
                                    break
                        if len(img_xref) > 0:
                            pagePixmap= fitz.Pixmap(doc, img_xref[0])
                            fname = "./data/temp.bmp"
                            pageQImage = QtGui.QImage(pagePixmap.samples, pagePixmap.width, pagePixmap.height, pagePixmap.stride, QtGui.QImage.Format_RGB888)
                            pixmap = QtGui.QPixmap()
                            pixmap.convertFromImage(pageQImage)
                            pixmap.save(fname)
                            windowCapture.copyboard(fname)
                                       
        else:
            if index == 1:
                dx = self.mouseBox.x() - self.pdfScreen.x()
                dy = self.mouseBox.y() - self.pdfScreen.y()
                pixmap2 = self.pdfScreen.pixmap().copy(dx, dy, self.mouseBox.rect.width(), self.mouseBox.rect.height())
            elif index == 2:
                dx = self.mouseBox.x() - self.pdfScreen2.x()
                dy = self.mouseBox.y() - self.pdfScreen2.y()
                pixmap2 = self.pdfScreen2.pixmap().copy(dx, dy, self.mouseBox.rect.width(), self.mouseBox.rect.height())
            
            if a.text() == "copy":
                fname = "./data/temp.bmp"
                pixmap2.save(fname)
                windowCapture.copyboard(fname)     
                docx = self.tabs[self.tabWidget.currentIndex()][4]
                docx.add_img(fname)   
                self.tabs[self.tabWidget.currentIndex()][3] = True
            elif a.text() == "save":
                fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'save img', './', '(*.bmp)')
                pixmap2.save(fname)

        self.mouseBox.hide()

    def inPdfScreen(self, x, y):
        x1 = self.pdfScreen.x()
        y1 = self.pdfScreen.y()
        x2 = self.pdfScreen2.x()
        y2 = self.pdfScreen2.y()
        w = self.w
        h = self.h
        if x > x1 and x < x1 + w and y > y1 and y < y1 + h:
            return 1
        if x > x2 and x < x2 + w and y > y2 and y < y2 + h:
            return 2
        return 0

    def reset(self):
        self.editMode = 0
        self.editbox_btn.state = False
        self.editbox_btn.update()
        self.textEdit_btn.state = False
        self.textEdit_btn.update()
        self.findGroup.hide()
        self.mouseBox.hide()
        self.mouseBox2.hide()

    def cursorMoveEvent(self, e):
        x0, y0 = e.x(), e.y()
        rx, ry = 0, 0
        scale = self.scale
        index = self.inPdfScreen(x0, y0)
        words = None
    
        if index == 1:
            rx = (x0 - self.pdfScreen.x())/scale
            ry = (y0 - self.pdfScreen.y())/scale
            words = self.words
        elif index == 2:
            rx = (x0 - self.pdfScreen2.x())/scale
            ry = (y0 - self.pdfScreen2.y())/scale
            words = self.words1
        
        cflag = False
        if words != None:
            for w in words:
                if self.mouseBox.inRange(rx,ry,*(w[:4])):
                    self.graphicView.setCursor(QtCore.Qt.CursorShape.IBeamCursor)
                    cflag = True
                    break
        if not cflag:
            self.graphicView.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

        if self.mousePressed:
            if (self.editMode == 1 or self.editMode == 2) and self.mouseBox.isVisible():
                x = self.mouseBox.x()
                y = self.mouseBox.y()
                
                self.mouseBox.setRect(x, y, x0, y0)
            elif self.mouseBox2.isVisible():
                x = self.mouseBox2.x()
                y = self.mouseBox2.y()
                    
                self.mouseBox2.setRect(x, y, x0, y0)

    def myMousePressEvent(self, e):
        self.mousePressed = True
        
        self.mouseBox2.hide()
        if self.findGroup.isHidden():
            self.mouseBox.hide()

        point = e.scenePos()
        index = self.inPdfScreen(point.x(), point.y())
            
        if self.editMode == 1 or self.editMode == 2:
            if index:
                self.mouseBox.page = int(self.pageEdit.text()) - 2 + index
                self.mouseBox.setRect(point.x(), point.y(), point.x(), point.y(), update=True)
                self.mouseBox.setVisible(True)
        elif self.editMode == 0:
            if index:
                self.mouseBox2.page = int(self.pageEdit.text()) - 2 + index
                self.mouseBox2.setRect(point.x(), point.y(), point.x(), point.y(), update=True)
                self.mouseBox2.setVisible(True)

    def myMouseReleaseEvent(self, e):
        self.mousePressed = False

        if self.editMode == 1:
            self.editToolbar.move(self.mouseBox.x()+self.mouseBox.rect.width(), self.mouseBox.y()+self.mouseBox.rect.height())
            self.editToolbar.show()

            self.mouseBox.blocks = []
        elif self.editMode == 2:
            minw = 120
            minh = 20
            if self.mouseBox.rx1 - self.mouseBox.rx < minw:
                self.mouseBox.rx1 = self.mouseBox.rx + minw
            if self.mouseBox.ry1 - self.mouseBox.ry < minh:
                self.mouseBox.ry1 = self.mouseBox.ry + minh

            self.mouseBox.rect.setSize(self.mouseBox.rx1-self.mouseBox.rx,self.mouseBox.ry1-self.mouseBox.ry)
            self.textEdit.setText("")
            self.textEdit.setGeometry(QtCore.QRect(self.mouseBox.x(),self.mouseBox.y(),self.mouseBox.rect.width(), self.mouseBox.rect.height()))
            self.textEdit.show()
            self.editToolbar2.move(self.mouseBox.x()+self.mouseBox.rect.width(), self.mouseBox.y()+self.mouseBox.rect.height())
            self.editToolbar2.show()

    def mythread(self):
        text = self.findEdit.text() 
        doc = self.tabs[self.tabWidget.currentIndex()][2]
        pageNum = doc.page_count
        findFlag = False
        for i in range(pageNum):
            page = doc.load_page(i)
            wordlist = page.search_for(text)
            for w in wordlist:
                self.wordlist.append([w,i])
            if len(self.wordlist) > 0 and not findFlag:
                self.setFindBox(0)
            self.findLabel.setText(self.findLabel.text().split("/")[0] + "/" + str(len(self.wordlist)))

    def find_click(self):
        self.editMode = 3 
        self.findLabel.setText("0/0") 
        self.wordlist = []
        t1 = threading.Thread(target=self.mythread)
        t1.start()
            
    def setFindBox(self, index):
        pageNum = self.wordlist[index][1]
        self.findLabel.setText(str(index+1) + "/" + str(len(self.wordlist)))
        self.mouseBox.page = pageNum
        self.slider.setValue(self.slider.maximum() - pageNum*self.div - self.wordlist[index][0].tl.y*self.scale*self.div//self.pdfScreen.pixmap().height()+50)

        rect = self.wordlist[index][0]
        self.mouseBox.rx = rect.tl.x
        self.mouseBox.ry = rect.tl.y
        
        self.mouseBox.setPos(self.pdfScreen.x()+rect.tl.x*self.scale, self.pdfScreen.y()+rect.tl.y*self.scale)
        self.mouseBox.rect.setRect(0,0,rect.tr.x-rect.tl.x,rect.br.y-rect.tr.y)
        self.mouseBox.setVisible(True)

    def up_btn_click(self):
        num = self.findLabel.text().split("/")
        current_word = int(num[0])
        
        if current_word > 1:
            current_word -= 1
            
        self.setFindBox(current_word-1)

    def down_btn_click(self):
        num = self.findLabel.text().split("/")
        current_word = int(num[0])
        total_word = int(num[1])
        
        if current_word < total_word:
            current_word += 1
            
        self.setFindBox(current_word-1)

    def cross_btn_click(self):
        self.reset()

    def editbox_btn_click(self):
        if self.editMode == 0:
            self.editMode = 1
        elif self.editMode == 1:
            self.reset()

    def textEdit_btn_click(self):
        if self.editMode != 2:
            self.editMode = 2
        else:
            self.reset()

    def add_btn_click(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open files', './', '(*.pdf)')
        if fname.split(".")[-1] == "pdf":
            if fname not in [x[0] for x in self.bookshelf]:
                self.bookshelf.append([fname,0])
                self.setCover(len(self.bookshelf)-1)
    
    def home_btn_click(self):
        self.home()
    
    def bookmark_click(self, index):
        item = self.bookmark.currentItem()
        pageNum = int(item.text(1)) - 1
        print(pageNum)
        self.slider.setValue(self.slider.maximum() - pageNum*self.div)

    def bookmark_btn_click(self):
        self.bookmark.clear()
        toc = self.tabs[self.tabWidget.currentIndex()][2].get_toc()
        toc.insert(0, [0, "Cover", 0])

        def connectParent(parent, index, toc): #dfs
            i = index + 1
            while i < len(toc):
                d = toc[i][0] - toc[index][0]
                if d == 1:
                    child = QtWidgets.QTreeWidgetItem(parent)
                    #child.setBackground(toc[i][0], QBrush(QtCore.Qt.GlobalColor.white))
                    child.setText(0, toc[i][1])
                    child.setText(1, str(toc[i][2]))
                    i = connectParent(child, i, toc)
                    if i == -1:
                        return -1
                else:
                    return i
            return -1

        connectParent(self.bookmark, 0, toc)

        self.bookmark.show()

    def plus_btn_click(self):
        self.scale += 1
        self.pdfResize()
    def minus_btn_click(self):
        if self.scale - 1 > 0:
            self.scale -= 1 
            self.pdfResize()
    
    def valChange2(self):
        if self.mode == 1 and not self.slider2.isHidden():
            self.pdfScreen.setPos(-self.slider2.value()*self.dx, self.pdfScreen.y())
            self.pdfScreen2.setPos(self.pdfScreen.x(), self.pdfScreen2.y())
            
        self.mouseBox.update()
        self.mouseBox2.update()
            
    def valChange(self):
        if self.mode == 1:
            index = self.tabWidget.currentIndex()
            sliderValue = self.slider.maximum() - self.slider.value()
            pageNum = sliderValue // self.div
            dy = (sliderValue - pageNum*self.div)*(self.pdfScreen.pixmap().height()+10)//self.div
            if pageNum != self.tabs[index][1]:
                self.pageEdit.setText(str(pageNum+1))
                self.tabs[index][1] = pageNum
                pixmap, self.page, self.words = self.myPixmap(self.tabs[index][2],pageNum)
                self.pdfScreen.setPixmap(pixmap)
                if pageNum+1 < self.tabs[index][2].page_count:
                    pixmap, self.page1, self.words1 = self.myPixmap(self.tabs[index][2],pageNum+1)
                    self.pdfScreen2.setPixmap(pixmap)
            self.pdfScreen.setPos(self.pdfScreen.x(), -dy)
            self.pdfScreen2.setPos(self.pdfScreen.x(), self.pdfScreen.y()+self.pdfScreen.pixmap().height()+10)
            
            self.mouseBox.update()
            self.mouseBox2.update()

    def generateMenu(self, pos):
        row_num = col_num = -1
        for i in self.tableWidget.selectionModel().selection().indexes():
            row_num = i.row()
            col_num = i.column()
        index = col_num + row_num*self.c
        if index < len(self.bookshelf):
            menu = QtWidgets.QMenu()
            item1 = menu.addAction('read')
            item2 = menu.addAction('delete')
            action = menu.exec_(self.tableWidget.mapToGlobal(pos))
            if action == item1:
                self.read(self.bookshelf[index])
            elif action == item2:
                self.delete(index)
    def tableClick(self, pos):
        index = pos.column()+pos.row()*self.c
        if index < len(self.bookshelf):
            self.read(self.bookshelf[index])

    def setCover(self, index):
        x = index % self.c
        y = index // self.c

        doc = fitz.open(self.bookshelf[index][0])
        page = doc.load_page(0)
        cover = pdfProcessor.pdfPageToImg(page, 1)
        label = QtWidgets.QLabel(self)
        label.setScaledContents(True)
        label.setPixmap(cover)
        self.tableWidget.setCellWidget(y, x, label)
        del label
        doc.close()


    def read(self, book):
        title = book[0].split('/' or "\\")[-1].replace(".pdf", "")
        tab = QtWidgets.QTabWidget()
        if len(title) > 16:
            title = title[:14] + ".."
        self.tabWidget.insertTab(0, tab, title)
        
        doc = fitz.open(book[0])
        filename = book[0].split(".pdf")
        filename.append("_note.docx")
        docx = docManager.Doc("".join(filename))
        
        self.tabs.insert(0, [*book,doc,False,docx]) #0path,1page,2doc,3modified,4docx
        self.tabWidget.currentChanged.connect(self.pdfReadPage)
        self.tabWidget.setCurrentIndex(0)
        self.reset()
        self.pdfReadPage()     

    def delete(self, index):
        for i in range(index, len(self.bookshelf)):
            x = i % self.c
            y = i // self.c
            self.tableWidget.removeCellWidget(y, x)
        self.bookshelf.pop(index)
        for i in range(index, len(self.bookshelf)):
            self.setCover(i)
    
    def save(self, index):
        doc = self.tabs[index][2]
        docx = self.tabs[index][4]
        if self.tabs[index][3]:
            try:
                docx.save()
            except BaseException:
                filename = docx.filename.split(".docx")
                filename.append("_modified.docx")
                docx.save("".join(filename))

            try:
                doc.save(self.tabs[index][0],deflate=True,encryption=0,incremental=1)
            except BaseException as e:    
                filename = self.tabs[index][0].split(".pdf")
                filename.append("_modified.pdf")
                str0 = "".join(filename)
                doc.save(str0,deflate=True,encryption=0)

                for i in range((len(self.bookshelf))):
                    if self.bookshelf[i][0] == self.tabs[index][0]:
                        self.tabs[index][0] = str0
                        self.bookshelf[i][0] = str0
                        break
                
    def remove_tab(self, index):
        self.bookmark.hide()
        doc = self.tabs[index][2]
        self.save(index)
        doc.close()
        
        #self.tabWidget.setCurrentIndex(0)
        for i in range(len(self.bookshelf)):
            if self.bookshelf[i][0] == self.tabs[index][0]:
                self.bookshelf[i][1] = self.tabs[index][1]
                break
        self.tabs.pop(index)
        self.tabWidget.removeTab(index)
        if len(self.tabs) == 0:
            self.home()
        else:
            self.pdfReadPage()
        self.findGroup.hide()

    def home(self):
        self.mode = 0
        self.tableWidget.show()
        self.groupBox2.hide()
        self.graphicView.hide()
        self.tabWidget.setCurrentIndex(len(self.tabs))
    
    def pdfResize(self):
        index = self.tabWidget.currentIndex()
        pageNum = self.tabs[index][1]
        pixmap, self.page, self.words = self.myPixmap(self.tabs[index][2],pageNum)
        self.w = pixmap.width()
        self.h = pixmap.height()
        self.pdfScreen.setPixmap(pixmap)
        self.pdfScreen.setPos(self.graphicView.width()//2-pixmap.width()//2, self.pdfScreen.y())
        if pageNum + 1 < self.tabs[index][2].page_count:
            pixmap, self.page1, self.words1 = self.myPixmap(self.tabs[index][2],pageNum+1)
            self.pdfScreen2.setPixmap(pixmap)
            self.pdfScreen2.setPos(self.graphicView.width()//2-pixmap.width()//2, pixmap.height()+self.pdfScreen.y()+10)
        if pixmap.width() > self.graphicView.width() + self.dx*2:
            self.slider2.show()
            self.slider2.setRange(0, math.ceil((pixmap.width()-self.graphicView.width())/self.dx))
            self.slider2.setValue(self.slider2.maximum()//2)
        else:
            self.slider2.hide()

        self.valChange()

    def pdfReadPage(self):
        index = self.tabWidget.currentIndex()
        if index != len(self.tabs):
            self.mode = 1
            self.bookmark.hide()
            self.mouseBox.hide()
            self.mouseBox2.hide()
            
            if index >= 0 and len(self.tabs) > 0:
                self.tableWidget.hide()
                self.groupBox2.show()
                self.graphicView.show()

                doc = self.tabs[index][2]
                self.bookName.setText(doc.metadata["title"])
                pageNum = self.tabs[index][1]
                page_count = doc.page_count
                self.pageEdit.setText(str(pageNum+1))
                self.pageLabel.setText(" / " + str(doc.page_count))

                pixmap, self.page, self.words = self.myPixmap(self.tabs[index][2],pageNum)
                self.w = pixmap.width()
                self.h = pixmap.height()
                self.pdfScreen.setPixmap(pixmap)
                self.pdfScreen.setPos(self.graphicView.width()//2-pixmap.width()//2, 0)
                if pageNum + 1 < page_count:
                    pixmap, self.page1, self.words1 = self.myPixmap(self.tabs[index][2],pageNum+1)
                    self.pdfScreen2.setPixmap(pixmap)
                    self.pdfScreen2.setPos(self.pdfScreen.x(), self.pdfScreen.pixmap().height()+self.pdfScreen.y()+10)
                
                if self.slider2.isVisible():
                    self.slider2.setRange(0, math.ceil((pixmap.width()-self.graphicView.width())/self.dx))
                    self.slider2.setValue(self.slider2.maximum()//2)
                self.slider.setRange(0, page_count*self.div-self.graphicView.height()*self.div//self.pdfScreen.pixmap().height())
                self.slider.setValue(self.slider.maximum() - pageNum*self.div)
    
    def myPixmap(self, doc, pageNum):
        page = doc.load_page(pageNum)
        words = page.get_text("words")
        return pdfProcessor.pdfPageToImg(page, self.scale), page, words
