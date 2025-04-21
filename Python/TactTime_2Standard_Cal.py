import re
from datetime import datetime
import csv

def parse_log_time(line):
    """시간 정보 추출"""
    match = re.search(r"\[(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\]", line)
    if match:
        return datetime.strptime(match.group(1), "%Y/%m/%d %H:%M:%S.%f")
    return None

def analyze_multiple_takt_times(log_path, output_csv_path):
    with open(log_path, 'r', encoding='utf-16-le') as f:
        lines = f.readlines()

    takt_results = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # 기준2 탐색
        if "910. Sesnor Scan Seq Start" in line:
            # 기준2의 시간: 이전 줄들 중 시간 포함된 것 찾기
            standard2_time = None
            for j in range(i, -1, -1):
                standard2_time = parse_log_time(lines[j])
                if standard2_time:
                    break

            if standard2_time is None:
                print(f"{i+1}번째 기준2에서 시간 정보 없음 (스킵)")
                i += 1
                continue

            # 기준2 이후 기준1 찾기
            found = False
            for k in range(i + 1, len(lines)):
                if "[ PLC_BUSY_OFF ] 트리거 시작 완료" in lines[k]:
                    standard1_time = parse_log_time(lines[k])
                    if standard1_time:
                        takt = (standard1_time - standard2_time).total_seconds()
                        takt_results.append((i+1, standard2_time, standard1_time, takt))
                        i = k  # 다음 탐색을 이 이후부터
                        found = True
                        break

            if not found:
                print(f"{i+1}번째 기준2 이후 기준1이 없음")
        i += 1

    # 결과 출력
    for idx, t2, t1, takt in takt_results:
        print(f"[기준2 Line {idx}] {t2} → {t1}  ▶ 택타임: {takt:.3f}초")

    print(f"\n총 {len(takt_results)}개 택타임 분석 완료")

    # ✅ CSV 저장
    with open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["기준2 라인 번호", "기준2 시간", "기준1 시간", "택타임(초)"])
        for idx, t2, t1, takt in takt_results:
            writer.writerow([idx, t2.strftime('%Y-%m-%d %H:%M:%S.%f'), t1.strftime('%Y-%m-%d %H:%M:%S.%f'), takt])

    print(f"\n📁 CSV 저장 완료: {output_csv_path}")

# ✅ 파일 경로
log_file_path = r"C:\Users\kwon\Downloads\MI2\3-1 short\20250417_Event.log"
csv_output_path = r"C:\Users\kwon\Downloads\MI2\3-1 short\20250417_Event.csv"

analyze_multiple_takt_times(log_file_path, csv_output_path)
