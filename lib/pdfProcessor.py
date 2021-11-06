import fitz
from PyQt5.QtGui import *

def pdfPageToImg(page_data, scale=2):
    zoom_matrix = fitz.Matrix(scale, scale)   
    pagePixmap = page_data.get_pixmap(matrix = zoom_matrix, alpha=False) 
    pageQImage = QImage(pagePixmap.samples, pagePixmap.width, pagePixmap.height, pagePixmap.stride, QImage.Format_RGB888)
    pixmap = QPixmap()
    pixmap.convertFromImage(pageQImage)

    return pixmap