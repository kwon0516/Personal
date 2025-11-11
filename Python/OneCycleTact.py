import sys
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QLineEdit, QMessageBox, QTextEdit
)


class TactTimeCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("택타임 평균 계산기")
        self.setGeometry(200, 200, 500, 400)

        layout = QVBoxLayout()

        # 평균 구할 개수 입력
        self.input_label = QLabel("몇 개의 값으로 평균을 구할까요?")
        layout.addWidget(self.input_label)

        self.count_input = QLineEdit()
        self.count_input.setPlaceholderText("예: 10")
        layout.addWidget(self.count_input)

        # 파일 선택 버튼
        self.file_button = QPushButton("로그 파일 선택 (.log)")
        self.file_button.clicked.connect(self.load_file)
        layout.addWidget(self.file_button)

    # 선택된 파일명 표시
        self.file_name_label = QLabel("선택된 파일: 없음")
        layout.addWidget(self.file_name_label)

    # 결과 출력
        self.result_label = QLabel("결과가 여기에 표시됩니다.")
        layout.addWidget(self.result_label)

    # 더한 값들 교차검증 출력
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        layout.addWidget(self.detail_text)

        self.setLayout(layout)

    def load_file(self):
        # 파일 선택 다이얼로그
        file_path, _ = QFileDialog.getOpenFileName(self, "로그 파일 선택", "", "Log Files (*.log)")
        if not file_path:
            return
        self.file_name_label.setText(f"선택된 파일: {os.path.basename(file_path)}")

        try:
            n = int(self.count_input.text())
            if n <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "입력 오류", "올바른 숫자를 입력하세요.")
            return

        # 로그에서 "One Cycle Tact" 값 찾기
        values = []
        pattern = re.compile(r"\[\s*One\s+Cycle\s+Tact\s*\]\[(\d+\.\d+)\]")

        # UTF-16 우선, 실패하면 UTF-8 시도
        encodings = ["utf-16", "utf-8", "cp949"]
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    for line in f:
                        match = pattern.search(line)
                        if match:
                            try:
                                values.append(float(match.group(1)))
                            except ValueError:
                                pass
                if values:
                    break  # 성공하면 멈춤
            except Exception:
                continue

        if not values:
            self.result_label.setText("로그에서 'One Cycle Tact' 값을 찾을 수 없습니다.")
            self.detail_text.setText("")
            return

        # 뒤에서부터 N개만 선택
        recent_values = values[-n:]
        avg = sum(recent_values) / len(recent_values)

        # 결과 표시
        self.result_label.setText(
            f"평균: {avg:.3f} (데이터 {len(recent_values)}개 사용)"
        )

        # 교차검증용 값 리스트 표시
        detail_str = "사용된 값들:\n" + "\n".join(f"{v:.3f}" for v in recent_values)
        self.detail_text.setText(detail_str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TactTimeCalculator()
    window.show()
    sys.exit(app.exec_())
