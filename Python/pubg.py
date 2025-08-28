import sys
import random
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QMainWindow, QPushButton, QLineEdit, QLabel
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QBrush, QPen, QCursor


# 커스텀 QGraphicsView 클래스
class RecoilView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.simulator = parent  # RecoilSimulator 인스턴스 참조

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.simulator.is_firing:
            self.simulator.is_firing = True
            self.simulator.fire_one_bullet()
            rpm = 600
            self.simulator.fire_delay = int(60000 / rpm)
            self.simulator.timer.start(self.simulator.fire_delay)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.simulator.is_firing = False
            self.simulator.timer.stop()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        scene_pos = self.mapToScene(pos)
        self.simulator.current_point = scene_pos

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_C:
            self.simulator.clear_shots()
        else:
            super().keyPressEvent(event)


class RecoilSimulator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simulator")
        self.setGeometry(100, 100, 800, 600)

        self.view = RecoilView(self)
        self.setCentralWidget(self.view)

        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.view.setSceneRect(0, 0, 800, 600)

        self.current_point = QPointF(400, 300)
        self.shots = []

        # 표적지(타겟) 시각화: 중앙에 원 추가
        self.target_radius = 40
        self.target = QGraphicsEllipseItem(400 - self.target_radius, 300 - self.target_radius, self.target_radius * 2, self.target_radius * 2)
        self.target.setPen(QPen(Qt.black, 2))
        self.target.setBrush(QBrush(Qt.transparent))
        self.scene.addItem(self.target)

        # 점 지우기 버튼
        self.clear_button = QPushButton("점 지우기", self)
        self.clear_button.setGeometry(650, 20, 100, 30)
        self.clear_button.clicked.connect(self.clear_shots)

        # 반동 수치 입력 UI
        self.label_recoil_x = QLabel("반동 X범위:", self)
        self.label_recoil_x.setGeometry(650, 70, 70, 25)
        self.input_recoil_x = QLineEdit(self)
        self.input_recoil_x.setGeometry(720, 70, 40, 25)
        self.input_recoil_x.setText("5")

        self.label_recoil_y = QLabel("반동 Y범위:", self)
        self.label_recoil_y.setGeometry(650, 100, 70, 25)
        self.input_recoil_y = QLineEdit(self)
        self.input_recoil_y.setGeometry(720, 100, 40, 25)
        self.input_recoil_y.setText("8")

        self.timer = QTimer()
        self.timer.timeout.connect(self.fire_one_bullet)
        self.is_firing = False
        self.fire_delay = 100

    def fire_one_bullet(self):
        if not self.is_firing:
            return

        # 현재 커서 위치 가져오기
        global_pos = QCursor.pos()
        scene_pos = self.view.mapToScene(self.view.mapFromGlobal(global_pos))
        self.current_point = scene_pos

        # 반동 범위 입력값 적용
        try:
            recoil_x_range = float(self.input_recoil_x.text())
        except ValueError:
            recoil_x_range = 5
        try:
            recoil_y_range = float(self.input_recoil_y.text())
        except ValueError:
            recoil_y_range = 8

        recoil_x = random.uniform(-recoil_x_range, recoil_x_range)
        recoil_y = random.uniform(-recoil_y_range, -3)
        self.current_point += QPointF(recoil_x, recoil_y)

        # 실제 커서도 반동만큼 튀게 적용
        QCursor.setPos(global_pos.x() + recoil_x, global_pos.y() + recoil_y)

        # 점 찍기
        dot = QGraphicsEllipseItem(-2, -2, 4, 4)
        dot.setPos(self.current_point)
        dot.setBrush(QBrush(Qt.red))
        dot.setPen(QPen(Qt.NoPen))
        self.scene.addItem(dot)
        self.shots.append(dot)

    def clear_shots(self):
        for dot in self.shots:
            self.scene.removeItem(dot)
        self.shots.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecoilSimulator()
    window.show()
    sys.exit(app.exec_())
