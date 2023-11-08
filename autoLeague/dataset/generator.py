#APIKEY = 'RGAPI-1a1d24de-0002-4894-85cc-6deaf6ec560e'
import requests
import time
from tqdm import tqdm
from datetime import datetime

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
    def get_summonerIds(self, queue , tier , division): #queue : RANKED_SOLO_5x5 #tier : CHALLENGER(대문자) #division : I ~ IV
        page = 1             #페이지 초기값
        summoners = []       #소환사 명단
        while True:
            datas = requests.get(f'https://kr.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={page}&api_key={self.api_key}').json()
            if len(datas) == 0 or page > 30 :
                break
            page = page + 1
            for data in datas:
                summoners.append(data['summonerId'])

        
        return summoners
    
    #SUMMONERID -> PUUID
    def get_puuid(self, summonerId):
        try:
            puuid = requests.get(f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}?api_key={self.api_key}').json()["puuid"]
            return puuid
        except:
            return None
        
    #PUUID -> SUMMONERID
    def get_summonerId(puuid):
        try:
            summonerId = requests.get(f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={APIKEY}').json()['id']
            return summonerId
        except:
            return None
        
    # 최근 패치의 경기인지 감별(patch_start_millisec < game_creation_millisec)
    # patch_start_millisec 은 patch_start_datetime 을 millisec 으로 변환해서 얻음
    # patch_start_datetime 포맷 : 'YYYY.MM.DD' (예 : 2023.10.08)
    def is_in_recent_patch(self, game_creation_millisec, patch_start_datetime):
        
        dt_obj = datetime.strptime(patch_start_datetime,'%Y.%m.%d')
        patch_start_millisec = dt_obj.timestamp() * 1000

        return patch_start_millisec < game_creation_millisec
        
    #PUUID -> MATCHID(S)
    def get_matchIds(self, puuid, patch_start_datetime):
        if puuid == None:
            return []
        
        matchIdsOver15 = []
        matchIds = requests.get(f'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&type=ranked&start=0&count={self.count}&api_key={self.api_key}').json()    
        count = 0
        for matchId in matchIds:
            try:
                response = requests.get(f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchId}?api_key={self.api_key}")
                gameDuration = round(response.json()['info']['gameDuration'])
                gameCreation = round(response.json()['info']['gameCreation'])
                if (gameDuration >= 25*60) and (count < self.count) and self.is_in_recent_patch(self, gameCreation, patch_start_datetime):
                    matchIdsOver15.append(matchId)
                    count = count + 1
                else:
                    break
            except:
                pass
                
        return matchIdsOver15
    
    #get matchids { precondition : queue(=랭크 타입) , tier(=티어), division(=단계, 예:I,II,III,IV) , patch_start_datetime(=패치시작일, 예: '2023.10.08') }
    def get_tier_matchIds(self, queue, tier, division , max_ids, patch_start_datetime):
    
        # process : queue, tier, division -> summonerId(s)
        summonerIds = self.get_summonerIds(self, queue , tier , division)
        
        puuids = []
        matchIds = []

        # process : summonerId -> puuid
        for summonerId in tqdm(summonerIds[:max_ids] ,
                               desc = 'Gathering summoner_ids by Riot_API... ', ## 진행률 앞쪽 출력 문장
                               ncols = 120, ## 진행률 출력 폭 조절
                               ascii = ' =', 
                               leave=True
                               ):
            try:
                puuids.append(self.get_puuid(self,summonerId))
                time.sleep(0.01)
            except:
                pass
        
        # process : puuid -> matchId(s)
        for puuid in tqdm(puuids , 
                          desc = 'Gathering puuids by Riot_API from summoner_ids... ', ## 진행률 앞쪽 출력 문장
                          ncols = 120, ## 진행률 출력 폭 조절
                          ascii = ' =', 
                          leave=True
                          ):
            try:
                matchIds.extend(self.get_matchIds(self,puuid,patch_start_datetime))
                #print(len(matchIds),"개의 경기 누적")
                time.sleep(0.01)
            except:
                pass
        
        return matchIds
    
    