# transform preprocessed image folder to csv type dataset 
import os
import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm
import csv
import requests


blue_jug_near_baron = [(370,400),(200,300),(135,165),(100,200),(100,550),(150,550),(200,575),(370,400)]#### ?

blue_jug_near_drake = [(840-415,830-365),(840-350,830-325),(840-300,830-200),(840-210,830-210),(840-200,830-110),(840-230,830-100),(840-550,830-100),(840-550,830-150),(840-575,830-200),(840-415,830-365)] #### ^^

red_jug_near_baron = [(415,365),(350,325),(300,200),(210,210),(200,110),(230,100),(550,100),(550,150),(575,200),(415,365)] #### %

red_jug_near_drake = [(840-370,830-400),(840-200,830-300),(840-135,830-165),(840-100,830-200),(840-100,830-550),(840-150,830-550),(840-200,830-575),(840-370,830-400)]

#[(840-415,830-365),(840-350,830-325),(840-300,830-200),(840-210,830-210),(840-200,830-110),(840-230,830-100),(840-550,830-100),(840-550,830-150),(840-575,830-200),(840-415,830-365)]

river_near_baron = [(370,400),(200,300),(135,165),(200,110),(210,210),(300,200),(350,325),(415,365),(370,400)] ####

river_near_drake = [(840-370,830-400),(840-200,830-300),(840-135,830-165),(840-200,830-110),(840-210,830-210),(840-300,830-200),(840-350,830-325),(840-415,830-365),(840-370,830-400)] ####!

API_KEY = 'RGAPI-1a1d24de-0002-4894-85cc-6deaf6ec560e'

class DataPreprocessor(object):

    def __init__(self , project_folder_dir , tier):
        self.project_folder_dir = project_folder_dir, 
        self.tier = tier


    def get_triangle_roi(image, points):
        mask = np.zeros_like(image)
        cv2.fillPoly(mask, [points], (255, 255, 255))
        roi = cv2.bitwise_and(image, mask)
        return roi

    def calculate_pixel_sum(image_gray):
        pixel_sum = np.sum(image_gray)
        return pixel_sum//255

    def get_is_win(matchid, team_color):
        
        
        matchID = matchid.replace('-','_')
        if team_color == 'Blue':
            return 1 if requests.get(f'https://asia.api.riotgames.com/lol/match/v5/matches/{matchID}?api_key={API_KEY}').json()['info']['teams'][0]['win'] == True else 0
        else: 
            return 1 if requests.get(f'https://asia.api.riotgames.com/lol/match/v5/matches/{matchID}?api_key={API_KEY}').json()['info']['teams'][1]['win'] == True else 0
    

    # 이미지 파일 읽기

    def get_each_Vision_Area(self, image_dir):    #image_dir 예시 : r'C:\dataset\CHALLENGER\KR-6415928037\Blue\black\105.png'
        
        #image = cv2.imread(r'C:\dataset\CHALLENGER\KR-6415928037\Blue\black\105.png')
        image = cv2.imread(image_dir)

        triangle_BJ_B = self.get_triangle_roi(image, np.array(blue_jug_near_baron))
        area_BJ_B = self.calculate_pixel_sum(triangle_BJ_B)
        #print("블루팀 블루근처 시야면적:", area_BJ_B)

        triangle_BJ_D = self.get_triangle_roi(image, np.array(blue_jug_near_drake))
        area_BJ_D = self.calculate_pixel_sum(triangle_BJ_D)
        #print("블루팀 레드근처 시야면적:", area_BJ_D)

        triangle_RJ_B = self.get_triangle_roi(image, np.array(red_jug_near_baron))
        area_RJ_B = self.calculate_pixel_sum(triangle_RJ_B)
        #print("레드팀 레드근처 시야면적:", area_RJ_B)

        triangle_RJ_D = self.get_triangle_roi(image, np.array(red_jug_near_drake))
        area_RJ_D = self.calculate_pixel_sum(triangle_RJ_D)
        #print("레드팀 블루근처 시야면적:", area_RJ_D)

        triangle_BARON_RIVER = self.get_triangle_roi(image, np.array(river_near_baron))
        area_BARON_RIVER = self.calculate_pixel_sum(triangle_BARON_RIVER)
        #print("바론 강가 시야면적:", area_BARON_RIVER)

        triangle_DRAKE_RIVER = self.get_triangle_roi(image, np.array(river_near_drake))
        area_DRAKE_RIVER = self.calculate_pixel_sum(triangle_DRAKE_RIVER)
        #print("용 강가 시야면적:", area_DRAKE_RIVER)

        return [area_BJ_B, area_BJ_D, area_RJ_B, area_RJ_D, area_BARON_RIVER, area_DRAKE_RIVER]

    # 해당 티어에 있는 경기들의 면적 정보들을 csv 파일로 정리. 
    def get_each_Vision_Area_Per_Tier(self, project_folder_dir, tier):

        # EXAMPLE ##########################################
        # project_folder_dir : C:\Users\김성윤\Desktop\pyLoL 때로는 C:\dataset
        # tier : CHALLENGER
        #################################################### 
        INITIAL = 0
        match_folders = os.listdir(f'{project_folder_dir}\{tier}')
        project_folder_dir = f'{project_folder_dir}\{tier}'

        # 각 경기 폴더들 => 예시 : C:\Users\김성윤\Desktop\pyLoL\CHALLENGER\KR-6415928037

        f = open(rf'C:\dataset\{tier}_dataset.csv','a', newline='')
        features = ['matchID']
        for i in range(379):
            features.extend([f'블루바론{i}',f'블루용{i}',f'레드바론{i}',f'레드용{i}',f'바론{i}',f'용{i}'])

        features.append('is_win')

        print(len(features))

        wr = csv.writer(f)
        wr.writerow(features)
        f.close()
        for m_folder in tqdm(match_folders):

            # 레드, 블루
            team_folders = os.listdir(f'{project_folder_dir}\{m_folder}')

            #os.remove(rf'{folder_dir}\{m_folder}\{t_folder}\black\{removed_index}.png')

            i = INITIAL
            
            for t_folder in team_folders:
                
                data = [f'{m_folder}_{t_folder}']

                #csv file write
                f = open(rf'C:\dataset\{tier}_dataset.csv','a', newline='')
                wr = csv.writer(f)

                files = os.listdir(f'{project_folder_dir}\{m_folder}\{t_folder}\\black')
                for file in files:
                    data.extend(self.get_each_Vision_Area(rf'{project_folder_dir}\{m_folder}\{t_folder}\\black\{file}'))

                data.extend(str(self.get_is_win(m_folder, t_folder)))
                wr.writerow(data)
                f.close()
                
                #os.remove(rf'{folder_dir}\{m_folder}\{t_folder}\black\{removed_index}.png')

        print('Done!')

