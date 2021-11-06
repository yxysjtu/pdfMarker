import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from MainWindow import Ui_MainWindow
from lib import windowCapture, sqlManager, translator
import fitz

class MyMainWindowForm(QtWidgets.QMainWindow, QtWidgets.QScrollArea, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindowForm, self).__init__(parent)
        self.setupUi(self)
        self.setAcceptDrops(True)

        key_plus = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Plus), self)
        key_plus.activated.connect(self.plusEvent)
        key_minus = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Minus), self)
        key_minus.activated.connect(self.minusEvent)
        find = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
        find.activated.connect(self.findEvent)
        translate = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Z"), self)
        translate.activated.connect(self.translateEvent)
        highlight = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+X"), self)
        highlight.activated.connect(self.highlightEvent)
        escape = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Escape), self)
        escape.activated.connect(self.escapeEvent)
        enter = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Return), self)
        enter.activated.connect(self.myEnterEvent)
        copy = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+C"), self)
        copy.activated.connect(self.copyEvent)
        switch_left = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Left), self)
        switch_left.activated.connect(self.leftEvent)
        switch_right = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Right), self)
        switch_right.activated.connect(self.rightEvent)
        switch_up = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Up), self)
        switch_up.activated.connect(self.upEvent)
        switch_down = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key.Key_Down), self)
        switch_down.activated.connect(self.downEvent)

    def dragEnterEvent(self, event):
        file = event.mimeData().urls()[0].toLocalFile()
        print(file)
        if file not in [x[0] for x in self.bookshelf]: 
            filename = file.split('/')[-1]
            fileformat = filename.split('.')[-1]
            if fileformat == "pdf":
                self.bookshelf.append([file,0])
                self.setCover(len(self.bookshelf) - 1)
    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.bookmark.hide()
        return super().mousePressEvent(a0)

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        if self.mode == 1:
            sliderValue = self.slider.value() + a0.angleDelta().y()
            if sliderValue > self.slider.maximum():
                sliderValue = self.slider.maximum()
            elif sliderValue < self.slider.minimum():
                sliderValue = self.slider.minimum()
            self.slider.setValue(sliderValue)

            if not self.slider2.isHidden():
                v = self.slider2.value() - a0.angleDelta().x()*self.slider2.maximum()//200
                if v < 0:
                    v = 0
                elif v > self.slider2.maximum():
                    v = self.slider2.maximum()
                self.slider2.setValue(v)     

        return super().wheelEvent(a0)
    
    def findEvent(self):
        self.findLabel.setText("0/0")
        self.findEdit.setText("")
        self.findGroup.show()

    def escapeEvent(self):
        self.reset()
    
    def highlightEvent(self):
        if self.mouseBox2.isVisible():
            index = self.tabWidget.currentIndex()
            self.tabs[index][3] = True
            doc = self.tabs[index][2]
            page = doc.load_page(self.mouseBox2.page)
            docx = self.tabs[index][4]
            
            for w in self.mouseBox2.wordRects.values():
                p1 = w[1][:2]
                p2 = w[1][2:4]
                rect = fitz.Rect(*p1, *p2)
                quad = fitz.Quad(rect.tl, rect.tr, rect.bl, rect.br)
            
                page.add_highlight_annot(quad)
            
            zoom_matrix = fitz.Matrix(self.scale, self.scale)
            pagePixmap = page.get_pixmap(matrix = zoom_matrix, alpha=False) 
            pageQImage = QtGui.QImage(pagePixmap.samples, pagePixmap.width, pagePixmap.height, pagePixmap.stride, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap()
            pixmap.convertFromImage(pageQImage)

            index = self.mouseBox2.page - (int)(self.pageEdit.text()) + 2
            if index == 1:
                self.pdfScreen.setPixmap(pixmap)
            elif index == 2:
                self.pdfScreen2.setPixmap(pixmap)
            
            tocName = None
            for toc in doc.get_toc():
                if toc[2] > self.mouseBox2.page:
                    tocName = toc[1]
                    break
            if tocName != None:
                docx.add_text(self.copyEvent() + "    ----(P" + str(self.mouseBox2.page+1) + " in " + tocName +")", style="List Bullet")
            else:
                docx.add_text(self.copyEvent() + "    ----(P" + str(self.mouseBox2.page+1) + ")", style="List Bullet")
            
            self.reset()
            
    def translateEvent(self):
        if self.mouseBox2.isVisible():
            i = self.mouseBox2.index0
            str1 = []
            while i <= self.mouseBox2.index1:
                word = self.mouseBox2.wordRects[i][1][4]
                if word[-1] == "-":
                    str1.append(word[:-1] + self.mouseBox2.wordRects[i+1][1][4])
                    i += 1
                else:
                    str1.append(word)
                i += 1
                if word[0] == "-" and len(str1) > 1:
                    str1[len(str1)-2] = str1[len(str1)-2] + str1[len(str1)-1][1:]
                    str1.pop(len(str1)-1)
            
            x, y = self.mouseBox2.x(), self.mouseBox2.y()
            if self.mouseBox2.rx1 > self.mouseBox2.rx:
                x += (self.mouseBox2.rx1 - self.mouseBox2.rx)*self.scale
            if self.mouseBox2.ry1 > self.mouseBox2.ry:
                y += (self.mouseBox2.ry1 - self.mouseBox2.ry)*self.scale
            self.textBrowser.move(x, y)
            try:
                result = translator.translate(" ".join(str1).replace("’","'").replace("”","\"").replace("“","\"").replace("‘","'"))
                self.textBrowser.setText(result)
                self.textBrowser.show()
            except BaseException:
                self.textBrowser.setText("no internet connection")
                self.textBrowser.show()

    def copyEvent(self):
        str2 = None
        if self.mouseBox.isVisible() and self.editMode == 1:
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
        elif self.mouseBox2.isVisible():
            i = self.mouseBox2.index0
            str1 = []
            while i <= self.mouseBox2.index1:
                word = self.mouseBox2.wordRects[i][1][4]
                if word[-1] == "-":
                    str1.append(word[:-1] + self.mouseBox2.wordRects[i+1][1][4])
                    i += 1
                else:
                    str1.append(word)
                i += 1
                if word[0] == "-" and len(str1) > 1:
                    str1[len(str1)-2] = str1[len(str1)-2] + str1[len(str1)-1][1:]
                    str1.pop(len(str1)-1)
            str2 = " ".join(str1).replace("’","'").replace("”","\"").replace("“","\"").replace("‘","'")
            windowCapture.copystr(str2)
        return str2
            
    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if self.textBrowser.isVisible():
            self.reset()
        return super().keyPressEvent(a0)

    def plusEvent(self):
        self.plus_btn_click()
    def minusEvent(self):
        self.minus_btn_click()

    def myEnterEvent(self):
        if self.mode == 1:
            if self.findGroup.isVisible():
                self.find_click()

            elif self.editMode == 1 and self.mouseBox.isVisible():
                index = self.inPdfScreen(self.mouseBox.x(),self.mouseBox.y())
                pixmap2 = None
                if index == 1:
                    dx = self.mouseBox.x() - self.pdfScreen.x()
                    dy = self.mouseBox.y() - self.pdfScreen.y()
                    pixmap2 = self.pdfScreen.pixmap().copy(dx, dy, self.mouseBox.rect.width(), self.mouseBox.rect.height())
                elif index == 2:
                    dx = self.mouseBox.x() - self.pdfScreen2.x()
                    dy = self.mouseBox.y() - self.pdfScreen2.y()
                    pixmap2 = self.pdfScreen2.pixmap().copy(dx, dy, self.mouseBox.rect.width(), self.mouseBox.rect.height())
                fname = "./data/temp.bmp"
                pixmap2.save(fname)
                windowCapture.copyboard(fname)   
                
                docx = self.tabs[self.tabWidget.currentIndex()][4]
                docx.add_img(fname)  
                self.tabs[self.tabWidget.currentIndex()][3] = True

                self.editToolbar.hide()
                self.mouseBox.setVisible(False)
            
            pageNum0 = (self.slider.maximum() - self.slider.value())//self.div
            pageNum = int(self.pageEdit.text()) - 1
            if pageNum0 != pageNum:
                self.slider.setValue(self.slider.maximum() - pageNum*self.div)

    def leftEvent(self):
        if self.mode == 1:
            if self.slider2.isHidden():
                pageNum = int(self.pageEdit.text()) - 1
                if pageNum - 1 >= 0:
                    pageNum -= 1
                self.slider.setValue(self.slider.maximum() - pageNum*self.div)
            elif self.slider2.value() > 0:
                self.slider2.setValue(self.slider2.value()-1)           
    
    def rightEvent(self):
        if self.mode == 1:
            if self.slider2.isHidden():
                pageNum = int(self.pageEdit.text()) - 1
                if pageNum + 1 < self.tabs[self.tabWidget.currentIndex()][2].page_count:
                    pageNum += 1
                self.slider.setValue(self.slider.maximum() - pageNum*self.div)
            elif self.slider2.value() < self.slider2.maximum():
                self.slider2.setValue(self.slider2.value()+1) 

    def upEvent(self):
        if self.mode == 1:
            sliderValue = self.slider.value() + 20
            if sliderValue > self.slider.maximum():
                sliderValue = self.slider.maximum()
            elif sliderValue < self.slider.minimum():
                sliderValue = self.slider.minimum()
            self.slider.setValue(sliderValue)
    def downEvent(self):
        if self.mode == 1:
            sliderValue = self.slider.value() - 20
            if sliderValue > self.slider.maximum():
                sliderValue = self.slider.maximum()
            elif sliderValue < self.slider.minimum():
                sliderValue = self.slider.minimum()
            self.slider.setValue(sliderValue)

    def closeEvent(self, event):
        for index in range(len(self.tabs)):
            for v in self.bookshelf:
                if v[0] == self.tabs[index][0]:
                    v[1] = self.tabs[index][1]
                    break
            self.save(index)

        db = sqlManager.SqlManager("./data/bookshelf.db")
        db.clear()
        for v in self.bookshelf:
            db.insert(value=v)
        print(db.select())
        db.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myWin = MyMainWindowForm()
    myWin.show()
    sys.exit(app.exec_())