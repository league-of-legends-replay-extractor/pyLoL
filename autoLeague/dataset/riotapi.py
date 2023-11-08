#APIKEY = 'RGAPI-1a1d24de-0002-4894-85cc-6deaf6ec560e'
import requests
import time
from tqdm import tqdm
import csv
import numpy as np

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


        f = open(rf'C:\Users\김성윤\Desktop\pyLoL\riot_api_dataset.csv','a', newline='')
        wr = csv.writer(f)
        wr.writerow(features)
        
        for matchId in tqdm(matchIds):
            row = self.getMatchData(self,matchId)
            
            wr.writerow(row)

        f.close()

        print('csv write complete')
