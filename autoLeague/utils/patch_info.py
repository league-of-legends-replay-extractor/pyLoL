from datetime import datetime


def get_patch_info():
    # 패치 일정 딕셔너리
    patch_schedule = {
        "25.01": "2025-01-09",
        "25.02": "2025-01-23",
        "25.03": "2025-02-05",
        "25.04": "2025-02-20",
        "25.05": "2025-03-05",
        "25.06": "2025-03-19",
        "25.07": "2025-04-02",
        "25.08": "2025-04-16",
        "25.09": "2025-04-30",
        "25.10": "2025-05-14",
        "25.11": "2025-05-28",
        "25.12": "2025-06-11",
        "25.13": "2025-06-25",
        "25.14": "2025-07-16",
        "25.15": "2025-07-30",
        "25.16": "2025-08-13",
        "25.17": "2025-08-27",
        "25.18": "2025-09-10",
        "25.19": "2025-09-24",
        "25.20": "2025-10-08",
        "25.21": "2025-10-22",
        "25.22": "2025-11-05",
        "25.23": "2025-11-19",
        "25.24": "2025-12-10"
    }

    # 현재 시각 (KST)
    current_time = datetime.now()

    # 가장 최근의 과거 패치 찾기
    recent_patch = None
    recent_date = None

    for version, date_str in patch_schedule.items():
        patch_date = datetime.strptime(date_str, "%Y-%m-%d")
        if patch_date <= current_time:
            if (recent_date is None) or (patch_date > recent_date):
                recent_patch = version
                recent_date = patch_date

    # 결과 출력
    if recent_patch and recent_date:
        print(f"현재 시각: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"가장 최근의 과거 패치 버전: {recent_patch}")
        print(f"패치일: {recent_date.strftime('%Y-%m-%d')}")
    else:
        print("현재 시각 이전의 패치가 없습니다.")
