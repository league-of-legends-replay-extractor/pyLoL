import requests
import time
from tqdm import tqdm
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

'''데이터셋 생성기, 원하는 티어 입력해주면 해당 티어대의 리플레이들을 저장해준다.'''

class DataGenerator(object):

    '''
        api_key : riot api key
        count : match per each player
    '''
    def __init__(self , api_key , count):
        self.api_key = api_key
        self.count = count

    '''
    queue : {RANKED_SOLO_5x5, RANKED_TFT, RANKED_FLEX_SR, RANKED_FLEX_TT}
    tier : {CHALLENGER, GRANDMASTER, MASTER, DIAMOND, PLATINUM, GOLD, SILVER, BRONZE, IRON}   !NOTICE: 'MASTER+' ONLY TAKE DIVISION 'I'
    division : {I, II, III, IV}
    '''
    def get_puuids(self, queue , tier , division): #queue : RANKED_SOLO_5x5 #tier : CHALLENGER(대문자) #division : I ~ IV
        page = 1             #페이지 초기값
        summoners_puuids = []       #소환사 명단
        while True:
            datas = requests.get(f'https://kr.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}&api_key={self.api_key}').json()
            if len(datas) == 0 or page > 300 :
                break
            page = page + 1
            for data in datas:
                summoners_puuids.append(data['puuid'])

        return summoners_puuids
    
    #SUMMONERID -> PUUID
    def get_puuid(self, summonerId):
        try:
            puuid = requests.get(f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}?api_key={self.api_key}').json()["puuid"]
            # print(f'puuid : {puuid}')
            return puuid
        except:
            return None
        

    def is_in_recent_patch(self, game_creation_millisec, patch_start_datetime):
        
        dt_obj = datetime.strptime(patch_start_datetime,'%Y.%m.%d')
        patch_start_millisec = dt_obj.timestamp() * 1000

        return patch_start_millisec < game_creation_millisec
    
    
        
    #PUUID -> MATCHID(S)
    def get_matchIds(self, puuid, patch_start_datetime, min_game_duration, max_game_duration):


        def convert_humantime_to_unixtimestamp(humantime): # 2024.09.25 >> 1727265600
            # 문자열을 datetime 객체로 변환
            date_obj = datetime.strptime(humantime, '%Y.%m.%d').replace(hour=12, minute=0, second=0)
            # datetime 객체를 UNIX 타임스탬프(초 단위)로 변환
            unix_timestamp = int(time.mktime(date_obj.timetuple()))
            return unix_timestamp

        def add_days_to_date(date_str, days):
            # 문자열을 datetime 객체로 변환
            date_obj = datetime.strptime(date_str, '%Y.%m.%d')
            # 지정된 일수를 더함
            new_date_obj = date_obj + timedelta(days=days)
            # 다시 문자열 형식으로 변환
            new_date_str = new_date_obj.strftime('%Y.%m.%d')
            return new_date_str

        # 7일 추가 (롤 패치일이 14일 간격임을 감안.)
        patch_start_datetime_add_7days = add_days_to_date(patch_start_datetime, 7)
        
        # print("?패치 시작일 : ", patch_start_datetime)
        # print("?패치 시작일 + 7일 : ", convert_humantime_to_unixtimestamp(patch_start_datetime))
        # print("?패치 시작일 + 7일 : ", convert_humantime_to_unixtimestamp(patch_start_datetime_add_7days))
        if puuid == None:
            return []
        
        matchIdsOver15 = []
        matchIds = requests.get(f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={convert_humantime_to_unixtimestamp(patch_start_datetime)}&queue=420&type=ranked&start=0&count={self.count}&api_key={self.api_key}').json()    
        matchIds_7day_after = requests.get(f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={convert_humantime_to_unixtimestamp(patch_start_datetime_add_7days)}&queue=420&type=ranked&start=0&count={self.count}&api_key={self.api_key}').json()
        
        # print(f'총 {len(matchIds)}개의 경기 기록이 있습니다.')
        # print(f'총 {len(matchIds_7day_after)}개의 경기 기록이 있습니다. (패치 시작일 + 7일)')
        count = 0
        for matchId in matchIds:
            try:
                response = requests.get(f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchId}?api_key={self.api_key}")
                gameDuration = round(response.json()['info']['gameDuration'])
                gameCreation = round(response.json()['info']['gameCreation'])
                if (max_game_duration*60 >= gameDuration >= min_game_duration*60) and (count < self.count) and self.is_in_recent_patch(gameCreation, patch_start_datetime):
                    matchIdsOver15.append(matchId)
                    count = count + 1
                else:
                    break
            except:
                pass

        for matchId in matchIds_7day_after:
            try:
                response = requests.get(f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchId}?api_key={self.api_key}")
                gameDuration = round(response.json()['info']['gameDuration'])
                gameCreation = round(response.json()['info']['gameCreation'])
                if (max_game_duration*60 >= gameDuration >= min_game_duration*60) and (count < self.count) and self.is_in_recent_patch(gameCreation, patch_start_datetime):
                    matchIdsOver15.append(matchId)
                    count = count + 1
                else:
                    break
            except:
                pass

        # 중복 제거
        matchIdsOver15 = list(set(matchIdsOver15))  

        return matchIdsOver15

    ############## Updated match-history lookup to use PUUID, since summoner-ID queries have been removed from the Riot API.##############
    # #get matchids { precondition : queue(=랭크 타입) , tier(=티어), division(=단계, 예:I,II,III,IV) , patch_start_datetime(=패치시작일, 예: '2023.10.08')  , min_game_duration : 최소 게임 진행시간(분)}
    # def get_tier_matchIds(self, queue, tier, division , max_ids, patch_start_datetime, min_game_duration, max_game_duration):
    
    #     # process : queue, tier, division -> summonerId(s)
    #     puuids = self.get_puuids(self, queue , tier , division)[:max_ids] # max_ids 만큼만 가져오기
    #     # print("PUUIDS",puuids)
    #     matchIds = []
        
    #     # process : puuid -> matchId(s)
    #     for puuid in tqdm(puuids , 
    #                       desc = 'Gathering puuids by Riot_API from puuids(not summonerIds)... ', ## 진행률 앞쪽 출력 문장
    #                       ncols = 120, ## 진행률 출력 폭 조절
    #                       ascii = ' =', 
    #                       leave=True
    #                       ):
    #         try:
    #             matchIds.extend(self.get_matchIds(self, puuid, patch_start_datetime, min_game_duration, max_game_duration))
    #             # print(len(matchIds),"개의 경기 누적")
    #             time.sleep(0.001)
    #         except:
    #             pass
        
    #     return list(set(matchIds)) # 중복 방지
    
    # DataGenerator 내부 메서드 교체
    def get_tier_matchIds(
        self,
        queue: str,
        tier: str,
        division: str,
        max_ids: int,
        patch_start_datetime: str,
        min_game_duration: int,
        max_game_duration: int,
        max_workers: int = 8      # 동시 쓰레드 수 (API 제한 고려해 6~10 사이 권장)
    ):
        # 1) 티어/디비전 → PUUID 목록
        puuids = self.get_puuids(queue, tier, division)[:max_ids]

        # 2) 병렬 수집용 헬퍼
        def _fetch(puuid):
            try:
                ids = self.get_matchIds(
                    puuid,
                    patch_start_datetime,
                    min_game_duration,
                    max_game_duration
                )
                # 필요 시 아주 짧게 쉬어주면 (rate-limit 완화)
                # time.sleep(0.05)
                return ids
            except Exception:
                return []

        # 3) 병렬 실행 + 단일 tqdm
        match_ids = set()
        with ThreadPoolExecutor(max_workers=max_workers) as executor, \
            tqdm(total=len(puuids),
                desc=f'[{tier}-{division}] fetch matchIds',
                ncols=120, ascii=" =",
                leave=True) as pbar:

            futures = [executor.submit(_fetch, p) for p in puuids]

            for fut in as_completed(futures):
                match_ids.update(fut.result())
                pbar.update(1)   # 완료된 작업마다 1씩 진행

        return list(match_ids)
