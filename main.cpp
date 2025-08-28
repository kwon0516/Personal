// #include <iostream>
#include <bits/stdc++.h>
using namespace std;

// int main()
// {
//     int n;
//     cin >> n;

//     vector<int> arr(n);
//     for (int i = 0; i < n; i++)
//     {
//         cin >> arr[i];
//     }

//     sort(arr.begin(), arr.end());

//     for (int i = 0; i < n; i++)
//     {
//         cout << arr[i] << " ";
//     }

//     cout << "\nPress Enter to exit...";

//     cin >> n;
//     // cin.get(); // 엔터 입력 대기
    

//     return 0;
// }

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int nDay, nStandard;
    cin >> nDay >> nStandard;

    vector<double> dTemp(nDay);
    for (int i = 0; i < nDay; i++) {
        cin >> dTemp[i];
    }

    // 초기 구간 합
    double sum = 0.0;
    for (int i = 0; i < nStandard; i++) {
        sum += dTemp[i];
    }

    double maxAvg = sum / nStandard;

    // 슬라이딩 윈도우 적용 (O(N))
    for (int i = nStandard; i < nDay; i++) {
        sum += dTemp[i] - dTemp[i - nStandard];
        maxAvg = max(maxAvg, sum / nStandard);
    }

    // 소숫점 둘째자리까지 고정 출력
    cout << fixed << setprecision(2) << maxAvg << "\n";
    cout << "zz" << endl;

    cin.get();

    return 0;
}