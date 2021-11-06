from PyQt5 import QtCore, QtGui, QtWidgets


class MyButton(QtWidgets.QPushButton):
    def __init__(self, parent=None, *, name, pos, text=None, img=None, clickfunc):
        super().__init__(parent)
        self.widget = parent
        self.setGeometry(QtCore.QRect(*pos))
        self.setObjectName(name)
        if text != None:
            self.setText(text)
        self.img = False
        if img != None:
            self.img = True
            self.icon = QtGui.QIcon(img[0])
            self.icon_click = QtGui.QIcon(img[1])
            self.icon_hover = QtGui.QIcon(img[2])
            self.setIcon(self.icon)
            self.setIconSize(QtCore.QSize(self.width(),self.height()))
        self.func = clickfunc
        self.setMouseTracking(True)
        self.setStyleSheet("""background-color: transparent;
                            border:none;""")

    def mousePressEvent(self, e):
        self.setIcon(self.icon_click)
        self.func()
        self.setIcon(self.icon)

    def mouseMoveEvent(self, e):
        x = e.x()
        y = e.y()
        d = 8
        if x > d and x < self.width()-d and y > d and y < self.height()-d:
            self.setIcon(self.icon_hover)
        else:
            self.setIcon(self.icon)   
    def mouseReleaseEvent(self, e):
        self.setIcon(self.icon)

class MyStateButton(QtWidgets.QPushButton):
    def __init__(self, parent=None, *, name, pos, text=None, img=None, clickfunc):
        super().__init__(parent)
        self.widget = parent
        self.setGeometry(QtCore.QRect(*pos))
        self.setObjectName(name)
        self.state = False
        if text != None:
            self.setText(text)
        self.img = False
        if img != None:
            self.img = True
            self.icon = QtGui.QIcon(img[0])
            self.icon_click = QtGui.QIcon(img[1])
            self.setIcon(self.icon)
            self.setIconSize(QtCore.QSize(self.width(),self.height()))
        self.func = clickfunc
        self.setStyleSheet("""background-color: transparent;
                            border:none;""")
    def update(self):
        if self.state:
            self.setIcon(self.icon_click)
        else:
            self.setIcon(self.icon)

    def mousePressEvent(self, e):
        self.state = not self.state
        self.update()
        self.func()

