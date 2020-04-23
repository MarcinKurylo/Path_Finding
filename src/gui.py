import sys
import traceback
from collections import namedtuple
from PyQt5.QtGui import QPixmap, QPainter,  QPen, QFont
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QPlainTextEdit, QDialog, QMessageBox
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QObject
from src.evol_algo import EvolutionaryAlgorithm


class WorkerSignals(QObject):

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(object)


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)


class ChildWin(QDialog):
    resized = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Set points')
        self.setGeometry(200, 200, 200, 200)
        self.resized.connect(self.resize_widgets)
        self.init_ui()

    def init_ui(self):
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.setStyleSheet('background-color:#FFFFFF;')
        self.label1 = QLabel(self)
        self.label1.setText('A')
        self.label2 = QLabel(self)
        self.label2.setText('B')
        self.label3 = QLabel(self)
        self.label3.setText('X')
        self.label4 = QLabel(self)
        self.label4.setText('Y')
        self.plain1 = QPlainTextEdit(self.bg_label)
        self.plain1.setStyleSheet('background-color:#1bbe70;')
        self.plain1.setFont(QFont('Arial', 10, ))
        self.plain1.setFrameStyle(3)
        self.plain1.setLineWidth(2)
        self.plain2 = QPlainTextEdit(self.bg_label)
        self.plain2.setStyleSheet('background-color:#1bbe70;')
        self.plain2.setFont(QFont('Arial', 10, ))
        self.plain2.setFrameStyle(3)
        self.plain2.setLineWidth(2)
        self.plain3 = QPlainTextEdit(self.bg_label)
        self.plain3.setStyleSheet('background-color:#1bbe70;')
        self.plain3.setFont(QFont('Arial', 10, ))
        self.plain3.setFrameStyle(3)
        self.plain3.setLineWidth(2)
        self.plain4 = QPlainTextEdit(self.bg_label)
        self.plain4.setStyleSheet('background-color:#1bbe70;')
        self.plain4.setFont(QFont('Arial', 10, ))
        self.plain4.setFrameStyle(3)
        self.plain4.setLineWidth(2)
        self.button1 = QPushButton(self)
        self.button1.setText('SET')
        self.button1.clicked.connect(self.get_entry)

    def get_entry(self):
        self.accept()
        x_a = int(self.plain1.toPlainText())
        y_a = int(self.plain2.toPlainText())
        x_b = int(self.plain3.toPlainText())
        y_b = int(self.plain4.toPlainText())
        return x_a, y_a, x_b, y_b

    def resizeEvent(self, event):
        self.resized.emit()
        return super().resizeEvent(event)

    def resize_widgets(self):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.label1.setGeometry(0.2 * self.width(), 0.25 * self.height(), 0.2 * self.width(), 0.2 * self.height())
        self.label2.setGeometry(0.2 * self.width(), 0.5 * self.height(), 0.2 * self.width(), 0.2 * self.height())
        self.label3.setGeometry(0.33 * self.width(), 0.1 * self.height(), 0.2 * self.width(), 0.2 * self.height())
        self.label4.setGeometry(0.57 * self.width(), 0.1 * self.height(), 0.2 * self.width(), 0.2 * self.height())
        self.plain1.setGeometry(0.25 * self.width(), 0.25 * self.height(), 0.2 * self.width(), 0.2 * self.height())
        self.plain2.setGeometry(0.5 * self.width(), 0.25 * self.height(), 0.2 * self.width(), 0.2 * self.height())
        self.plain3.setGeometry(0.25 * self.width(), 0.5 * self.height(), 0.2 * self.width(), 0.2 * self.height())
        self.plain4.setGeometry(0.5 * self.width(), 0.5 * self.height(), 0.2 * self.width(), 0.2 * self.height())
        self.button1.setGeometry(0.25 * self.width(), 0.8 * self.height(), 0.45 * self.width(), 0.2 * self.height())


