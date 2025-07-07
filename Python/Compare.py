import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QMessageBox, QHBoxLayout, QLineEdit
)
import pandas as pd

class CompareCSVApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV 비교기 - Short에만 있는 원소 찾기")
        self.setGeometry(100, 100, 600, 400)

        self.short_path = ""
        self.long_path = ""

        layout = QVBoxLayout()

        # Short 파일 경로 표시
        short_layout = QHBoxLayout()
        self.short_label = QLabel("Short CSV 파일:")
        self.short_line = QLineEdit()
        self.short_line.setReadOnly(True)
        self.btn_select_short = QPushButton("Short 파일 선택")
        self.btn_select_short.clicked.connect(self.load_short_file)
        short_layout.addWidget(self.short_label)
        short_layout.addWidget(self.short_line)
        short_layout.addWidget(self.btn_select_short)

        # Long 파일 경로 표시
        long_layout = QHBoxLayout()
        self.long_label = QLabel("Long CSV 파일:")
        self.long_line = QLineEdit()
        self.long_line.setReadOnly(True)
        self.btn_select_long = QPushButton("Long 파일 선택")
        self.btn_select_long.clicked.connect(self.load_long_file)
        long_layout.addWidget(self.long_label)
        long_layout.addWidget(self.long_line)
        long_layout.addWidget(self.btn_select_long)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        self.btn_compare = QPushButton("비교 실행")
        self.btn_compare.clicked.connect(self.compare_files)

        self.btn_save = QPushButton("결과 저장")
        self.btn_save.clicked.connect(self.save_result)

        layout.addLayout(short_layout)
        layout.addLayout(long_layout)
        layout.addWidget(self.btn_compare)
        layout.addWidget(self.result_text)
        layout.addWidget(self.btn_save)

        self.setLayout(layout)

    def load_short_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Short 파일 선택", "", "CSV/Excel Files (*.csv *.xlsx)")
        if path:
            self.short_path = path
            self.short_line.setText(path)

    def load_long_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Long 파일 선택", "", "CSV/Excel Files (*.csv *.xlsx)")
        if path:
            self.long_path = path
            self.long_line.setText(path)

    def compare_files(self):
        if not self.short_path or not self.long_path:
            QMessageBox.warning(self, "경고", "두 개의 CSV 파일을 모두 선택해주세요.")
            return

        try:
            short_df = pd.read_csv(self.short_path, header=None)
            long_df = pd.read_csv(self.long_path, header=None)

            short_list = short_df[0].astype(str).tolist()
            long_list = long_df[0].astype(str).tolist()

            missing = [item for item in short_list if item not in long_list]
            self.result_text.setPlainText("\n".join(missing))

        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))

    def save_result(self):
        if self.result_text.toPlainText().strip() == "":
            QMessageBox.warning(self, "경고", "저장할 결과가 없습니다.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "결과 저장", "result.csv", "CSV/Excel Files (*.csv *.xlsx)")
        if path:
            result_lines = self.result_text.toPlainText().split('\n')
            pd.DataFrame(result_lines).to_csv(path, index=False, header=False)
            QMessageBox.information(self, "저장 완료", f"결과가 저장되었습니다: {path}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CompareCSVApp()
    window.show()
    sys.exit(app.exec_())