class MyGroup2(QtWidgets.QGraphicsItemGroup):
    def __init__(self, parent=None, *, widget):
        super().__init__(parent)
        self.widget = widget
        self.setVisible(False)

        self.wordRects = {}

        self.page = 0
        self.rx = 0
        self.ry = 0
        self.rx1 = 0
        self.ry1 = 0
        self.words = None
        self.index0 = -1
        self.index1 = -1

    def setRect(self, x0, y0, x1, y1, *, update=False):
        self.setPos(x0, y0)
        scale = self.widget.scale
        index = self.widget.inPdfScreen(x0, y0)
        self.words = None
        if index == 1:
            self.rx = (x0 - self.widget.pdfScreen.x())/scale
            self.ry = (y0 - self.widget.pdfScreen.y())/scale
            self.rx1 = (x1 - self.widget.pdfScreen.x())/scale
            self.ry1 = (y1 - self.widget.pdfScreen.y())/scale
            self.words = self.widget.words
        elif index == 2:
            self.rx = (x0 - self.widget.pdfScreen2.x())/scale
            self.ry = (y0 - self.widget.pdfScreen2.y())/scale
            self.rx1 = (x1 - self.widget.pdfScreen2.x())/scale
            self.ry1 = (y1 - self.widget.pdfScreen2.y())/scale
            self.words = self.widget.words1
        
        if self.rx1 > self.widget.w/scale:
            self.rx1 = self.widget.w/scale
        if self.ry1 > self.widget.h/scale:
            self.ry1 = self.widget.h/scale
        
        index0 = -1
        index1 = -1

        for i in range(len(self.words)):
            b = self.words[i]
            if self.intersect((self.rx,self.ry,self.rx1,self.ry1), b[:4]):
                index0 = i
                break

        for i in range(len(self.words)-1, self.index0-1,-1):
            b = self.words[i]
            if self.intersect((self.rx,self.ry,self.rx1,self.ry1), b[:4]):
                index1 = i
                break
        
        if update:
            for b in self.wordRects.values():
                self.removeFromGroup(b[0])
            self.wordRects.clear()
            self.index0 = index0
            self.index1 = index1

        if index0 != -1 and index1 != -1:
            for i in range(min(self.index0,index0),max(self.index1,index1)+1):
                
                if i not in self.wordRects and i >= index0 and i <= index1:
                    b = self.words[i]
                    rrx = self.rx - b[0]
                    rry = self.ry - b[1]
                    
                    wordRect = MyRect(self, color=QtGui.QColor(0, 128, 255))
                    self.wordRects[i] = [wordRect, b]
                    wordRect.setRect(*self.mapTo((rrx,rry),(0,0)),(b[2]-b[0]),(b[3]-b[1]))
                    self.addToGroup(wordRect)
                elif i in self.wordRects and (i < index0 or i > index1):
                    wordRect = self.wordRects[i][0]

                    self.wordRects.pop(i)
                    self.removeFromGroup(wordRect)

        self.index0 = index0
        self.index1 = index1

    def mapTo(self, rp, p):
        return (p[0]-rp[0], p[1]-rp[1])

    def intersect(self, r1, r2):
        x11, y11, x12, y12 = r1
        x21, y21, x22, y22 = r2
        if y12 < y11:
            y11, y12 = y12, y11
        if y22 < y21:
            y21, y22 = y22, y21
        if x11 > x12:
            x11, x12 = x12, x11
        if x21 > x22:
            x21, x22 = x22, x21
        if (x12 < x21 or x11 > x22) or (y12 < y21 or y11 > y22):
            return False
        return True

    def inRange(self, x, y, x0, y0, x1, y1):
        return x > x0 and x < x1 and y > y0 and y < y1

    def update(self):
        if self.widget.editMode == 0:
            scale = self.widget.scale
            pageNum = int(self.widget.pageEdit.text()) - 1
            
            self.setPos(self.rx*scale+self.widget.pdfScreen.x(), self.widget.pdfScreen.y()-(pageNum-self.page)*(self.widget.pdfScreen.pixmap().height()+10)+self.ry*scale)
            for wr in self.wordRects.values():
                wr[0].update()

            x, y = self.x(), self.y()
            if self.rx1 > self.rx:
                x += (self.rx1 - self.rx)*scale
            if self.ry1 > self.ry:
                y += (self.ry1 - self.ry)*scale
            self.widget.textBrowser.setGeometry(x, y, 400, 100)
    
    def hide(self):
        super().hide()
        self.words = None
        self.widget.textBrowser.hide()

