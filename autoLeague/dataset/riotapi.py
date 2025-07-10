import requests
import time
import random          # ← 추가
from tqdm import tqdm
from collections import defaultdict     # ← 추가
import csv
import numpy as np
import os
from rich.progress import track  # rich 진행바 임포트
import pandas as pd
import csv, os, requests, math
import csv, os, requests, math
import multiprocessing as mp
from collections import deque
import os, csv, requests, itertools, time, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import (
    Progress, SpinnerColumn, BarColumn, TextColumn,
    TimeElapsedColumn, TimeRemainingColumn
)
from concurrent.futures import ProcessPoolExecutor, as_completed 
'''데이터셋 생성기, 원하는 티어 입력해주면 해당 티어대의 리플레이들을 저장해준다.'''
class RiotAPI(object):

    '''
        api_key : riot api key
        count : match per each player
    '''
    def __init__(self , api_key):
        self.api_key = api_key


    def getPuuid(self,summonerId):
        try:
            puuid = requests.get(f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}?api_key={self.api_key}').json()["puuid"]
            return puuid
        except:
            return None


    def getSummonerId(self,puuid):
        try:
            summonerId = requests.get(f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={self.api_key}').json()['id']
            return summonerId
        except:
            return None
    
    # 리스트의 각 원소가 순차적으로 누적한다.
    def transfomList(original_list):
        original_list = original_list
        new_list = []

        running_sum = 0
        for value in original_list:
            running_sum += value
            new_list.append(running_sum)

        return new_list

    # 두 리스트의 차이를 반환한다. ( 블루팀 - 레드팀 )
    def subtractList(blue_list1, red_list2):

        result = [a - b for a, b in zip(blue_list1, red_list2)]

        return result

    def getMatchData(self, matchId):
        data = requests.get(f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchId}/timeline?api_key={self.api_key}").json()
        #### 블루팀 participantId 1 ~ 5 // 레드팀 participantId 6 ~ 10
        BLUE_IDs = [1,2,3,4,5]
        RED_IDs = [6,7,8,9,10]
        #### 여기는 프레임 인덱스가 N 일때, 실제 그 프레임이 담는 시간대는 N-1 분 0초부터 N-1 분 59초까지임
        #### 따라서 5분부터 15분 0초까지의 정보는 프레임 6분부터 15까지이다.
        frame_5_to_15 = data['info']['frames'][6:16]
        
        # (해당 시간대에서) 각 팀별 킬 수, 어시스트 수, 누적 대형 오브젝트 처치 수 
        BLUE_KILLS,BLUE_DEATHS,BLUE_ASSISTS,BLUE_OBJECTS,BLUE_GOLDS,BLUE_EXPERIENCES  = [],[],[],[],[],[]   # 참고로 여기서는 각 챔피언들의 어시스트 합
        RED_KILLS,RED_DEATHS,RED_ASSISTS,RED_OBJECTS,RED_GOLDS,RED_EXPERIENCES = [],[],[],[],[],[]



        for frame in frame_5_to_15:

            blue_kills,blue_deaths,blue_assists,blue_objects,blue_golds,blue_experiences  = 0,0,0,0,0,0
            red_kills,red_deaths,red_assists,red_objects,red_golds,red_experiences = 0,0,0,0,0,0


            for event in frame['events']:

                if event['type'] == "CHAMPION_KILL":            # KILL, DEATH, ASSIST
                    if event['killerId'] in BLUE_IDs:
                        blue_kills += 1
                    if event['killerId'] in RED_IDs:
                        red_kills += 1
                    if event['victimId'] in BLUE_IDs:
                        blue_deaths += 1
                    if event['victimId'] in RED_IDs:
                        red_deaths += 1
                    if event.get("assistingParticipantIds") != None:
                        for assistId in event.get("assistingParticipantIds"):
                            if assistId in BLUE_IDs:
                                blue_assists += 1
                            if assistId in RED_IDs:
                                red_assists += 1

                if event['type'] == "ELITE_MONSTER_KILL":       # ELITE MONSTER KILL
                    if event['killerTeamId'] == 100:
                        blue_objects += 1
                    else:
                        red_objects += 1
          

            for index in frame['participantFrames']:
                if int(index)  <= 5:
                    #print(frame['participantFrames'][index]['totalGold'])
                    blue_golds += frame['participantFrames'][index]['totalGold']
                    blue_experiences += frame['participantFrames'][str(index)]['xp']
                else:
                    red_golds += frame['participantFrames'][index]['totalGold']
                    red_experiences += frame['participantFrames'][index]['xp']

              


            BLUE_KILLS.append(blue_kills)
            BLUE_DEATHS.append(blue_deaths)
            BLUE_ASSISTS.append(blue_assists)
            BLUE_OBJECTS.append(blue_objects)
            BLUE_GOLDS.append(blue_golds)
            BLUE_EXPERIENCES.append(blue_experiences)

            # 누적 횟수로 전환
            BLUE_KILLS = self.transfomList(BLUE_KILLS)
            BLUE_DEATHS = self.transfomList(BLUE_DEATHS)
            BLUE_ASSISTS = self.transfomList(BLUE_ASSISTS)
            BLUE_OBJECTS = self.transfomList(BLUE_OBJECTS)
            BLUE_GOLDS = self.transfomList(BLUE_GOLDS)
            BLUE_EXPERIENCES = self.transfomList(BLUE_EXPERIENCES)

            RED_KILLS.append(red_kills)
            RED_DEATHS.append(red_deaths)
            RED_ASSISTS.append(red_assists)
            RED_OBJECTS.append(red_objects)
            RED_GOLDS.append(red_golds)
            RED_EXPERIENCES.append(red_experiences)

            # 누적 횟수로 전환
            RED_KILLS = self.transfomList(RED_KILLS)
            RED_DEATHS = self.transfomList(RED_DEATHS)
            RED_ASSISTS = self.transfomList(RED_ASSISTS)
            RED_OBJECTS = self.transfomList(RED_OBJECTS)
            RED_GOLDS = self.transfomList(RED_GOLDS)
            RED_EXPERIENCES = self.transfomList(RED_EXPERIENCES)


            # 팀 차이 계산

            DIFF_KILLS = self.subtractList(BLUE_KILLS,RED_KILLS)
            DIFF_DEATHS = self.subtractList(BLUE_DEATHS,RED_DEATHS)
            DIFF_ASSISTS = self.subtractList(BLUE_ASSISTS,RED_ASSISTS)
            DIFF_OBJECTS = self.subtractList(BLUE_OBJECTS,RED_OBJECTS)
            DIFF_GOLDS = self.subtractList(BLUE_GOLDS,RED_GOLDS)
            DIFF_EXPERIENCES = self.subtractList(BLUE_EXPERIENCES,RED_EXPERIENCES)

                #위 순서대로 리스트 병합
        
        allData = []
        '''allData.append(matchId)
        allData.extend(BLUE_KILLS) , allData.extend(BLUE_DEATHS) , allData.extend(BLUE_ASSISTS) , allData.extend(BLUE_OBJECTS) , allData.extend(BLUE_GOLDS) , allData.extend(BLUE_EXPERIENCES)
        allData.extend(RED_KILLS) , allData.extend(RED_DEATHS) , allData.extend(RED_ASSISTS) , allData.extend(RED_OBJECTS) , allData.extend(RED_GOLDS) , allData.extend(RED_EXPERIENCES)'''

        allData.append(DIFF_KILLS) , allData.append(DIFF_DEATHS) , allData.append(DIFF_ASSISTS) , allData.append(DIFF_OBJECTS) , allData.append(DIFF_GOLDS) , allData.append(DIFF_EXPERIENCES)

        # Convert the 2D list to a NumPy array and transpose it to have shape (time_steps, features)
        data_np = np.array(allData).transpose()

        # Add an extra dimension for samples, resulting in shape (samples, time_steps, features)
        data_np = np.expand_dims(data_np, axis=0)
        return data_np
    


    def writeCSVfile(self, matchIds): #위에서 추출한 정보들을 csv 파일로 저장한다. 모든 matchIds들에 대해서 진행.
        
        features = ['matchID']
        for i in range(10):
            features.append(f'블루킬{i}')

        for i in range(10):
            features.append(f'블루데스{i}')

        for i in range(10):
            features.append(f'블루어시{i}')

        for i in range(10):
            features.append(f'블루오브젝{i}')

        for i in range(10):
            features.append(f'레드킬{i}')

        for i in range(10):
            features.append(f'레드데스{i}')

        for i in range(10):
            features.append(f'레드어시{i}')

        for i in range(10):
            features.append(f'레드오브젝{i}')


        f = open(rf'riot_api_dataset.csv','a', newline='')
        wr = csv.writer(f)
        wr.writerow(features)
        
        for matchId in tqdm(matchIds):
            row = self.getMatchData(self,matchId)
            
            wr.writerow(row)

        f.close()

        print('csv write complete')


    
    # def save_champnames_from_matches_with_rofl(self, csv_save_folder_dir, csv_name, replay_dir):    
    #     # 리플레이 파일이 있는 디렉토리 (예시 경로)
    #     # replay_dir = r'C:\Users\username\Documents\League of Legends\Replays'
    #     # CSV를 저장할 디렉토리
    #     # csv_save_folder_dir = 'data'
    #     def get_champnames_per_match(matchid):
    #         # API 호출을 위해 '-'를 '_'로 변환
    #         matchid_api = matchid.replace('-', '_')
    #         url = f'https://asia.api.riotgames.com/lol/match/v5/matches/{matchid_api}?api_key={self.api_key}'
    #         data = requests.get(url).json()
    #         players = data['info']['participants']
    #         champNames = [player['championName'] for player in players]
    #         return champNames
    
    #     if not os.path.exists(csv_save_folder_dir):
    #         os.makedirs(csv_save_folder_dir)

    #     csv_file = os.path.join(csv_save_folder_dir, csv_name)

    #     with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
    #         writer = csv.writer(f)
    #         # 헤더 작성: match_id와 10개의 챔피언 컬럼
    #         writer.writerow(['match_id'] + [f'champion_{i+1}' for i in range(10)])
            
    #         # replay_dir 안의 모든 *.rofl 파일 목록 생성
    #         replay_files = [filename for filename in os.listdir(replay_dir) if filename.endswith('.rofl')]
            
    #         # rich 진행바를 사용해 파일 목록 순회
    #         for filename in track(replay_files, description="Processing replays..."):
    #             match_id = os.path.splitext(filename)[0]
    #             try:
    #                 champ_names = get_champnames_per_match(match_id)
    #                 if len(champ_names) == 10:
    #                     writer.writerow([match_id] + champ_names)
    #                 else:
    #                     print(f"경기 {match_id}에 챔피언이 10개가 아닙니다.")
    #             except Exception as e:
    #                 print(f"{match_id} 처리 중 에러 발생: {e}")

    def save_champnames_from_matches_with_rofl(
        self,
        csv_save_folder_dir: str,
        csv_name: str,
        replay_dir: str,
        max_workers: int = 8,          # 동시에 돌릴 스레드 수
    ):
        """리플레이(.rofl) 파일만 있을 때:
        파일명에서 matchid를 추출 → Riot API로 챔피언명 10개 조회 → CSV 저장
        """
        # ── 내부 함수 ────────────────────────────────────────────────
        def fetch_champnames(match_id: str) -> list[str]:
            # API 호출을 위해 '-' → '_' 치환
            matchid_api = match_id.replace("-", "_")
            url = (
                f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchid_api}"
                f"?api_key={self.api_key}"
            )
            data = requests.get(url, timeout=10).json()
            return [p["championName"] for p in data["info"]["participants"]]

        # ── 출력 디렉터리 준비 ───────────────────────────────────────
        if csv_save_folder_dir and not os.path.exists(csv_save_folder_dir):
            os.makedirs(csv_save_folder_dir, exist_ok=True)
        csv_file = os.path.join(csv_save_folder_dir, csv_name)

        # ── CSV 헤더(최초 1회) ──────────────────────────────────────
        if not os.path.exists(csv_file):
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["match_id"] + [f"champion_{i+1}" for i in range(10)])

        # ── 리플레이 파일 목록 ──────────────────────────────────────
        replay_files = [
            fn for fn in os.listdir(replay_dir) if fn.lower().endswith(".rofl")
        ]
        match_ids = [os.path.splitext(fn)[0] for fn in replay_files]

        # ── 진행 막대 설정 ─────────────────────────────────────────
        progress_cols = [
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        ]
        with Progress(*progress_cols, transient=True) as progress:
            task = progress.add_task("Fetching match data…", total=len(match_ids))

            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {
                    pool.submit(fetch_champnames, mid): mid for mid in match_ids
                }

                # CSV는 한 번만 열어서 메인 스레드에서 기록
                with open(csv_file, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)

                    for fut in as_completed(futures):
                        mid = futures[fut]
                        try:
                            champs = fut.result()
                            if len(champs) == 10:
                                writer.writerow([mid] + champs)
                            else:
                                progress.console.print(
                                    f"[yellow]⚠️  {mid}: 챔피언 개수 {len(champs)}[/]"
                                )
                        except Exception as e:
                            progress.console.print(
                                f"[red]✗ {mid} 처리 실패: {e}[/]"
                            )
                        progress.advance(task)





    # def save_champnames_from_matches_without_rofl(self, input_csv_path, output_csv_path):
    #     def get_champnames_per_match(matchid):
    #         url = f'https://asia.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={self.api_key}'
    #         data = requests.get(url).json()
    #         players = data['info']['participants']
    #         champNames = [player['championName'] for player in players]
    #         return champNames

    #     # 디렉토리 경로만 추출
    #     output_csv_dir = os.path.dirname(output_csv_path)

    #     if not os.path.exists(output_csv_dir):
    #         os.makedirs(output_csv_dir)

    #     csv_file = output_csv_path
    #     matchids = pd.read_csv(input_csv_path)['matchid'].tolist()

    #     # 헤더가 없는 경우만 헤더 작성
    #     if not os.path.exists(csv_file):
    #         with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
    #             writer = csv.writer(f)
    #             writer.writerow(['match_id'] + [f'champion_{i+1}' for i in range(10)])

    #     # 하나씩 append 모드로 작성
    #     for match_id in track(matchids, description="Appending match data..."):
    #         try:
    #             champ_names = get_champnames_per_match(match_id)
    #             if len(champ_names) == 10:
    #                 with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
    #                     writer = csv.writer(f)
    #                     writer.writerow([match_id] + champ_names)
    #             else:
    #                 print(f"경기 {match_id}에 챔피언이 10개가 아닙니다.")
    #         except Exception as e:
    #             print(f"{match_id} 처리 중 에러 발생: {e}")
    def save_champnames_from_matches_without_rofl(
        self,
        input_csv_path: str,
        output_csv_path: str,
        max_workers: int = 8,          # 🌟 동시에 호출할 스레드 수
    ):
        """download_replays.ipynb 단계를 건너뛰었을 때:
        CSV에 있는 matchid를 읽어 Riot API로 챔피언 10명을 조회해 저장한다.
        """
        # ── 내부 함수 ────────────────────────────────────────────────
        def get_champnames_per_match(matchid: str) -> list[str]:
            url = (
                f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchid}"
                f"?api_key={self.api_key}"
            )
            data = requests.get(url, timeout=10).json()
            return [p["championName"] for p in data["info"]["participants"]]

        # ── 출력 디렉터리 준비 ───────────────────────────────────────
        out_dir = os.path.dirname(output_csv_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # ── matchid 목록 로드 ──────────────────────────────────────
        matchids = pd.read_csv(input_csv_path)["matchid"].tolist()

        # ── 결과 CSV 헤더(최초 1회) ─────────────────────────────────
        if not os.path.exists(output_csv_path):
            with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["match_id"] + [f"champion_{i+1}" for i in range(10)])

        # ── 병렬 수집 + 진행 막대 ─────────────────────────────────
        progress_cols = [
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        ]
        with Progress(*progress_cols, transient=True) as progress:
            task = progress.add_task("Fetching match data…", total=len(matchids))

            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {pool.submit(get_champnames_per_match, mid): mid for mid in matchids}

                # CSV를 append 모드로 한 번만 열어둔 뒤 순차적으로 기록
                with open(output_csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)

                    for fut in as_completed(futures):
                        match_id = futures[fut]
                        try:
                            champs = fut.result()
                            if len(champs) == 10:
                                writer.writerow([match_id] + champs)
                            else:
                                progress.console.print(
                                    f"[yellow]⚠️  {match_id}: 챔피언 개수 {len(champs)}[/]"
                                )
                        except Exception as e:
                            progress.console.print(
                                f"[red]✗ {match_id} 처리 실패: {e}[/]"
                            )
                        progress.advance(task)
    @staticmethod
    def filter_matches_by_excluded_champions(csv_in, csv_out, excluded_champions):
        # ① CSV 로드
        df = pd.read_csv(csv_in)

        # ② champion_* 컬럼만 골라서 한 행(row) 안에 EXCLUDED_CHAMPIONS가
        #    하나라도 포함돼 있으면 True
        champ_cols = [c for c in df.columns if c.startswith("champion_")]
        has_excluded = df[champ_cols].isin(excluded_champions).any(axis=1)

        # ③ 조건 반전(~) → 제외 챔피언이 **없는** 경기만 선택
        filtered_df = df.loc[~has_excluded, ["match_id"]]

        # ④ 저장
        os.makedirs(os.path.dirname(csv_out), exist_ok=True)
        filtered_df.to_csv(csv_out, index=False)

        print(f"전체 {len(df)} 개 matchid 중에서 {len(filtered_df)}개의 match_id 가 {csv_out}에 저장되었습니다.")
    
    @staticmethod
    def save_top_matches_by_score(
        avg_score_csv_path: str,
        data_json_path: str,
        output_path: str,
        top_n: int = 6000,
    ):
        """
        avg_score_csv_path 에서 상위 top_n개의 match_id를 avg_score 기준으로 추출하고,
        data_json_path (kill_events_timeline JSON)에 존재하는 매치들만 필터링하여
        output_path에 저장합니다.
        """
        import csv, json, os

        # ① 평균 점수 CSV에서 match_id, avg_score 로드
        matches = []
        with open(avg_score_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m_id = row["match_id"]
                if m_id.startswith("KR_"):
                    m_id = m_id.replace("KR_", "")
                avg_score = float(row["avg_score"])
                matches.append((m_id, avg_score))

        # ② data.json 로드
        with open(data_json_path, "r", encoding="utf-8") as f:
            original_data = json.load(f)

        orig_inner_data = original_data.get("data", {})
        existing_ids = set(orig_inner_data.keys())

        # ③ 실제 존재하는 match_id 중에서 avg_score 기준 내림차순 상위 N개
        matches_in_json = [(m_id, score) for (m_id, score) in matches if m_id in existing_ids]
        matches_in_json.sort(key=lambda x: x[1], reverse=True)
        top_match_ids = [m_id for (m_id, _) in matches_in_json[:top_n]]

        # ④ 필터링하여 저장
        filtered_dict = {m_id: orig_inner_data[m_id] for m_id in top_match_ids}
        result_obj = {"data": filtered_dict}

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_obj, f, ensure_ascii=False, indent=2)

        print(f"data.json 기준 상위 {len(top_match_ids)}개 경기 필터링 완료.")
        print(f"결과 파일: {output_path}")


    @staticmethod
    def find_disjoint_matches_combinations(target_matches, max_solutions):
        # target_matches = 7  # 예시로 7경기를 선택 (원래 코드는 15였으나 테스트를 위해 7로 함)
        # max_solutions = 3   # 최대 3개의 조합을 찾도록 설정

        def load_matches(csv_path):
            matches = []
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)  # 헤더 건너뛰기
                for row in reader:
                    match_id = row[0]
                    champions = row[1:]
                    matches.append((match_id, set(champions)))
            return matches

        def find_disjoint_matches_all(matches, target, start, used_champions, selected, solutions, max_solutions=3):
            # 목표 경기 수(target)만큼 선택하면 하나의 조합 저장
            if len(selected) == target:
                solutions.append(selected.copy())
                return
            # 남은 경기들 순회
            for i in range(start, len(matches)):
                # 이미 원하는 조합 수를 찾은 경우 종료
                if len(solutions) >= max_solutions:
                    break
                match_id, champs = matches[i]
                # 선택된 경기들의 챔피언과 겹치는지 확인
                if used_champions & champs:
                    continue
                selected.append(match_id)
                new_used = used_champions.union(champs)
                find_disjoint_matches_all(matches, target, i+1, new_used, selected, solutions, max_solutions)
                selected.pop()
                
        # CSV 파일 경로
        csv_file = os.path.join('data', 'match_champions.csv')
        matches = load_matches(csv_file)
        solutions = []
        find_disjoint_matches_all(matches, target_matches, 0, set(), [], solutions, max_solutions)

        if solutions:
            print(f"챔피언이 겹치지 않는 {target_matches}개 경기 집합 (총 {len(solutions)}개):")
            for sol in solutions:
                print(sol)
        else:
            print("조건에 맞는 경기 집합을 찾을 수 없습니다.")



    
    @staticmethod
    def find_disjoint_matches_combinations_with_initial(
        target_matches,             # 원하는 최종 match_id 개수
        max_solutions,              # 최대 몇 개의 서로 다른 조합을 찾을지
        initial_matches,            # 이미 겹치지 않는 match_id 리스트 (예: ['KR-123', ...])
        csv_file_path=None          # 매치 CSV 파일 경로(기본값 None -> 예시 data폴더)
    ):
        if csv_file_path is None:
            csv_file_path = os.path.join('data', 'match_champions.csv')
        

        def load_matches(csv_path):
            """CSV에서 (match_id, 해당 매치에 등장한 champion들의 집합) 형태로 로드"""
            matches = []
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)  # 헤더 건너뛰기
                for row in reader:
                    match_id = row[0]
                    champions = row[1:]
                    matches.append((match_id, set(champions)))
            return matches

        def find_disjoint_matches_additional(matches, target, start_index,
                                            used_champions, selected,
                                            solutions, max_solutions):
            """
            이미 selected 에 일부 match_id가 들어가 있고,
            used_champions 에는 이때까지 선택된 매치들의 챔피언이 전부 들어가 있다고 가정한다.
            
            (matches는 (match_id, champion_set) 리스트)
            target은 '최종적으로 원하는 match_id의 총 개수'
            start_index부터 탐색을 시작하며,
            겹치는 챔피언이 없으면 match_id를 선택(selected에 추가)해서 다음 단계로 넘어간다.
            """
            # 만약 현재 selected 개수가 target에 도달했다면 하나의 조합을 완성한 것이므로 저장
            if len(selected) == target:
                solutions.append(selected.copy())
                return
            
            for i in range(start_index, len(matches)):
                # 이미 원하는 조합 수를 충분히 찾았다면 중단
                if len(solutions) >= max_solutions:
                    break
                
                match_id, champs = matches[i]
                
                # 이미 초기 리스트에 들어간 match_id는 중복으로 사용하지 않도록 건너뜀
                if match_id in selected:
                    continue
                
                # 겹치는 챔피언이 있는지 확인
                if used_champions & champs:
                    continue

                # 새 매치 선택
                selected.append(match_id)
                new_used = used_champions.union(champs)
                
                # 다음 매치 탐색 (i+1부터)
                find_disjoint_matches_additional(matches, target, i+1,
                                                new_used, selected,
                                                solutions, max_solutions)
                
                # 백트래킹 (원상복구)
                selected.pop()

        # CSV 로드
        matches = load_matches(csv_file_path)
        
        # 이미 주어진 match_id들의 챔피언 집합 구하기
        used_champions = set()
        for match_id, champ_set in matches:
            if match_id in initial_matches:
                used_champions |= champ_set
        
        # 현재까지 선택된 match_id 개수
        current_len = len(initial_matches)
        
        # 이미 target_matches 이상 들어있다면 그대로 한 가지 해답으로 처리
        # (만약 target_matches < current_len이면 로직상 더 줄일 순 없으니 그대로 리턴)
        if current_len >= target_matches:
            return [initial_matches]
        
        # 재귀를 통해 추가로 뽑아야 하는 수
        missing = target_matches - current_len
        
        solutions = []
        
        # 초기 selected에 initial_matches를 넣은 채로 시작
        selected = initial_matches.copy()
        
        # 재귀 호출
        find_disjoint_matches_additional(matches,
                                        target_matches,
                                        start_index=0,
                                        used_champions=used_champions,
                                        selected=selected,
                                        solutions=solutions,
                                        max_solutions=max_solutions)
        
        return solutions
    
    def find_matches_combinations_with_initial_allow_duplicate_2(
            self,
            distinct_champion_target=170,   # 목표 서로 다른 챔피언 수
            max_solutions=10,               # 최대 반환할 해법 수
            initial_matches=None,           # 이미 선택된 경기 리스트
            csv_file_path=None              # CSV 경로
    ):
        if initial_matches is None:
            initial_matches = []
        if csv_file_path is None:
            csv_file_path = os.path.join('data', 'match_champions.csv')

        # ① CSV 로드
        def load_matches(csv_path):
            matches = []
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    match_id = row[0]
                    champions = set(row[1:])
                    matches.append((match_id, champions))
            return matches

        # ② API 호출 (CSV에 없을 때만)
        def get_champnames_per_match(matchid):
            url = f'https://asia.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={self.api_key}'
            data = requests.get(url, timeout=3).json()
            return [p['championName'] for p in data['info']['participants']]

        matches = load_matches(csv_file_path)
        csv_ids = {mid for mid, _ in matches}

        # ③ 초기 used_champions 준비
        used_champs = set()
        for mid in initial_matches:
            if mid in csv_ids:
                used_champs |= dict(matches)[mid]
            else:
                if not self.api_key:
                    raise ValueError(f"API key required for match {mid}")
                used_champs |= set(get_champnames_per_match(mid))

        # 초기 세트만으로 목표 달성?
        if len(used_champs) >= distinct_champion_target:
            print(f"초기 조합만으로도 → 경기 {len(initial_matches)}, 고유 챔피언 {len(used_champs)}")
            return [initial_matches]

        solutions = []
        best_len = float('inf')

        # 스택: (start_idx, current_union, selected_matches)
        stack = [(0, used_champs, initial_matches.copy())]

        while stack and len(solutions) < max_solutions:
            start, union_champs, selected = stack.pop()

            # 목표 달성
            if len(union_champs) >= distinct_champion_target:
                # 해법 기록
                if len(selected) < best_len:
                    best_len = len(selected)
                    solutions.clear()
                if len(selected) == best_len:
                    solutions.append(selected.copy())
                continue

            # 가지치기: 이미 현재 best_len보다 크면 볼 필요 없음
            if len(selected) >= best_len:
                continue

            # 다음 후보
            for i in range(start, len(matches)):
                mid, champs = matches[i]
                if mid in selected:
                    continue
                # 겹치는 챔피언 개수
                overlap = len(union_champs & champs)
                if overlap > 5:
                    continue  # 중복이 6개 이상인 매치는 스킵

                new_union = union_champs | champs
                new_selected = selected + [mid]
                stack.append((i+1, new_union, new_selected))

        # 결과 출력
        if not solutions:
            print("조건을 만족하는 조합을 찾을 수 없습니다.")
            return []

        final = []
        for idx, sol in enumerate(solutions, 1):
            # 고유 챔피언 수 계산
            cu = set()
            for m in sol:
                if m in csv_ids:
                    cu |= dict(matches)[m]
                else:
                    cu |= set(get_champnames_per_match(m))
            print(f"[솔루션 {idx}] 경기 수={len(sol)}, 고유 챔피언 수={len(cu)} → {sol}")
            final.append(sol)

        return final

    


    def find_matches_combinations_with_initial_allow_duplicate(self,
            distinct_champion_target=170,   # 목표 서로 다른 챔피언 수
            max_solutions=10,               # 최대 반환할 해법 수
            initial_matches=None,           # 이미 선택된 경기 리스트
            csv_file_path=None              # CSV 파일 경로
    ):
        import os, csv, requests

        if initial_matches is None:
            initial_matches = []
        if csv_file_path is None:
            csv_file_path = os.path.join('data', 'match_champions.csv')

        # ① CSV 로드
        def load_matches(csv_path):
            matches = []
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # header skip
                for row in reader:
                    match_id = row[0]
                    champions = set(row[1:])
                    matches.append((match_id, champions))
            return matches

        # ② API 호출 (필요 시)
        def get_champnames_per_match(matchid):
            url = f'https://asia.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={self.api_key}'
            data = requests.get(url, timeout=3).json()
            return [p['championName'] for p in data['info']['participants']]

        # 매치 데이터 불러오기
        matches = load_matches(csv_file_path)
        id2champs = {mid: champs for mid, champs in matches}
        csv_ids = set(id2champs.keys())

        # ③ initial_matches로부터 used_champions 구성
        used_champions = set()
        for mid in initial_matches:
            if mid in csv_ids:
                used_champions |= id2champs[mid]
            else:
                if not self.api_key:
                    raise ValueError(f"API Key 필요: CSV에 없는 match '{mid}' 정보 조회용")
                used_champions |= set(get_champnames_per_match(mid))

        # 초기만으로 목표 달성 시
        if len(used_champions) >= distinct_champion_target:
            print(f"초기만으로 충분: 경기 {len(initial_matches)}, 고유 챔피언 {len(used_champions)}개")
            return [initial_matches]

        solutions = []
        best_len = float('inf')
        stack = [(0, used_champions, initial_matches.copy())]

        # ④ DFS + 백트래킹
        while stack and len(solutions) < max_solutions:
            start_index, curr_union, selected = stack.pop()

            # 목표 달성
            if len(curr_union) >= distinct_champion_target:
                if len(selected) < best_len:
                    best_len = len(selected)
                    solutions.clear()
                if len(selected) == best_len:
                    solutions.append(selected.copy())
                continue

            # 가지치기
            if len(selected) >= best_len:
                continue

            # 다음 후보
            for i in range(start_index, len(matches)):
                mid, champs = matches[i]
                if mid in selected:
                    continue
                new_union = curr_union | champs
                new_selected = selected + [mid]
                stack.append((i+1, new_union, new_selected))

        # ⑤ 결과 출력(경기 수, 고유 챔피언 수) 후 반환
        if not solutions:
            print("조건을 만족하는 조합을 찾지 못했습니다.")
            return []

        for idx, sol in enumerate(solutions, 1):
            # 고유 챔피언 수 계산
            champ_set = set()
            for m in sol:
                if m in csv_ids:
                    champ_set |= id2champs[m]
                else:
                    champ_set |= set(get_champnames_per_match(m))
            print(f"[솔루션 {idx}] 경기 수 = {len(sol)}, 고유 챔피언 수 = {len(champ_set)} → {sol}")

        return solutions


    def find_disjoint_matches_combinations_with_initial_ver2(
            self,
            target_matches: int,
            max_solutions: int,
            initial_matches: list[str],
            csv_file_path: str | None = None,
            max_duplicates: int = 0              # ← 새로 추가: n개까지 중복 허용
    ):

        if csv_file_path is None:
            csv_file_path = os.path.join('data', 'match_champions.csv')
        if initial_matches is None:
            initial_matches = []

        # ─────────────────────────────── CSV 로드
        with open(csv_file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            matches = [(row[0], set(row[1:])) for row in reader]

        id2champs = {mid: champs for mid, champs in matches}
        csv_ids   = set(id2champs.keys())

        # ─────────────────────────────── API helper
        _api_cache: dict[str, set[str]] = {}

        def champs_from_api(matchid: str) -> set[str]:
            if matchid in _api_cache:
                return _api_cache[matchid]
            if not getattr(self, "api_key", None):
                raise ValueError("API key가 필요합니다")
            url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={self.api_key}"
            data = requests.get(url, timeout=3).json()
            names = {p["championName"] for p in data["info"]["participants"]}
            _api_cache[matchid] = names
            return names

        # ─────────────────────────────── 초기 상태
        used = set()
        for mid in initial_matches:
            used |= id2champs[mid] if mid in csv_ids else champs_from_api(mid)

        # 초기 조합이 목표 경기 수 이상인 경우
        if len(initial_matches) >= target_matches:
            print(f"[초기] 경기 {len(initial_matches)}, 고유 챔피언 {len(used)}")
            return [initial_matches]

        # 새 챔피언 많이 주는 순서로 정렬
        sorted_matches = sorted(matches,
                                key=lambda mc: len(mc[1] - used),
                                reverse=True)

        solutions: list[list[str]] = []

        # ─────────────────────────────── DFS (중복 n개 허용)
        def dfs(start: int, union: set, chosen: list, dupes_used: int):
            if len(chosen) == target_matches:
                solutions.append(chosen.copy())
                return
            if len(solutions) >= max_solutions:
                return

            for idx in range(start, len(sorted_matches)):
                mid, champs = sorted_matches[idx]
                if mid in chosen:
                    continue

                overlap = union & champs
                new_dupes = len(overlap)
                if dupes_used + new_dupes > max_duplicates:
                    continue  # 허용 중복 초과

                chosen.append(mid)
                dfs(idx + 1, union | champs, chosen, dupes_used + new_dupes)
                chosen.pop()

                if len(solutions) >= max_solutions:
                    return

        dfs(0, used, initial_matches.copy(), dupes_used=0)

        # ─────────────────────────────── 결과
        if not solutions:
            print("조건에 맞는 조합을 찾지 못했습니다.")
            return []

        for i, combo in enumerate(solutions, 1):
            champ_set = set()
            for m in combo:
                champ_set |= id2champs[m] if m in csv_ids else champs_from_api(m)
            print(f"[솔루션 {i}] 경기 {len(combo)}, 고유 챔피언 {len(champ_set)} "
                f"(중복 허용 {max_duplicates}) → {combo}")

        return solutions


    def find_disjoint_matches_combinations_with_initial_ver3(
            self,
            target_matches: int,
            max_solutions: int,
            initial_matches: list[str] | None = None,
            csv_file_path: str | None = None,
            max_duplicates: int = 0,
            verbose: bool = True,
    ):
        """
        중복 챔피언을 max_duplicates명까지 허용하며, target_matches개의 경기 조합을 찾는다.
        - initial_matches: 이미 선택된 match_id 리스트
        - max_solutions  : 반환할 최대 솔루션 수
        - verbose=True   : 진행 로그·통계 출력
        """
        import os, csv, requests, itertools

        if csv_file_path is None:
            csv_file_path = os.path.join("data", "match_champions.csv")
        if initial_matches is None:
            initial_matches = []

        # ─────────────────────────────── ① CSV 로드 + 전체 고유 챔피언 수
        with open(csv_file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # header skip
            matches = [(row[0], set(row[1:])) for row in reader]

        all_unique_champs = set().union(*(ch for _, ch in matches))
        if verbose:
            print(f"CSV 전체 경기 통틀어 고유 챔피언 수: {len(all_unique_champs)}명\n")

        id2champs = {mid: champs for mid, champs in matches}
        csv_ids   = set(id2champs.keys())

        # ─────────────────────────────── ② API helper (CSV에 없는 경기 처리)
        _api_cache: dict[str, set[str]] = {}

        def champs_from_api(matchid: str) -> set[str]:
            if matchid in _api_cache:
                return _api_cache[matchid]
            if not getattr(self, "api_key", None):
                raise ValueError("self.api_key가 설정돼 있지 않습니다.")
            url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchid}?api_key={self.api_key}"
            data = requests.get(url, timeout=3).json()
            names = {p["championName"] for p in data["info"]["participants"]}
            _api_cache[matchid] = names
            return names

        # ─────────────────────────────── ③ 초기 상태
        used = set()
        for mid in initial_matches:
            used |= id2champs[mid] if mid in csv_ids else champs_from_api(mid)

        if len(initial_matches) >= target_matches:
            print(f"[초기] 경기 {len(initial_matches)}, 고유 챔피언 {len(used)}")
            return [initial_matches]

        # 새 챔피언 기여가 큰 순서로 정렬
        sorted_matches = sorted(
            matches,
            key=lambda mc: len(mc[1] - used),
            reverse=True,
        )

        # ─────────────────────────────── ④ DFS 탐색
        solutions: list[list[str]] = []
        node_counter = itertools.count(1)  # 방문 노드 카운터

        def dfs(start: int, union: set, chosen: list, dupes_used: int, depth: int):
            # 1000개 노드마다 진행 상황 출력
            if verbose and next(node_counter) % 1000 == 0:
                print(f"depth={depth:<2} | 탐색 노드={next(node_counter)-1:<7} "
                    f"| 선택 경기={len(chosen)} | 중복 사용={dupes_used}")

            if len(chosen) == target_matches:
                solutions.append(chosen.copy())
                if verbose:
                    print(f"✔️  솔루션 발견! (경기 {len(chosen)})")
                return
            if len(solutions) >= max_solutions:
                return

            for idx in range(start, len(sorted_matches)):
                mid, champs = sorted_matches[idx]
                if mid in chosen:
                    continue

                overlap_cnt = len(union & champs)
                if dupes_used + overlap_cnt > max_duplicates:
                    continue  # 허용 중복 초과

                chosen.append(mid)
                dfs(idx + 1,
                    union | champs,
                    chosen,
                    dupes_used + overlap_cnt,
                    depth + 1)
                chosen.pop()

                if len(solutions) >= max_solutions:
                    return

        dfs(0, used, initial_matches.copy(), dupes_used=0, depth=0)

        # ─────────────────────────────── ⑤ 결과 출력
        if not solutions:
            print("조건에 맞는 조합을 찾지 못했습니다.")
            return []

        for i, combo in enumerate(solutions, 1):
            champ_set = set()
            for m in combo:
                champ_set |= id2champs[m] if m in csv_ids else champs_from_api(m)
            print(f"\n[솔루션 {i}] "
                f"경기 {len(combo)}, 고유 챔피언 {len(champ_set)} "
                f"(중복 허용 {max_duplicates})\n→ {combo}")

        return solutions



    def find_disjoint_matches_combinations_with_initial_ver4(
            self,
            target_matches: int,
            max_solutions: int,
            initial_matches: list[str] | None = None,
            csv_file_path: str | None = None,
            max_duplicates: int = 0,
            verbose: bool = True,
    ):
        """
        중복 챔피언 max_duplicates명까지 허용.
        반환: [(match_id_list, unique_champion_set, coverage_ratio), ...]
        """
        import os, csv, requests, itertools

        if csv_file_path is None:
            csv_file_path = os.path.join("data", "match_champions.csv")
        if initial_matches is None:
            initial_matches = []

        # ───────────────────────── ① CSV 로드 + 전체 고유 챔피언 수
        with open(csv_file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            matches = [(row[0], set(row[1:])) for row in reader]

        all_unique_champs = set().union(*(ch for _, ch in matches))
        if verbose:
            print(f"CSV 전체 경기 통틀어 고유 챔피언 수: {len(all_unique_champs)}명\n")

        id2champs = {mid: champs for mid, champs in matches}
        csv_ids   = set(id2champs.keys())

        # ───────────────────────── ② API helper
        _api_cache: dict[str, set[str]] = {}

        def champs_from_api(matchid: str) -> set[str]:
            if matchid in _api_cache:
                return _api_cache[matchid]
            if not getattr(self, "api_key", None):
                raise ValueError("self.api_key가 필요합니다.")
            url = (f"https://asia.api.riotgames.com/lol/match/v5/matches/"
                f"{matchid}?api_key={self.api_key}")
            data = requests.get(url, timeout=3).json()
            names = {p["championName"] for p in data["info"]["participants"]}
            _api_cache[matchid] = names
            return names

        # ───────────────────────── ③ 초기 상태
        used = set()
        for mid in initial_matches:
            used |= id2champs[mid] if mid in csv_ids else champs_from_api(mid)

        if len(initial_matches) >= target_matches:
            print(f"[초기] 경기 {len(initial_matches)}, 고유 챔피언 {len(used)}")
            champ_set = used
            coverage = sum(1 for _, ch in matches if ch <= champ_set) / len(matches) * 100
            return [(initial_matches, champ_set, coverage)]

        sorted_matches = sorted(
            matches,
            key=lambda mc: len(mc[1] - used),
            reverse=True,
        )

        # ───────────────────────── ④ DFS
        solutions: list[list[str]] = []
        node_counter = itertools.count(1)

        def dfs(start: int, union: set, chosen: list, dupes_used: int, depth: int):
            if verbose and next(node_counter) % 1000 == 0:
                print(f"depth={depth:<2} | 노드={next(node_counter)-1:<7} "
                    f"| 선택={len(chosen)} | 중복={dupes_used}")
            if len(chosen) == target_matches:
                solutions.append(chosen.copy())
                if verbose:
                    print(f"✔️  솔루션 발견! (경기 {len(chosen)})")
                return
            if len(solutions) >= max_solutions:
                return

            for idx in range(start, len(sorted_matches)):
                mid, champs = sorted_matches[idx]
                if mid in chosen:
                    continue
                overlap = len(union & champs)
                if dupes_used + overlap > max_duplicates:
                    continue
                chosen.append(mid)
                dfs(idx+1, union | champs, chosen,
                    dupes_used + overlap, depth+1)
                chosen.pop()
                if len(solutions) >= max_solutions:
                    return

        dfs(0, used, initial_matches.copy(), dupes_used=0, depth=0)

        # ───────────────────────── ⑤ 결과
        if not solutions:
            print("조건에 맞는 조합을 찾지 못했습니다.")
            return []

        final_results = []

        for i, combo in enumerate(solutions, 1):
            champ_set = set()
            for m in combo:
                champ_set |= id2champs[m] if m in csv_ids else champs_from_api(m)
            # 커버리지: champ_set으로 완전히 포함되는 CSV 경기 비율
            covered = sum(1 for _, ch in matches if ch <= champ_set)
            coverage_ratio = covered / len(matches) * 100

            print(f"\n[솔루션 {i}] "
                  f"경기 {len(combo)}, 고유 챔피언 {len(champ_set)} "
                  f"(중복 허용 {max_duplicates})")
            print(f"  ▶ CSV 경기 중 {covered}/{len(matches)}개 "
                  f"({coverage_ratio:.2f}%)가 이 챔프 집합으로 커버됩니다.")
            print(f"  ▶ match_id 리스트: {combo}")

            # ▲ 경기별로 ‘이번 경기에서 새롭게 추가된 챔피언’ 계산·출력
            print("  ▶ 경기별 신규 챔피언:")
            seen = set()
            for mid in combo:
                champs = id2champs[mid] if mid in csv_ids else champs_from_api(mid)
                new_champs = champs - seen          # 이번 경기로 인해 새로 포함되는 챔프
                seen |= champs
                new_list = ", ".join(sorted(new_champs)) if new_champs else "(없음)"
                print(f"     - {mid}: {new_list}")

            final_results.append((combo, champ_set, coverage_ratio))

        return final_results



    def calc_coverage_with_initial_matches(
            self,
            initial_matches: list[str],
            csv_file_path: str | None = None,
            verbose: bool = True
    ):
        """
        initial_matches 로부터 얻은 고유 챔피언 집합이
        csv_file_path 에 존재하는 모든 경기들 중 얼마나 커버(⊆) 되는지 비율을 반환한다.
        
        반환값: (unique_champ_set, coverage_ratio, covered_count, total_matches)
        """
        import os, csv, requests

        if csv_file_path is None:
            csv_file_path = os.path.join("data", "match_champions.csv")
        if initial_matches is None:
            initial_matches = []

        # ───────────────────────── ① CSV 로드
        with open(csv_file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # header skip
            matches = [(row[0], set(row[1:])) for row in reader]

        id2champs = {mid: champs for mid, champs in matches}
        csv_ids   = set(id2champs.keys())

        # ───────────────────────── ② API helper (CSV에 없는 경기)
        _api_cache: dict[str, set[str]] = {}

        def champs_from_api(matchid: str) -> set[str]:
            if matchid in _api_cache:
                return _api_cache[matchid]
            if not getattr(self, "api_key", None):
                raise ValueError("self.api_key가 필요합니다.")
            url = (f"https://asia.api.riotgames.com/lol/match/v5/matches/"
                f"{matchid}?api_key={self.api_key}")
            data = requests.get(url, timeout=3).json()
            names = {p["championName"] for p in data["info"]["participants"]}
            _api_cache[matchid] = names
            return names

        # ───────────────────────── ③ initial_matches → champ_set
        champ_set = set()
        for mid in initial_matches:
            champ_set |= id2champs[mid] if mid in csv_ids else champs_from_api(mid)

        # ───────────────────────── ④ 커버리지 계산
        total = len(matches)
        covered = sum(1 for _, champs in matches if champs <= champ_set)
        coverage_ratio = covered / total * 100 if total else 0.0

        if verbose:
            print(f"▶ 초기 match 수          : {len(initial_matches)}")
            print(f"▶ 고유 챔피언 수         : {len(champ_set)}")
            print(f"▶ CSV 경기 총            : {total}")
            print(f"▶ 완전히 커버된 경기 수   : {covered}")
            print(f"▶ 커버리지               : {coverage_ratio:.2f}%")

        return champ_set, coverage_ratio, covered, total



    def find_best_coverage_with_additional_matches(
            self,
            initial_matches: list[str],      # 고정 match_id 리스트
            add_matches: list[str],          # 추가 후보 match_id 리스트
            n: int,                          # add_matches 중에서 고를 개수
            csv_file_path: str | None = None,
            top_k: int | None = 100,         # 후보가 많을 때 상위 k개만 브루트포스 (None이면 전체)
    ):
        """
        initial_matches는 고정, add_matches 중 n개를 더해
        CSV 경기 커버리지를 최대화하는 조합을 탐색.
        반환: (best_combo, coverage_ratio, covered_cnt, total_cnt)
        """
        import os, csv, itertools, requests

        if csv_file_path is None:
            csv_file_path = os.path.join("data", "match_champions.csv")

        # ───────────────── CSV 로드
        with open(csv_file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            csv_matches = [(row[0], set(row[1:])) for row in reader]

        id2champs = {mid: champs for mid, champs in csv_matches}
        csv_ids   = set(id2champs.keys())

        # ───────────────── API helper
        _cache: dict[str, set[str]] = {}

        def champs_api(mid):
            if mid in _cache:
                return _cache[mid]
            url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{mid}?api_key={self.api_key}"
            data = requests.get(url, timeout=3).json()
            names = {p["championName"] for p in data["info"]["participants"]}
            _cache[mid] = names
            return names

        # ───────────────── initial 챔프 집합
        base_champs = set()
        for m in initial_matches:
            base_champs |= id2champs[m] if m in csv_ids else champs_api(m)

        # ───────────────── add_matches의 새 챔피언 기여 계산
        add_info = []
        for m in add_matches:
            champs = id2champs[m] if m in csv_ids else champs_api(m)
            gain   = len(champs - base_champs)
            add_info.append((gain, m, champs))

        # 기여도가 높은 순으로 정렬
        add_info.sort(reverse=True)

        # top_k로 컷 (옵션)
        if top_k is not None and len(add_info) > top_k:
            add_info = add_info[:top_k]

        # ───────────────── 조합 탐색
        best_combo, best_cov, best_cnt = None, -1.0, 0
        total_csv = len(csv_matches)

        for combo in itertools.combinations(add_info, n):
            combo_ids   = [m for _, m, _ in combo]
            combo_champ = base_champs.union(*(c for _, _, c in combo))

            covered = sum(1 for _, champs in csv_matches if champs <= combo_champ)
            cov_pct = covered / total_csv * 100

            if cov_pct > best_cov:
                best_cov, best_combo, best_cnt = cov_pct, combo_ids, covered

        # ───────────────── 결과 출력
        if best_combo is None:
            print("조건에 맞는 조합을 찾지 못했습니다.")
            return None

        print(f"\n■ 초기 {len(initial_matches)}경기 + 추가 {n}경기 조합 결과")
        print(f"  ▶ 최적 match_id 조합 : {best_combo}")
        print(f"  ▶ 커버리지          : {best_cnt}/{total_csv} "
            f"({best_cov:.2f}%)")
        print(f"  ▶ 고유 챔피언 수     : {len(base_champs.union(*(id2champs[m] if m in csv_ids else champs_api(m)
                                                        for m in best_combo)))}")

        return best_combo, best_cov, best_cnt, total_csv


    def save_summoner_leagueinfo_of_replays(
        self,
        replay_dir: str,
        save_folder: str,
        region: str = "KR",
        queue_type: str = "RANKED_SOLO_5x5",
        max_workers: int = 8,            # 🌟 동시에 돌릴 스레드 수
    ):
        """
        replay_dir 의 .rofl 파일들을 기반으로
        소환사 10인의 랭크 정보를 JSON(경기별 1파일)로 병렬 저장.
        """
        import os, json, requests

        os.makedirs(save_folder, exist_ok=True)

        rofl_files = [f for f in os.listdir(replay_dir) if f.endswith(".rofl")]
        print(f"총 {len(rofl_files)}개의 리플레이 파일을 처리합니다.")

        # ── 내부 함수: 한 경기 처리 ───────────────────────────────────
        def process_one_match(rofl_name: str):
            match_id_api = os.path.splitext(rofl_name)[0].replace("-", "_")
            json_path = os.path.join(save_folder, f"{match_id_api}.json")
            if os.path.exists(json_path):
                return  # 이미 있음

            # 1) match → puuid 10개
            url_match = (f"https://asia.api.riotgames.com/lol/match/v5/matches/"
                        f"{match_id_api}?api_key={self.api_key}")
            try:
                match_data = requests.get(url_match, timeout=5).json()
                puuids = match_data.get("metadata", {}).get("participants", [])
                if len(puuids) != 10:
                    return
            except Exception:
                return

            # 2) 각 puuid → 랭크 정보
            players = []
            for puuid in puuids:
                url_rank = (f"https://kr.api.riotgames.com/lol/league/v4/entries/by-puuid/"
                            f"{puuid}?api_key={self.api_key}")
                try:
                    data = requests.get(url_rank, timeout=5).json()
                except Exception:
                    continue

                solo = next((e for e in data if e.get("queueType") == queue_type), None)
                players.append({
                    "puuid": puuid,
                    "tier":  solo.get("tier", "UNRANKED") if solo else "UNRANKED",
                    "rank":  solo.get("rank", "")         if solo else "",
                    "leaguePoints": solo.get("leaguePoints", 0) if solo else 0,
                    "wins":  solo.get("wins", 0)          if solo else 0,
                    "losses": solo.get("losses", 0)       if solo else 0,
                })

            # 3) JSON 저장
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump({"match_id": match_id_api, "players": players},
                        jf, ensure_ascii=False, indent=4)

        # ── 진행 막대(딱 한 개) ──────────────────────────────────────
        progress_cols = [
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        ]
        with Progress(*progress_cols, transient=True) as progress:
            task = progress.add_task("Fetching rank data…", total=len(rofl_files))

            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {pool.submit(process_one_match, r): r for r in rofl_files}

                for _ in as_completed(futures):
                    progress.advance(task)

    def save_summoner_leagueinfo_from_csv(
        self,
        csv_in: str  = "data/match_champ_dict(25.13).csv",
        save_folder: str = "data/match_info",
        region: str = "KR",
        queue_type: str = "RANKED_SOLO_5x5",
        max_workers: int = 4,               # 🌟 동시에 돌릴 스레드 수
    ):
        """
        CSV에 있는 match_id별로 소환사 랭크 정보를 JSON(경기당 1파일)로 저장한다.
        - CSV에는 반드시 'match_id' 컬럼이 있어야 함.
        """
        import pandas as pd, os, json, requests

        # ── 출력 폴더 준비 ────────────────────────────────────────────
        os.makedirs(save_folder, exist_ok=True)

        # ── match_id 목록 로드 ───────────────────────────────────────
        df = pd.read_csv(csv_in)
        if "match_id" not in df.columns:
            raise ValueError(f"'match_id' 컬럼이 없습니다 → {csv_in}")

        match_ids = [mid for mid in df["match_id"].dropna().unique()
                    if str(mid).startswith(f"{region}_")]
        print(f"총 {len(match_ids)}개의 match_id를 처리합니다.")

        # ── 내부 함수: 한 경기 처리 ──────────────────────────────────
        def process_one_match(match_id_api: str):
            json_path = os.path.join(save_folder, f"{match_id_api}.json")
            if os.path.exists(json_path):        # 이미 있으면 스킵
                return

            # 1) match → puuid 10개
            url_match = (f"https://asia.api.riotgames.com/lol/match/v5/matches/"
                        f"{match_id_api}?api_key={self.api_key}")
            try:
                match_data = requests.get(url_match, timeout=5).json()
                puuids = match_data.get("metadata", {}).get("participants", [])
                if len(puuids) != 10:
                    return
            except Exception:
                return

            # 2) 각 puuid → 랭크 정보
            players = []
            for puuid in puuids:
                url_rank = (f"https://kr.api.riotgames.com/lol/league/v4/entries/by-puuid/"
                            f"{puuid}?api_key={self.api_key}")
                try:
                    data = requests.get(url_rank, timeout=5).json()
                except Exception:
                    continue
                solo = next((e for e in data if e.get("queueType") == queue_type), None)
                players.append({
                    "puuid": puuid,
                    "tier":  solo.get("tier", "UNRANKED") if solo else "UNRANKED",
                    "rank":  solo.get("rank", "")         if solo else "",
                    "leaguePoints": solo.get("leaguePoints", 0) if solo else 0,
                    "wins":  solo.get("wins", 0)          if solo else 0,
                    "losses": solo.get("losses", 0)       if solo else 0,
                })

            # 3) JSON 저장
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump({"match_id": match_id_api, "players": players},
                        jf, ensure_ascii=False, indent=4)

        # ── 진행 막대 설정 (하나만) ─────────────────────────────────
        progress_cols = [
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        ]
        with Progress(*progress_cols, transient=True) as progress:
            task = progress.add_task("Fetching rank data…", total=len(match_ids))

            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {pool.submit(process_one_match, mid): mid for mid in match_ids}

                for fut in as_completed(futures):
                    progress.advance(task)       # 한 경기 완료될 때마다 1칸 전진



    def save_match_avg_score_from_json(
        self,
        match_info_dir: str,
        output_csv_path: str,
    ):
        """
        match_info_dir 안의 *.json(경기별 소환사 랭크 정보) → 
        10인 평균 점수를 계산해 output_csv_path에 저장한다.

        Args:
            match_info_dir (str)  : KR_xxx.json 파일들이 들어 있는 디렉터리
            output_csv_path (str) : 결과 CSV 경로 (헤더: match_id,avg_score)
        """

        # ── ① 점수 변환 기준 ───────────────────────────────────────
        tier_points = {
            "BRONZE": 0, "SILVER": 400, "GOLD": 800,
            "PLATINUM": 1200, "EMERALD": 1600,
            "DIAMOND": 2000, "MASTER": 2400,
            "GRANDMASTER": 2800, "CHALLENGER": 3200,
        }
        rank_points = {"I": 300, "II": 200, "III": 100, "IV": 0}

        # ── ② 결과 CSV 헤더 준비 (없으면 생성) ─────────────────────
        file_exists = os.path.exists(output_csv_path)
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        if not file_exists:
            with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["match_id", "avg_score"])

        # ── ③ JSON 순회 ───────────────────────────────────────────
        json_files = [fn for fn in os.listdir(match_info_dir) if fn.endswith(".json")]
        for fn in track(json_files, description="Calculating average scores…"):
            path = os.path.join(match_info_dir, fn)
            with open(path, "r", encoding="utf-8") as jf:
                data = json.load(jf)

            match_id = data.get("match_id")
            players  = data.get("players", [])
            if not match_id or len(players) != 10:
                continue  # 정보 부족 → 스킵

            scores = []
            for p in players:
                tier = str(p.get("tier", "")).upper()
                rank = str(p.get("rank", "")).upper()
                lp   = int(p.get("leaguePoints", 0))

                base  = tier_points.get(tier, 0)
                bonus = rank_points.get(rank, 0)
                scores.append(base + bonus + lp)

            if not scores:
                continue

            avg_score = sum(scores) / len(scores)

            # ── ④ CSV에 기록(append) ──────────────────────────────
            with open(output_csv_path, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([match_id, avg_score])









    # ==========================================================
    # ① Timeline 분석용 헬퍼 메서드들
    # ==========================================================
    @staticmethod
    def _format_timestamp_ms(ts_ms: int) -> str:
        m, s = divmod(round(ts_ms / 1000), 60)
        return f"{m}:{s:02d}"

    @staticmethod
    def get_matchids(full_matchids: list[str]) -> list[str]:
        """'KR-7650415714' → '7650415714'로 변환해 정렬"""
        nums = [mid.replace("KR-", "") for mid in full_matchids if mid.startswith("KR-")]
        nums.sort()
        return nums
    
    @staticmethod
    def get_matchids2(full_matchids: list[str]) -> list[str]:
        """'KR-7650415714' → '7650415714'로 변환해 정렬"""
        nums = [mid.replace("KR_", "") for mid in full_matchids if mid.startswith("KR_")]
        nums.sort()
        return nums

    def _get_match_timeline_data(self, match_id_num: str, max_retries: int = 5) -> dict:
        """Riot Timeline API 호출 (간단 rate-limit 대응 포함)"""
        url = (f"https://asia.api.riotgames.com/lol/match/v5/matches/"
               f"KR_{match_id_num}/timeline")
        params = {"api_key": self.api_key}

        for _ in range(max_retries):
            try:
                resp = requests.get(url, params=params)
                if resp.status_code == 429:        # Too Many Requests
                    wait = int(resp.headers.get("Retry-After", "2"))
                    time.sleep(wait)
                    continue
                if 500 <= resp.status_code < 600:  # 서버 오류
                    time.sleep(2)
                    continue
                resp.raise_for_status()
                time.sleep(random.uniform(0.1, 0.3))
                return resp.json()
            except requests.exceptions.RequestException:
                time.sleep(2)
        raise ValueError(f"[{match_id_num}] timeline 호출 재시도 초과")

    @staticmethod
    def _get_champion_kill_logs(tl_data: dict) -> list[dict]:
        logs = []
        for frame in tl_data["info"]["frames"]:
            for ev in frame.get("events", []):
                if ev.get("type") == "CHAMPION_KILL":
                    logs.append({
                        **ev,
                        "formatted_time": RiotAPI._format_timestamp_ms(ev["timestamp"]),
                        "minute": ev["timestamp"] // 60000
                    })
        return logs

    @staticmethod
    def _bind_kill_event_per_minute(kill_logs: list[dict]) -> dict:
        by_min = defaultdict(list)
        for ev in kill_logs:
            by_min[ev["minute"]].append({
                "formatted_time": ev["formatted_time"],
                "position": ev.get("position")
            })
        return {
            str(m): {"event_count": len(v), "events": v}
            for m, v in by_min.items() if len(v) >= 4
        }

    @staticmethod
    def _get_frequent_kill_minute(kill_per_min: dict, kill_events_threshold: int = 4) -> list[int]:
        return sorted(int(m) for m, info in kill_per_min.items()
                      if info["event_count"] >= kill_events_threshold)

    def _process_one_match(self, matchid_num: str, kill_events_threshold) -> list[int]:
        tl = self._get_match_timeline_data(matchid_num)
        kills = self._get_champion_kill_logs(tl)
        per_min = self._bind_kill_event_per_minute(kills)
        return self._get_frequent_kill_minute(per_min, kill_events_threshold)

    # ==========================================================
    # ② .json 저장 메서드 (멀티-프로세싱)
    # ==========================================================
    def save_kill_events_from_matchlist(
        self,
        matchids: list[str],
        output_json_path: str | None = None,
        kill_events_threshold: int = 4,
        max_workers: int = 2,
    ):
        """
        KR-xxxx 형식 match_id 리스트를 받아
        타임라인에서 분당 킬 이벤트 ≥4인 분(minute)을 찾아
        save_dir/data.json 에 누적 저장.
        """
 
        # 기존 결과 불러오기
        if os.path.exists(output_json_path):
            with open(output_json_path, "r", encoding="utf-8") as f:
                result = json.load(f)
        else:
            result = {"data": {}}

        nums = self.get_matchids2(matchids)
        to_do = [m for m in nums if m not in result["data"]]
        if not to_do:
            print("모든 match_id가 이미 처리됨.")
            return

        # 멀티프로세싱
        from multiprocessing import set_start_method
        try:
            set_start_method("spawn", force=True)
        except RuntimeError:
            pass

        with ProcessPoolExecutor(max_workers=max_workers) as exe:
            fut_map = {exe.submit(self._process_one_match, mid, kill_events_threshold): mid for mid in to_do}

            for fut in track(as_completed(fut_map), total=len(fut_map),
                             description="Processing matches…"):
                mid = fut_map[fut]
                try:
                    minutes = fut.result()
                    result["data"][mid] = minutes
                except Exception as e:
                    print(f"{mid} 실패: {e}")

                # 중간 저장
                with open(output_json_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

        print("✅ 모든 매치 처리 완료!")


