import os 
import re
### easyorc ###
import easyocr
import cv2
import numpy as np

class OcrCenter(object):

    def __init__(self, project_folder_dir):
        self.project_folder_dir = project_folder_dir

    def get_ocr(self):
        replay_folders = [folder for folder in os.listdir(self.project_folder_dir) if folder[:3] == 'KR-']
        print(replay_folders)
        def extract_number_from_filename(filename):
                """
                파일 이름에서 숫자를 추출하는 함수.
                """
                match = re.search(r'(\d+)_team_kda', filename)
                if match:
                    return int(match.group(1))
                return float('inf')  # 숫자가 없는 경우에는 맨 뒤로 정렬하기 위함

        def sort_filenames(filenames):
            """
            주어진 파일 이름 목록을 숫자 순서대로 정렬하는 함수.
            """
            return sorted(filenames, key=extract_number_from_filename)
        
        def read_file(full_path):
            img_array = np.fromfile(full_path, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
        
        def lane_filtering(info_list):
            
            # 제압골드 삭제
            for i in range(len(info_list)):
                try:
                    if info_list[i][-1] == "G":
                        info_list.remove(info_list[i])
                except:
                    pass

            filtered_team_info = {}
            user_form = [{"K/D/A" : [],"CS" : 0},{"K/D/A" : [],"CS" : 0},{"K/D/A" : [],"CS" : 0},{"K/D/A" : [],"CS" : 0},{"K/D/A" : [],"CS" : 0},{"K/D/A" : [],"CS" : 0},{"K/D/A" : [],"CS" : 0},{"K/D/A" : [],"CS" : 0},{"K/D/A" : [],"CS" : 0},{"K/D/A" : [],"CS" : 0}]
            #print(info_list)
            j = 0
            for i in range(len(info_list)):
            
                if len(info_list[i].split("/")) > 1:
                    user_form[j]['K/D/A'] = info_list[i].split("/")
                # CS 인 경우
                if len(info_list[i].split("/")) == 1:
                    user_form[j]['CS'] = int(info_list[i])
               
                # 다 채워지면 info 에 추가 및 user_form 초기화
                if  len(user_form[j]['K/D/A']) > 1 and user_form[j]['CS'] != 0:
                    #filtered_team_info[j] = user_form)
                    #print(filtered_team_info)
                    #user_form['제압골드'] = '0'
                    #user_form['K/D/A'] = []
                    #user_form['CS'] = 0
                    j += 1


            return user_form
                


        for replay_folder in replay_folders:
            # 전체 시야에서 캡쳐한 화면들을 보기 위해서 해당 ../All 폴더에 가보고자 함.
            replay_folder_allow_all_sight = rf'{self.project_folder_dir}\{replay_folder}\All'
            print(replay_folder_allow_all_sight)
            filenames = [file for file in os.listdir(replay_folder_allow_all_sight) if file[-12:] == 'team_kda.png']
            sorted_filenames = sort_filenames(filenames)
            print(filenames)
            for file in sorted_filenames:
                full_file_path = rf'{replay_folder_allow_all_sight}\{file}'
                reader = easyocr.Reader(['ko'], gpu=True)
                img = read_file(full_file_path)
                info_list = reader.readtext(img, detail=0, allowlist="0123456789/G")
                filtered_info = lane_filtering(info_list)
                print("해당 프레임에서 kda, cs \n", filtered_info)
                



    

    