class MyGroup(QtWidgets.QGraphicsItemGroup):
    def __init__(self, parent=None, *, widget):
        super().__init__(parent)
        self.widget = widget
        self.setVisible(False)
        self.rect = MyRect(self)
        self.addToGroup(self.rect)

        self.blockRects = []

        self.page = 0
        self.rx = 0
        self.ry = 0
        self.rx1 = 0
        self.ry1 = 0
        self.blocks = None

    def setRect(self, x0, y0, x1, y1, *, update=False):
        self.setPos(x0, y0)
        scale = self.widget.scale
        index = self.widget.inPdfScreen(x0, y0)
        page = None
        if index == 1:
            self.rx = (x0 - self.widget.pdfScreen.x())/scale
            self.ry = (y0 - self.widget.pdfScreen.y())/scale
            self.rx1 = (x1 - self.widget.pdfScreen.x())/scale
            self.ry1 = (y1 - self.widget.pdfScreen.y())/scale
            page = self.widget.page
        elif index == 2:
            self.rx = (x0 - self.widget.pdfScreen2.x())/scale
            self.ry = (y0 - self.widget.pdfScreen2.y())/scale
            self.rx1 = (x1 - self.widget.pdfScreen2.x())/scale
            self.ry1 = (y1 - self.widget.pdfScreen2.y())/scale
            page = self.widget.page1
        
        if self.rx1 > self.widget.w/scale:
            self.rx1 = self.widget.w/scale
        elif self.rx1 < self.rx:
            self.rx1 = self.rx
        if self.ry1 > self.widget.h/scale:
            self.ry1 = self.widget.h/scale
        elif self.ry1 < self.ry:
            self.ry1 = self.ry

        if update:
            for b in self.blockRects:
                self.removeFromGroup(b[0])
            self.blockRects.clear()

            if page != None:
                self.blocks = []
                blocks = page.get_text("blocks")
                for b in blocks:
                    self.blocks.append([*b, False])

        if self.widget.editMode == 1:  

            for b in self.blocks:
                if self.intersect((self.rx,self.ry,self.rx1,self.ry1), b[:4]):
                    if not b[7]:
                        b[7] = True
                        rrx = self.rx - b[0]
                        rry = self.ry - b[1]
                        
                        blockRect = MyRect(self, color=QtGui.QColor(255, 255, 0))
                        self.blockRects.append([blockRect, b])
                        blockRect.setRect(*self.mapTo((rrx,rry),(0,0)),(b[2]-b[0]),(b[3]-b[1]))
                        self.addToGroup(blockRect)
                else:
                    if b[7]:
                        b[7] = False
                        for i in range(len(self.blockRects)):
                            if b == self.blockRects[i][1]:
                                blockRect = self.blockRects[i][0]
                                self.blockRects.pop(i)
                                self.removeFromGroup(blockRect)
                                break
                
        self.rect.setRect(0, 0, (x1-x0)/scale, (y1-y0)/scale)

    def mapTo(self, rp, p):
        return (p[0]-rp[0], p[1]-rp[1])

    def intersect(self, r1, r2):
        x11, y11, x12, y12 = r1
        x21, y21, x22, y22 = r2
        if (x12 < x21 or x11 > x22) or (y12 < y21 or y11 > y22):
            return False
        return True

    def inRange(self, x, y, x0, y0, x1, y1):
        return x > x0 and x < x1 and y > y0 and y < y1

    def update(self):
        if self.widget.editMode != 0:
            scale = self.widget.scale
            pageNum = int(self.widget.pageEdit.text()) - 1
            
            self.setPos(self.rx*scale+self.widget.pdfScreen.x(), self.widget.pdfScreen.y()-(pageNum-self.page)*(self.widget.pdfScreen.pixmap().height()+10)+self.ry*scale)
            self.rect.update()

            if self.widget.editMode == 2:
                self.widget.editToolbar2.move(self.x()+self.rect.width(), self.y()+self.rect.height())
                self.widget.textEdit.setGeometry(QtCore.QRect(self.widget.mouseBox.x(),self.widget.mouseBox.y(),self.widget.mouseBox.rect.width(), self.widget.mouseBox.rect.height()))
            elif self.widget.editMode == 1:
                for br in self.blockRects:
                    br[0].update()
                self.widget.editToolbar.move(self.x()+self.rect.width(), self.y()+self.rect.height())
        
    def hide(self):
        super().hide()
        self.blocks = None
        self.widget.editToolbar2.hide()
        self.widget.editToolbar.hide()
        self.widget.textEdit.hide()
        
class MyRect(QtWidgets.QGraphicsRectItem):
    def __init__(self, parent=None, *, color=QtGui.QColor(0,128,255), opa=0.2):
        super().__init__(parent)
        self.parent = parent
        self.setOpacity(opa)
        pen = QtGui.QPen(color)
        pen.setWidth(2)
        self.setPen(pen)
        self.setBrush(QtGui.QBrush(color))
        self.w = 0
        self.h = 0
        self.x = 0
        self.y = 0

    def setPos(self, x, y):
        self.setRect(x, y, self.w, self.h)

    def setRect(self, x, y, w, h):
        self.w, self.h, self.x, self.y = w, h, x, y
        scale = self.parent.widget.scale
        super().setRect(x*scale, y*scale, w*scale, h*scale)

    def setSize(self, w, h):
        self.w, self.h= w, h
        scale = self.parent.widget.scale
        super().setRect(self.x*scale, self.y*scale, w*scale, h*scale)

    def update(self):
        self.setPos(self.x, self.y)
    
    def width(self):
        return self.rect().width()
    def height(self):
        return self.rect().height()

