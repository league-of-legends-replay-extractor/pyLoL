import os
import shutil
import time
import json
import subprocess
import base64
import requests
import pyautogui
import pydirectinput
import cv2
import numpy as np
import re
from ftplib import FTP
import mss
import mss.tools
from threading import Thread

TEAM_HOTKEY_DICT = {'Red' : 'f2', 'Blue' : 'f1', 'All' : 'f'}


class ReplayScraper(object):
    """League of Legends replay scraper class.
    
    This class handles executing the League of Legends client in
    replay mode and the scraping application in the correct order.
    Args:
        game_dir: League of Legends game directory.
        replay_dir: League of Legends *.rofl replay directory.
        save_dir: JSON replay files output directory.
        replay_speed: League of Legends client replay speed multiplier.
        scraper_path: Directory of the scraper program.
    """
    def __init__(self,
            game_dir,
            replay_dir,
            save_dir,
            scraper_dir,
            replay_speed=8,
            region="KR",

            ftp_server='ftp_server_ip',
            ftp_username='ftp_username',
            ftp_password='ftp_password',
            local_folder_path=r'C:\dataset',
            remote_folder_path='/home/username'):
        
        self.game_dir = game_dir
        self.replay_dir = replay_dir
        self.save_dir = save_dir
        self.scraper_dir = scraper_dir
        self.replay_speed = replay_speed
        self.region = region

        self.ftp_server = ftp_server
        self.ftp_username = ftp_username
        self.ftp_password = ftp_password
        self.local_folder_path = local_folder_path #r'C:\dataset\KR-7025942524\All\1_292.38525390625.png'  # 로컬 파일 경로
        self.remote_folder_path = remote_folder_path # '/home/user/image.png'  # NAS 내 저장될 경로와 파일 이름
        
        files = os.listdir(self.replay_dir)
        replays = [file for file in files if file.endswith(".rofl")]
        print("현재 있는 리플레이 갯수 : ",len(replays))
    # 롤 실행 시
    def arg_list(self, replay_path):
        return [str(os.path.join(self.game_dir, "League of Legends.exe")),
                replay_path,
                "-SkipRads",
                "-SkipBuild",
                "-EnableLNP",
                "-UseNewX3D=1",
                "-UseNewX3DFramebuffers=1"]
    
    # lcu api 호출 성공인지 확인 용도
    def post_initialize(paused, start, speed):
        return requests.post(
                        'https://127.0.0.1:2999/replay/playback',
                        headers={
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        },
                        data = json.dumps({
                            "paused": paused,
                            "seeking" : False,   
                            "time": start - 5,
                            "speed": speed
                        }),
                        verify=False
                    )
    
    def replay_view_initialize():
        requests.post(
                        'https://127.0.0.1:2999/replay/render',
                        headers={
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        },
                        data = json.dumps({'banners': True,
                                            'cameraAttached': False,
                                            'cameraLookSpeed': 1.0,
                                            'cameraMode': 'fps',
                                            'cameraMoveSpeed': 10000.0,
                                            'cameraPosition': {'x': 10585.7119140625, 'y': 57447.296875, 'z': 850},
                                            'cameraRotation': {'x': 347.90582275390625, 'y': 85.0, 'z': 3.0},
                                            'characters': False,
                                            'depthFogColor': {'a': 1.0, 'b': 0.0, 'g': 0.0, 'r': 0.0},
                                            'depthFogEnabled': False,
                                            'depthFogEnd': 8000.0,
                                            'depthFogIntensity': 1.0,
                                            'depthFogStart': 5000.0,
                                            'depthOfFieldCircle': 10.0,
                                            'depthOfFieldDebug': False,
                                            'depthOfFieldEnabled': False,
                                            'depthOfFieldFar': 5000.0,
                                            'depthOfFieldMid': 2000.0,
                                            'depthOfFieldNear': 0.0,
                                            'depthOfFieldWidth': 800.0,
                                            'environment': False,
                                            'farClip': 66010.0,
                                            'fieldOfView': 19.0,
                                            'floatingText': False,
                                            'fogOfWar': False, # 여기 전장의 안개 옵션이 있는데?
                                            'healthBarChampions': False,
                                            'healthBarMinions': False,
                                            'healthBarPets': False,
                                            'healthBarStructures': True,
                                            'healthBarWards': False,
                                            'heightFogColor': {'a': 1.0, 'b': 0.0, 'g': 0.0, 'r': 0.0},
                                            'heightFogEnabled': False,
                                            'heightFogEnd': -100.0,
                                            'heightFogIntensity': 1.0,
                                            'heightFogStart': 300.0,
                                            'interfaceAll': True,
                                            'interfaceAnnounce': False,
                                            'interfaceChat': False,
                                            'interfaceFrames': True,
                                            'interfaceKillCallouts': False,
                                            'interfaceMinimap': True,
                                            'interfaceNeutralTimers': False,
                                            'interfaceQuests': None,
                                            'interfaceReplay': True,
                                            'interfaceScore': True,
                                            'interfaceScoreboard': True,
                                            'interfaceTarget': False,
                                            'interfaceTimeline': False, #
                                            'navGridOffset': 0.0,
                                            'nearClip': 50.0,
                                            'outlineHover': False,
                                            'outlineSelect': True,
                                            'particles': False,
                                            'selectionName': '',
                                            'selectionOffset': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                                            'skyboxOffset': 0.0,
                                            'skyboxPath': '',
                                            'skyboxRadius': 2500.0,
                                            'skyboxRotation': 0.0,
                                            'sunDirection': {'x': 0.31559720635414124,
                                            'y': -0.9467916488647461,
                                            'z': 0.06311944127082825}}),
                                            verify=False
                                            )

    

    """
    캡쳐한 화면을 이미지로 저장
    """
    def save_to_png(rgb, size, output):
        mss.tools.to_png(rgb, size, output=output)


    """
    게임 1경기에 대한 전체 스크린샷을 NAS 에 전송
    """
    def send_to_nas(ftp_server, ftp_username, ftp_password, local_folder_path, remote_folder_path, gameId, timestamplist):
    
        # FTP 서버 설정, FTP 세션 시작
        ftp = FTP(ftp_server)
        ftp.login(ftp_username, ftp_password)
        """
        파일 정렬
        """
        def list_all_files(base_dir):

            def extract_number(file_path):
                '''
                파일 이름에서 숫자를 추출하는 함수
                '''
                filename = file_path.split("\\")[-1]
                number = re.search(r'\d+', filename).group()
                return int(number)
        
            file_paths = []
            for dirpath, dirnames, filenames in os.walk(base_dir):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    file_paths.append(file_path)

            sorted_file_paths = sorted(file_paths, key=extract_number)
            return sorted_file_paths

        # 로컬 파일 불러오기
        all_files = list_all_files(local_folder_path)

        print('local file size : ', len(all_files))
        # 원격 폴더 생성
        ftp.mkd(f'{remote_folder_path}/{gameId}')
        # 원격 폴더로 로컬 파일 복사
        for idx, file in enumerate(all_files):
        # 파일을 바이너리 모드로 읽어서 전송
     
            with open(file, 'rb') as file:
                #ftp.storbinary(f"STOR {remote_folder_path}/{gameId}/{capture_count_list[idx]}_{timestamplist[idx]}.png", file)
                ftp.storbinary(f"STOR {remote_folder_path}/{gameId}/{timestamplist[idx]}.png", file)
        

        # 연결 종료
        ftp.quit()
        #print("파일 업로드 완료")

        # 로컬 폴더 삭제
        remain_folder_path = os.path.join(local_folder_path, os.listdir(local_folder_path)[0])
        """
        로컬의 폴더 삭제
        """
        def delete_folder(folder_path):
            # 폴더 존재 여부 확인
            if os.path.exists(folder_path):
                # 폴더와 모든 내용 삭제
                shutil.rmtree(folder_path)
                #print(f"The folder '{folder_path}' has been deleted successfully.")
            else:
                print("The folder does not exist.")
                
        delete_folder(remain_folder_path)

    def run_client_ver1(self, replay_path, gameId, start, end, speed, paused , team, remove_fog_of_war, use_nas=True):
        # argument setting
        args = self.arg_list(self, replay_path)
        # run League of Legends.exe
        
        subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=self.game_dir) 
        # 표준 출력과 표준 오류에서 한 줄씩 읽음

        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        parent_dir = self.save_dir
        path = os.path.join(parent_dir, gameId, str(start//60))  
        os.makedirs(path, exist_ok=True)
        """
        아래 10초를 대기하는 것은 리플레이 파일에서 특정 시간 시작에서 버퍼링이 걸리는 문제를 해결하기 위함. (파일을 충분히 로드할 때까지 기다림림)
        """
        time.sleep(3)         
        '''
        lcu_request_failed : post 요청 실패 여부.
        '''
        #리플레이 진영 시야 선택을 위한 단축키선택
        key = TEAM_HOTKEY_DICT[team]
        lcu_request_failed = True 

        # 리플레이 실행 호출 횟수 임계값, post 가 POST_COUNT_THRESH 이상이 되어도 리플레이 실행이 안되면 다음으로 넘어감
        POST_COUNT_THRESH = 3
        post_count = 0
        while lcu_request_failed:
            
            try:
                time.sleep(1)
                res = self.post_initialize(False, start, speed)
                
                if res.status_code == 200:
                    lcu_request_failed = False
            except:
                time.sleep(2)
                # 리플레이 실행 호출 횟수, 예외 날때마다 1 추가
                post_count = post_count + 1

                # 탈출 조건 : 이정도로 요청을 보냈는데도 리플레이 실행이 안되면, 다음 경기 리플레이 실행
                if post_count >= POST_COUNT_THRESH:
                    return None
                pass
       
        '''
        replay_running : 리플레이가 실행중인가에 대한 불린 ; 클라이언트가 end 시각까지만 실행하도록
        capture_count : 리플레이 하나 당 캡쳐하는 이미지 갯수 (또는 캡쳐중인 이미지의 현재 리플레이에서 인덱스)
        '''     
        self.replay_view_initialize()
        self.post_initialize(False, start, speed)
        replay_running = True 
        #Show Blue Team's Vision   ( RedTeam : f2 , All : f3)
        pydirectinput.press(key)
        pydirectinput.press('x')
        pydirectinput.press('f' if remove_fog_of_war else '')
        capture_count = 0  

        time.sleep(1)
        # 녹화 시작 시간을 기록합니다.
        start_time = time.time()

        # capture_count_list = []
        # timestamp_list = []

        # set replay interface_scoreboard => show curr_gold(total_gold)
        timegap_sec = end - start
        while replay_running :
            try:
                current_time = time.time()
                if (current_time - start_time) >= timegap_sec/speed:
                    replay_running  = False
             
                #capture_count_list.append(capture_count)

                with mss.mss() as sct:
                    # 기존 캡쳐 영역: 가운데 2160×1440
                    original_monitor = {"top": 0, "left": 1480, "width": 2160, "height": 1440}
                    # 기존 영역의 우측 하단 512×512 부분 계산:
                    sub_top = original_monitor["top"] + original_monitor["height"] - 512 - 23   # 0 + 1440 - 512 = 928
                    sub_left = original_monitor["left"] + original_monitor["width"] - 512 - 22   # 1480 + 2160 - 512 = 3128
                    monitor = {"top": sub_top, "left": sub_left, "width": 512, "height": 512}
                    
                    output = rf"{path}\{capture_count}.png"
                    sct_img = sct.grab(monitor)

                    thread = Thread(target=self.save_to_png, args=(sct_img.rgb, sct_img.size, output))
                    thread.start()
                    time.sleep(0.047)
                    
                capture_count = capture_count + 1

            except:
                pass

        ## 클라이언트 종료 ##              
        os.system("taskkill /f /im \"League of Legends.exe\"")    

        time.sleep(3)
        # NAS 사용시
        if use_nas:

            ftp_server = self.ftp_server
            ftp_username = self.ftp_username
            ftp_password=self.ftp_password
            local_folder_path = self.local_folder_path
            remote_folder_path = self.remote_folder_path
            #self.send_to_nas(ftp_server, ftp_username, ftp_password, local_folder_path, remote_folder_path, gameId, capture_count_list)
            #self.send_to_nas(ftp_server, ftp_username, ftp_password, local_folder_path, remote_folder_path, gameId, capture_count_list, timestamp_list)
           
        else:
            pass
        time.sleep(1)

        
    def get_replay_dir(self):
        return self.replay_dir
    
    def list_all_files(base_dir):

        def extract_number(file_path):
            '''
            파일 이름에서 숫자를 추출하는 함수
            '''
            filename = file_path.split("\\")[-1]
            number = re.search(r'\d+', filename).group()
            return int(number)
    
        file_paths = []
        for dirpath, dirnames, filenames in os.walk(base_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                file_paths.append(file_path)

        sorted_file_paths = sorted(file_paths, key=extract_number)
        return sorted_file_paths
    
    def delete_folder(folder_path):
        # 폴더 존재 여부 확인
        if os.path.exists(folder_path):
            # 폴더와 모든 내용 삭제
            shutil.rmtree(folder_path)
            print(f"The folder '{folder_path}' has been deleted successfully.")
        else:
            print("The folder does not exist.")