import sys
import re
import csv
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox
)

# 기존 콘솔 코드에서 수정: 기준 로그를 인자로 받도록

def parse_log_time(line):
    match = re.search(r"\[(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\]", line)
    if match:
        return datetime.strptime(match.group(1), "%Y/%m/%d %H:%M:%S.%f")
    return None

def analyze_multiple_takt_times(log_path, output_path, std1, std2):
    with open(log_path, 'r', encoding='utf-16-le') as f:
        lines = f.readlines()

    takt_results = []
    i = 0
    while i < len(lines):
        line = lines[i]

        if std2 in line:
            standard2_time = None
            for j in range(i, -1, -1):
                standard2_time = parse_log_time(lines[j])
                if standard2_time:
                    break

            if standard2_time is None:
                i += 1
                continue

            found = False
            for k in range(i + 1, len(lines)):
                if std1 in lines[k]:
                    standard1_time = parse_log_time(lines[k])
                    if standard1_time:
                        takt = (standard1_time - standard2_time).total_seconds()
                        takt_results.append((i+1, standard2_time, standard1_time, takt))
                        i = k
                        found = True
                        break
            if not found:
                pass
        i += 1

    if output_path.endswith(".csv"):
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["기준2 라인 번호", "기준2 시간", "기준1 시간", "택타임(초) (기준1 - 기준2)"])
            for idx, t2, t1, takt in takt_results:
                writer.writerow([idx, t2.strftime('%Y-%m-%d %H:%M:%S.%f'), t1.strftime('%Y-%m-%d %H:%M:%S.%f'), takt])
    else:
        with open(output_path, 'w', encoding='utf-8') as txtfile:
            txtfile.write("기준2 라인 번호\t기준2 시간\t기준1 시간\t택타임(초) (기준1 - 기준2)\n")
            for idx, t2, t1, takt in takt_results:
                txtfile.write(f"{idx}\t{t2.strftime('%Y-%m-%d %H:%M:%S.%f')}\t{t1.strftime('%Y-%m-%d %H:%M:%S.%f')}\t{takt}\n")

class TaktTimeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("택타임 분석기")

        self.std1_input = QLineEdit()
        self.std2_input = QLineEdit()
        self.log_path_btn = QPushButton("로그 파일 선택")
        self.save_path_btn = QPushButton("결과 저장 위치 선택")
        self.start_btn = QPushButton("분석 시작")

        self.log_path_label = QLabel("선택된 로그 파일: 없음")
        self.save_path_label = QLabel("선택된 저장 위치: 없음")

        self.log_path = ""
        self.save_path = ""

        layout = QVBoxLayout()
        layout.addWidget(QLabel("기준 로그 1 (예: 트리거 시작 완료):"))
        layout.addWidget(self.std1_input)
        layout.addWidget(QLabel("기준 로그 2 (예: Sesnor Scan Seq Start):"))
        layout.addWidget(self.std2_input)

        layout.addWidget(QLabel("※ 택타임 = 기준1 - 기준2"))

        layout.addWidget(self.log_path_btn)
        layout.addWidget(self.log_path_label)
        layout.addWidget(self.save_path_btn)
        layout.addWidget(self.save_path_label)
        layout.addWidget(self.start_btn)

        self.setLayout(layout)

        self.log_path_btn.clicked.connect(self.select_log_file)
        self.save_path_btn.clicked.connect(self.select_save_file)
        self.start_btn.clicked.connect(self.start_analysis)

    def select_log_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "로그 파일 선택", "", "Log Files (*.log *.txt)")
        if path:
            self.log_path = path
            self.log_path_label.setText(f"선택된 로그 파일: {path}")

    def select_save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "결과 저장 위치 선택", "", "CSV 또는 TXT (*.csv *.txt)")
        if path:
            self.save_path = path
            self.save_path_label.setText(f"선택된 저장 위치: {path}")

    def start_analysis(self):
        std1 = self.std1_input.text().strip()
        std2 = self.std2_input.text().strip()

        if not std1 or not std2:
            QMessageBox.warning(self, "입력 오류", "기준 로그를 모두 입력해 주세요.")
            return

        if not self.log_path or not self.save_path:
            QMessageBox.warning(self, "파일 오류", "파일 경로를 모두 선택해 주세요.")
            return

        try:
            analyze_multiple_takt_times(self.log_path, self.save_path, std1, std2)
            QMessageBox.information(self, "완료", f"파일 저장 완료: {self.save_path}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"분석 중 오류 발생: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaktTimeApp()
    window.show()
    sys.exit(app.exec_())