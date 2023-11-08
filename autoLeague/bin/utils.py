import subprocess
import base64
import requests

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class Utils(object):
  
    def __init__(self):
        pass
 
    def get_replay_dir(self):
        # 아직 Windows만 됨
        process =  subprocess.Popen("wmic PROCESS WHERE name='LeagueClientUx.exe' GET commandline", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        token = None
        port = None

        output, error = process.communicate()

        if error:
            raise ProcessLookupError("롤 클라이언트 안켜짐")
        else:
            cmd = output.strip().split('"')
            for i in cmd:
                if i.find("remoting-auth-token") != -1:
                    token = i.split("=")[1]
                elif i.find("app-port") != -1:
                    port = i.split("=")[1]

        r = requests.get(url='https://127.0.0.1:' + port + f'/lol-replays/v1/rofls/path',
        headers={ 'accept': 'application/json', 'Authorization': 'Basic ' + base64.b64encode(str('riot:'+token).encode('ascii')).decode('ascii') }, verify = False)

        return r.json().replace("\\", "/")