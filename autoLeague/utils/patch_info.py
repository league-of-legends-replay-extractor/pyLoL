from datetime import datetime


def get_patch_info():
    # 패치 일정 딕셔너리
    patch_schedule = {
        "26.01": "2026-01-08",
        "26.02": "2026-01-22",
        "26.03": "2026-02-04",
        "26.04": "2026-02-19",
        "26.05": "2026-03-04",
        "26.06": "2026-03-18",
        "26.07": "2026-04-01",
        "26.08": "2026-04-15",
        "26.09": "2026-04-29",
        "26.10": "2026-05-13",
        "26.11": "2026-05-28",
        "26.12": "2026-06-10",
        "26.13": "2026-06-24",
        "26.14": "2026-07-15",
        "26.15": "2026-07-29",
        "26.16": "2026-08-12",
        "26.17": "2026-08-26",
        "26.18": "2026-09-10",
        "26.19": "2026-09-23",
        "26.20": "2026-10-07",
        "26.21": "2026-10-21",
        "26.22": "2026-11-04",
        "26.23": "2026-11-18",
        "26.24": "2026-12-09"
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

