import sys
import os
import csv
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QLabel, QFileDialog
)

TARGET_CATEGORIES = [
    "Foil Start Point(pt)",
    "Electrode Start Pos(pt)",
    "Electrode Start Thick(mm)",
    "95% Point Pos(pt)",
    "95% Point Thick(mm)",
    "Electrode End Pos(pt)",
    "Flattening Start Pos(pt)",
    "Flattening End Pos(pt)",
    "Flattening Thick(mm)",
    "Flattening Thick - 95% Thick(mm)"
]

TIME_COLUMN = "Start Time"  # 표시할 시간 컬럼 이름


def load_csv_flexible(path):
    """
    여러 인코딩/파서 시도를 통해 DataFrame을 반환.
    반환: (df, method_description)
    예외 발생 시 IOError
    """
    encodings = ['utf-8', 'cp949', 'utf-16', 'latin1']
    # 1) pandas with engine='python' and on_bad_lines='skip' (or fallback)
    for enc in encodings:
        try:
            # pandas >=1.3
            df = pd.read_csv(path, header=None, encoding=enc, engine='python', on_bad_lines='skip')
            if df.shape[0] >= 6:
                return df, f"pandas_python_on_bad_lines (enc={enc})"
        except TypeError:
            # older pandas: error_bad_lines=False
            try:
                df = pd.read_csv(path, header=None, encoding=enc, engine='python', error_bad_lines=False)
                if df.shape[0] >= 6:
                    return df, f"pandas_python_error_bad_lines (enc={enc})"
            except Exception:
                pass
        except Exception:
            pass

    # 2) fallback: csv.Sniffer 로 구분자 추정해서 csv.reader 사용
    possible_delims = [',', '\t', ';', '|']
    for enc in encodings:
        try:
            with open(path, encoding=enc, errors='replace', newline='') as f:
                sample = f.read(8192)
                if not sample:
                    continue
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=possible_delims)
                    delim = dialect.delimiter
                except Exception:
                    # sniff 실패하면 기본 콤마 시도
                    delim = ','
                f.seek(0)
                reader = csv.reader(f, delimiter=delim)
                rows = [r for r in reader]
                if len(rows) >= 6:
                    df = pd.DataFrame(rows)
                    return df, f"csv_sniffer (enc={enc}, delim={repr(delim)})"
        except Exception:
            continue

    # 3) 마지막 시도: read as 'latin1' with pandas (가장 관대)
    try:
        df = pd.read_csv(path, header=None, encoding='latin1', engine='python', on_bad_lines='skip')
        if df.shape[0] >= 6:
            return df, "pandas_fallback_latin1"
    except Exception:
        pass

    raise IOError("Unable to parse CSV with flexible methods.")


def find_time_col_index(categories):
    """
    categories: list of header strings
    시도 순서:
      1) 정확히 TIME_COLUMN 일치 (strip, case-insensitive)
      2) 부분 일치 ('start' in & 'time' in)
      3) 'time' 단어 포함
      4) 없으면 None 반환
    """
    clean = [str(c).strip().lstrip('\ufeff') for c in categories]
    # exact match (case-insensitive)
    for i, c in enumerate(clean):
        if c.lower() == TIME_COLUMN.lower():
            return i
    # 'start' and 'time' 포함
    for i, c in enumerate(clean):
        low = c.lower()
        if 'start' in low and 'time' in low:
            return i
    # 'time' 포함
    for i, c in enumerate(clean):
        if 'time' in str(c).lower():
            return i
    return None


class CsvChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("검색할 폴더 경로:")
        layout.addWidget(self.label)

        self.path_input = QLineEdit()
        layout.addWidget(self.path_input)

        self.browse_btn = QPushButton("폴더 선택")
        self.browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_btn)

        self.check_btn = QPushButton("CSV 검사 실행")
        self.check_btn.clicked.connect(self.check_csv_files)
        layout.addWidget(self.check_btn)

        self.result_list = QListWidget()
        layout.addWidget(self.result_list)
        self.result_list.setSelectionMode(QListWidget.ExtendedSelection)

        # 여러 줄 복사 지원: Ctrl+C 이벤트 필터 등록
        self.result_list.installEventFilter(self)

        self.setLayout(layout)
        self.setWindowTitle("CSV Zero Value Checker (robust)")
        self.resize(800, 600)
        
    def eventFilter(self, source, event):
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QKeySequence
        if source == self.result_list and event.type() == QEvent.KeyPress:
            if event.matches(QKeySequence.Copy):
                selected_items = self.result_list.selectedItems()
                if selected_items:
                    text = "\n".join([item.text() for item in selected_items])
                    clipboard = QApplication.clipboard()
                    clipboard.setText(text)
                return True  # 이벤트 처리 완료
        return super().eventFilter(source, event)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if folder:
            self.path_input.setText(folder)

    def check_csv_files(self):
        folder_path = self.path_input.text().strip()
        if not folder_path or not os.path.exists(folder_path):
            self.result_list.addItem("❌ 유효한 폴더 경로를 입력하세요.")
            return

        self.result_list.clear()

        for root, _, files in os.walk(folder_path):
            for file in files:
                if "TOTAL_RESULT" in file and file.lower().endswith(".csv"):
                    file_path = os.path.join(root, file)
                    if "NA" in file_path:
                      continue  # NA가 경로에 있으면 건너뜀
                    try:
                        df, method = load_csv_flexible(file_path)
                        # ensure enough rows
                        if df.shape[0] < 6:
                            self.result_list.addItem(f"❌ {file} : 파싱은 되었으나 행이 충분하지 않습니다. ({method})")
                            continue

                        # header (5번째 행, index=4)
                        categories = df.iloc[4].astype(str).tolist()
                        # strip BOM / whitespace
                        categories = [c.strip().lstrip('\ufeff') for c in categories]

                        time_idx = find_time_col_index(categories)

                        issues = []
                        for row_idx in range(5, len(df)):
                            data_row = df.iloc[row_idx].astype(str).tolist()
                            # map category->value (zip truncates to shortest)
                            category_data = dict(zip(categories, data_row))

                            # get start_time value
                            start_time = None
                            if time_idx is not None and time_idx < len(data_row):
                                start_time = str(data_row[time_idx]).strip()
                            else:
                                # fallback: try by key
                                start_time = category_data.get(TIME_COLUMN, "")
                                if isinstance(start_time, float) and pd.isna(start_time):
                                    start_time = ""
                            if not start_time:
                                start_time = f"{row_idx+1}행"

                            for cat in TARGET_CATEGORIES:
                                if cat in category_data:
                                    val_raw = category_data.get(cat, "")
                                    val_str = str(val_raw).strip()
                                    if val_str == "":
                                        continue
                                    # 숫자 변환 시도 (천단위 콤마 제거)
                                    try:
                                        val_num = float(val_str.replace(',', ''))
                                        if val_num == 0.0:
                                            issues.append(f"   └─ {cat}, Start Time={start_time}, 값=0, {row_idx+1}번째 행")
                                            break  # 한 행에서 하나만 보고 다음 행으로
                                    except Exception:
                                        # 숫자로 변환 불가하면 건너뜀
                                        continue

                        if issues:
                            self.result_list.addItem(f"📂 {file_path}   ({method})")
                            # self.result_list.addItem(f"📂 {file}   ({method})")
                            for issue in issues:
                                self.result_list.addItem(issue)

                    except Exception as e:
                        self.result_list.addItem(f"❌ {file_path} 처리 오류: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CsvChecker()
    window.show()
    sys.exit(app.exec_())
