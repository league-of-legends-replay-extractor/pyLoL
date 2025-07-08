import requests
import base64
import subprocess
import json
import asyncio, aiohttp, ssl

class ReplayDownlader(object):

    def __init__(self):
        self.replays_dir = None #리플레이 저장 디렉토리
        self.token = None       #롤 클라 인증 토큰
        self.port = None        #롤 클라 프로세스 포트넘버

        # 아직 Windows만 됨
        # wmic PROCESS WHERE name='LeagueClientUx.exe' GET commandline
        # PowerShell 명령어 리스트 구성
        command = [
            "powershell",
            "-Command",
            "Get-WmiObject -Query \"Select CommandLine from Win32_Process Where Name='LeagueClientUx.exe'\""
        ]
        process =  subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, error = process.communicate()

        if error:
            raise ProcessLookupError("⚠️ 롤 클라이언트가 실행 중인지 확인하세요.")
        else:
            cmd = output.strip().split('"')
            for i in cmd:
                if i.find("remoting-auth-token") != -1:
                    self.token = i.split("=")[1]
                elif i.find("app-port") != -1:
                    self.port = i.split("=")[1]

        print('remoting-auth-token :', self.token)
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
        
    # ────────────────────────────────────
    # 비동기(병렬) API
    # ────────────────────────────────────
    async def _download_one(self, session: aiohttp.ClientSession, game_id: str):
        """내부용 · 단일 POST"""
        url = (f"https://127.0.0.1:{self.port}"
               f"/lol-replays/v1/rofls/{game_id.replace('KR_','')}/download/graceful")
        async with session.post(url, json={"componentType": "string"}) as resp:
            if resp.status not in (200, 202, 204):
                err = await resp.text()
                print(f"[{game_id}] 실패 {resp.status}: {err}")

    async def download_async(self, game_ids, concurrent: int = 6):
        """
        여러 matchId iterable을 병렬로 다운로드.
        • Jupyter 셀  :   await rd.download_async(ids)
        • 스크립트   :   asyncio.run(rd.download_async(ids))
        """
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        auth = "Basic " + base64.b64encode(f"riot:{self.token}".encode()).decode()
        conn = aiohttp.TCPConnector(limit=concurrent, ssl=ssl_ctx)
        async with aiohttp.ClientSession(
            connector=conn,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": auth,
            }) as session:

            sem = asyncio.Semaphore(concurrent)

            async def sem_task(gid):
                async with sem:
                    await self._download_one(session, gid)

            await asyncio.gather(*(sem_task(g) for g in game_ids))


# 모듈 import 시 자동 인스턴스
replay_downloader = ReplayDownlader()
# ─────────────────────────────────────────────────────────────