class MyWindow(QMainWindow):
    resized = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle('Path finder')
        self.setMinimumSize(500, 500)  # forbid resize
        self.setMaximumSize(500, 500)  # forbid resize
        self.threadpool = QThreadPool()
        self.drawing = False
        self.autodraw = False
        self.brushSize = 1
        self.brushColor = Qt.black
        self.lastPoint = QPoint()
        self.xytuple = namedtuple('xytuple', ['x', 'y'])
        self.obstacle_pointlist = []
        self.startpoint = None
        self.endpoint = None
        self.path = None
        self.resized.connect(self.resize_widgets)
        self.init_ui()

    def init_ui(self):
        self.bg_label = QLabel(self)
        self.label1 = QLabel(self)
        self.label1.setStyleSheet('background-color:#1bbe70;')
        self.label2 = QLabel(self.label1)
        self.label2.setText('Generation:')
        self.label3 = QLabel(self.label1)
        self.label3.setText('Distance:')
        self.pixmap = QPixmap(self.bg_label.size())
        self.pixmap.fill(Qt.white)
        self.bg_label.setPixmap(self.pixmap)
        self.button1 = QPushButton(self.label1)
        self.button1.setText('RUN')
        self.button1.clicked.connect(self.run)
        self.button2 = QPushButton(self.label1)
        self.button2.setText('SET POINTS')
        self.button2.clicked.connect(self.setpointswindow)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if(event.buttons() & Qt.LeftButton) & self.drawing:
            painter = QPainter(self.bg_label.pixmap())
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine))
            self.lastPoint = event.pos()
            self.update()
            if self.lastPoint not in self.obstacle_pointlist:
                for x in range(self.lastPoint.x()-3,self.lastPoint.x()+3):
                    for y in range(self.lastPoint.y()-3,self.lastPoint.y()+3):
                        painter.drawPoint(x,y)
                        if self.xytuple(x, y) not in self.obstacle_pointlist:
                            self.obstacle_pointlist.append(self.xytuple(x, y))
            painter.end()

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        if self.autodraw:
            canvaspainter = QPainter(self.bg_label.pixmap())
            canvaspainter.setPen(QPen(Qt.red, self.brushSize * 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            if not self.path:
                canvaspainter.setPen(
                    QPen(Qt.blue, self.brushSize * 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                canvaspainter.drawPoint(self.startpoint.x, self.startpoint.y)
                canvaspainter.drawPoint(self.endpoint.x, self.endpoint.y)
                canvaspainter.end()
                self.update()
                self.autodraw = False
            else:
                for i in range(1, len(self.path)):
                    point1, point2 = self.path[i], self.path[i-1]
                    canvaspainter.drawLine(point1.x, point1.y, point2.x, point2.y)
                canvaspainter.end()
                self.update()
                self.autodraw = False

    def resizeEvent(self, event):
        self.resized.emit()
        return super().resizeEvent(event)

    def resize_widgets(self):
        self.bg_label.setPixmap(self.pixmap.scaled(self.width(), 0.9*self.height()))
        self.bg_label.setGeometry(0, 0, self.width(), 0.9*self.height())
        self.label1.setGeometry(0, self.bg_label.height(), self.width(), 0.1 * self.height())
        self.label2.setGeometry(0.4*self.label1.width(), 0, self.label1.width(), 0.3*self.label1.height())
        self.label3.setGeometry(0.4 * self.label1.width(), 0.3*self.label1.height(),
                                self.label1.width(), 0.3 * self.label1.height())
        self.button1.setGeometry(0, 0, 0.2*self.label1.width(), self.label1.height())
        self.button2.setGeometry(0.2*self.label1.width(), 0, 0.2 * self.label1.width(), self.label1.height())

    def setpointswindow(self):
        child = ChildWin(self)
        if child.exec_():
            x_a, y_a, x_b, y_b = child.get_entry()
            self.startpoint = self.xytuple(x_a, y_a)
            self.endpoint = self.xytuple(x_b, y_b)
            self.autodraw = True

    def fn(self, progress_callback):
        self.path = self.ea.ea(progress_callback)
        self.autodraw = True
        return self.path

    @staticmethod
    def printresult(s):
        msg = QMessageBox()
        msg.setWindowTitle('Result')
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        s = [(t.x, t.y) for t in s]
        msg.setText(f'Best found path: {s}')
        msg.exec_()

    def progress_fn(self, i):
        self.label2.setText(f'Generation: {i[1]}')
        self.label3.setText(f'Best distance: {round(i[2],2)}')

    def run(self):
        self.ea = EvolutionaryAlgorithm(self.startpoint, self.endpoint, self.obstacle_pointlist)
        self.ea.register()
        worker = Worker(self.fn)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.result.connect(self.printresult)
        self.threadpool.start(worker)

