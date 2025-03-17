import re
from datetime import datetime

log_data = """
[2025/03/05 18:00:01.634][MAIN] 910. Sesnor Scan Seq Start, Check _0.698
[2025/03/05 18:00:05.741][MAIN] 910. Sesnor Scan Seq Start, Check _0.801
[2025/03/05 18:00:09.747][MAIN] 910. Sesnor Scan Seq Start, Check _0.750
[2025/03/05 18:00:14.145][MAIN] 910. Sesnor Scan Seq Start, Check _0.765
[2025/03/05 18:00:18.141][MAIN] 910. Sesnor Scan Seq Start, Check _0.764
[2025/03/05 18:00:22.140][MAIN] 910. Sesnor Scan Seq Start, Check _0.757
[2025/03/05 18:00:26.547][MAIN] 910. Sesnor Scan Seq Start, Check _0.785
[2025/03/05 18:00:31.537][MAIN] 910. Sesnor Scan Seq Start, Check _1.354
[2025/03/05 18:00:35.543][MAIN] 910. Sesnor Scan Seq Start, Check _0.756
[2025/03/05 18:00:39.940][MAIN] 910. Sesnor Scan Seq Start, Check _1.060
[2025/03/05 18:00:44.437][MAIN] 910. Sesnor Scan Seq Start, Check _0.851
[2025/03/05 18:00:48.836][MAIN] 910. Sesnor Scan Seq Start, Check _0.766
[2025/03/05 18:00:53.235][MAIN] 910. Sesnor Scan Seq Start, Check _0.764
[2025/03/05 18:00:57.240][MAIN] 910. Sesnor Scan Seq Start, Check _0.762
[2025/03/05 18:01:01.638][MAIN] 910. Sesnor Scan Seq Start, Check _0.764
[2025/03/05 18:01:06.136][MAIN] 910. Sesnor Scan Seq Start, Check _1.210
[2025/03/05 18:01:10.343][MAIN] 910. Sesnor Scan Seq Start, Check _0.971
[2025/03/05 18:01:17.535][MAIN] 910. Sesnor Scan Seq Start, Check _3.913
[2025/03/05 18:01:21.534][MAIN] 910. Sesnor Scan Seq Start, Check _0.737
[2025/03/05 18:01:27.434][MAIN] 910. Sesnor Scan Seq Start, Check _2.644
[2025/03/05 18:01:31.432][MAIN] 910. Sesnor Scan Seq Start, Check _0.743
[2025/03/05 18:01:35.737][MAIN] 910. Sesnor Scan Seq Start, Check _1.044
[2025/03/05 18:01:39.736][MAIN] 910. Sesnor Scan Seq Start, Check _0.744
[2025/03/05 18:01:44.032][MAIN] 910. Sesnor Scan Seq Start, Check _1.040
[2025/03/05 18:01:48.238][MAIN] 910. Sesnor Scan Seq Start, Check _0.946
[2025/03/05 18:01:52.335][MAIN] 910. Sesnor Scan Seq Start, Check _0.853
[2025/03/05 18:01:56.742][MAIN] 910. Sesnor Scan Seq Start, Check _0.763
[2025/03/05 18:02:00.732][MAIN] 910. Sesnor Scan Seq Start, Check _0.732
[2025/03/05 18:02:04.838][MAIN] 910. Sesnor Scan Seq Start, Check _0.762
[2025/03/05 18:02:09.136][MAIN] 910. Sesnor Scan Seq Start, Check _1.005
[2025/03/05 18:02:13.442][MAIN] 910. Sesnor Scan Seq Start, Check _0.765
[2025/03/05 18:02:17.439][MAIN] 910. Sesnor Scan Seq Start, Check _0.743
[2025/03/05 18:02:21.637][MAIN] 910. Sesnor Scan Seq Start, Check _0.931
[2025/03/05 18:02:25.633][MAIN] 910. Sesnor Scan Seq Start, Check _0.744
[2025/03/05 18:02:29.640][MAIN] 910. Sesnor Scan Seq Start, Check _0.766
[2025/03/05 18:02:33.737][MAIN] 910. Sesnor Scan Seq Start, Check _0.763
[2025/03/05 18:02:37.736][MAIN] 910. Sesnor Scan Seq Start, Check _0.731
[2025/03/05 18:02:41.932][MAIN] 910. Sesnor Scan Seq Start, Check _0.943
[2025/03/05 18:02:46.339][MAIN] 910. Sesnor Scan Seq Start, Check _0.771
[2025/03/05 18:02:51.230][MAIN] 910. Sesnor Scan Seq Start, Check _1.648
[2025/03/05 18:02:55.436][MAIN] 910. Sesnor Scan Seq Start, Check _0.965
[2025/03/05 18:02:59.733][MAIN] 910. Sesnor Scan Seq Start, Check _1.018
[2025/03/05 18:03:03.731][MAIN] 910. Sesnor Scan Seq Start, Check _0.751
[2025/03/05 18:03:07.829][MAIN] 910. Sesnor Scan Seq Start, Check _0.762
[2025/03/05 18:03:11.835][MAIN] 910. Sesnor Scan Seq Start, Check _0.753
[2025/03/05 18:03:15.831][MAIN] 910. Sesnor Scan Seq Start, Check _0.728
[2025/03/05 18:03:20.237][MAIN] 910. Sesnor Scan Seq Start, Check _0.760
[2025/03/05 18:03:24.236][MAIN] 910. Sesnor Scan Seq Start, Check _0.713
[2025/03/05 18:03:28.233][MAIN] 910. Sesnor Scan Seq Start, Check _0.734
[2025/03/05 18:03:32.238][MAIN] 910. Sesnor Scan Seq Start, Check _0.767
[2025/03/05 18:03:36.228][MAIN] 910. Sesnor Scan Seq Start, Check _0.760
[2025/03/05 18:03:40.534][MAIN] 910. Sesnor Scan Seq Start, Check _0.764
[2025/03/05 18:03:44.532][MAIN] 910. Sesnor Scan Seq Start, Check _0.724
[2025/03/05 18:03:48.630][MAIN] 910. Sesnor Scan Seq Start, Check _0.832
[2025/03/05 18:03:52.635][MAIN] 910. Sesnor Scan Seq Start, Check _0.760
[2025/03/05 18:03:57.033][MAIN] 910. Sesnor Scan Seq Start, Check _0.774
[2025/03/05 18:04:01.431][MAIN] 910. Sesnor Scan Seq Start, Check _0.769
[2025/03/05 18:04:06.337][MAIN] 910. Sesnor Scan Seq Start, Check _1.263
[2025/03/05 18:04:10.336][MAIN] 910. Sesnor Scan Seq Start, Check _0.727
[2025/03/05 18:04:14.935][MAIN] 910. Sesnor Scan Seq Start, Check _1.326
[2025/03/05 18:04:19.032][MAIN] 910. Sesnor Scan Seq Start, Check _0.758
[2025/03/05 18:04:23.329][MAIN] 910. Sesnor Scan Seq Start, Check _1.051
[2025/03/05 18:04:27.636][MAIN] 910. Sesnor Scan Seq Start, Check _0.768
[2025/03/05 18:04:31.632][MAIN] 910. Sesnor Scan Seq Start, Check _0.736
[2025/03/05 18:04:35.629][MAIN] 910. Sesnor Scan Seq Start, Check _0.730
[2025/03/05 18:04:39.728][MAIN] 910. Sesnor Scan Seq Start, Check _0.832
[2025/03/05 18:04:43.733][MAIN] 910. Sesnor Scan Seq Start, Check _0.766
[2025/03/05 18:04:48.732][MAIN] 910. Sesnor Scan Seq Start, Check _1.752
[2025/03/05 18:04:52.829][MAIN] 910. Sesnor Scan Seq Start, Check _0.767
[2025/03/05 18:04:57.027][MAIN] 910. Sesnor Scan Seq Start, Check _0.922
[2025/03/05 18:05:01.335][MAIN] 910. Sesnor Scan Seq Start, Check _1.011
[2025/03/05 18:05:05.732][MAIN] 910. Sesnor Scan Seq Start, Check _0.764
[2025/03/05 18:05:09.730][MAIN] 910. Sesnor Scan Seq Start, Check _0.725
[2025/03/05 18:05:13.736][MAIN] 910. Sesnor Scan Seq Start, Check _0.750
[2025/03/05 18:05:17.732][MAIN] 910. Sesnor Scan Seq Start, Check _0.735
[2025/03/05 18:05:21.930][MAIN] 910. Sesnor Scan Seq Start, Check _0.952
[2025/03/05 18:05:25.928][MAIN] 910. Sesnor Scan Seq Start, Check _0.753
[2025/03/05 18:05:30.836][MAIN] 910. Sesnor Scan Seq Start, Check _1.649
[2025/03/05 18:05:34.833][MAIN] 910. Sesnor Scan Seq Start, Check _0.756
[2025/03/05 18:05:39.932][MAIN] 910. Sesnor Scan Seq Start, Check _1.856
[2025/03/05 18:05:43.928][MAIN] 910. Sesnor Scan Seq Start, Check _0.750
[2025/03/05 18:05:48.728][MAIN] 910. Sesnor Scan Seq Start, Check _1.550
[2025/03/05 18:05:52.732][MAIN] 910. Sesnor Scan Seq Start, Check _0.756
[2025/03/05 18:05:57.132][MAIN] 910. Sesnor Scan Seq Start, Check _1.130
[2025/03/05 18:06:01.129][MAIN] 910. Sesnor Scan Seq Start, Check _0.743
[2025/03/05 18:06:06.027][MAIN] 910. Sesnor Scan Seq Start, Check _1.628
[2025/03/05 18:06:10.124][MAIN] 910. Sesnor Scan Seq Start, Check _0.746
[2025/03/05 18:06:14.332][MAIN] 910. Sesnor Scan Seq Start, Check _0.965
[2025/03/05 18:06:18.429][MAIN] 910. Sesnor Scan Seq Start, Check _0.766
[2025/03/05 18:06:22.435][MAIN] 910. Sesnor Scan Seq Start, Check _0.761
[2025/03/05 18:06:26.431][MAIN] 910. Sesnor Scan Seq Start, Check _0.748
[2025/03/05 18:06:30.429][MAIN] 910. Sesnor Scan Seq Start, Check _0.753
[2025/03/05 18:06:34.427][MAIN] 910. Sesnor Scan Seq Start, Check _0.742
[2025/03/05 18:06:39.124][MAIN] 910. Sesnor Scan Seq Start, Check _1.441
[2025/03/05 18:06:43.231][MAIN] 910. Sesnor Scan Seq Start, Check _0.864
[2025/03/05 18:06:48.431][MAIN] 910. Sesnor Scan Seq Start, Check _1.919
[2025/03/05 18:06:52.528][MAIN] 910. Sesnor Scan Seq Start, Check _0.835
[2025/03/05 18:06:56.933][MAIN] 910. Sesnor Scan Seq Start, Check _0.782
[2025/03/05 18:07:00.924][MAIN] 910. Sesnor Scan Seq Start, Check _0.717
[2025/03/05 18:07:04.929][MAIN] 910. Sesnor Scan Seq Start, Check _0.764
[2025/03/05 18:07:08.927][MAIN] 910. Sesnor Scan Seq Start, Check _0.743
"""

# 로그에서 시간 추출
time_pattern = re.compile(r'\[(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\]')
times = time_pattern.findall(log_data)

# Tact Time 계산
previous_time = None
tact_times = []

for time_str in times:
    current_time = datetime.strptime(time_str, '%Y/%m/%d %H:%M:%S.%f')
    if previous_time is not None:
        tact_time = (current_time - previous_time).total_seconds()
        tact_times.append(tact_time)
    previous_time = current_time

# Tact Time 출력
for i, tact_time in enumerate(tact_times):
    print(tact_time)
    # print(f"Tact Time {i+1}: {tact_time} seconds")