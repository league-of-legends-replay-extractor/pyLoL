import requests
import base64
import subprocess
import json

class ReplayDownlader(object):

    def __init__(self):
        self.replays_dir = None #리플레이 저장 디렉토리
        self.token = None       #롤 클라 인증 토큰
        self.port = None        #롤 클라 프로세스 포트넘버

        # 아직 Windows만 됨
        process =  subprocess.Popen("wmic PROCESS WHERE name='LeagueClientUx.exe' GET commandline", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, error = process.communicate()

        if error:
            raise ProcessLookupError("롤 클라이언트 안켜짐")
        else:
            cmd = output.strip().split('"')
            for i in cmd:
                if i.find("remoting-auth-token") != -1:
                    self.token = i.split("=")[1]
                elif i.find("app-port") != -1:
                    self.port = i.split("=")[1]

        print(self.token)
    '''리플레이 다운로드 위치 설정'''
    def set_replays_dir(self,folder_dir):
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        requests.patch(
                        f'https://127.0.0.1:{self.port}/lol-settings/v1/local/lol-replays',
                        headers={
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        },
                        data = json.dumps({
                            "replays-folder-path": folder_dir
                        }),
                        verify=False
                    )
        
        self.replays_dir = folder_dir


    '''리플레이 파일(gameId.rofl) 다운로드'''
    def download(self,gameId):
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        requests.post(
                        f'https://127.0.0.1:{self.port}/lol-replays/v1/rofls/{gameId.replace("KR_","")}/download/graceful',
                        headers={
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'Authorization': 'Basic ' + base64.b64encode(str('riot:'+self.token).encode('ascii')).decode('ascii')
                        },
                        data = json.dumps({
                                    'componentType': "string"
                                }),
                        
                        verify=False
                    )


            
