# 리그오브레전드 리플레이 추출/추적기

CV를 이용한 '리그 오브 레전드' 리플레이 추출기

리그 오브 레전드 리플레이 영상에서 데이터를 수집 / 분석하는 프로그램이다.
YouTube나 로컬에 저장된 비디오에서 시간에 따른 플레이어 위치 정보를 자동으로 수집할 수 있다.

![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/c33b106a-63eb-4b2e-9fca-dd89e445c2c3)


## 경고

  리플레이 영상을 보고 싶다면 리플레이 파일의 버전이 클라이언트의 버전과 동일해야 한다(!)

## 환경설정

  
  1. venv 생성
     
    conda create -n lolpago python=3.9.11
    
  3. venv 실행
     
    conda activate lolpago

  4. tensorflow 설치
     
    pip install tensorflow-gpu=2.10.0

  5. 소프트웨어 요구사항
     
    cuDNN = v8.1.0 for CUDA 11.2  :  https://developer.nvidia.com/rdp/cudnn-download   => save only {lib, include, bin} folders into CUDA(C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2)

    CUDA = 11.2  :  https://developer.nvidia.com/cuda-11.2.0-download-archive

    tensorflow  :  2.10.0

  5. 게임 config file 설정
    C:\Riot Games\League of Legends\Game\DATA\cfg\game.cfg => EnableReplayApi=1

    C:\Riot Games\League of Legends\Ga고

#### 1. 레포 다운로드 or 클론

깃헙으로부터 직접 다운받은 후 압축을 푼다.
혹은 명령창을 이용하여 clone해도 된다.

Download directly from github and unzip or clone from the command line

#### 2. 필요한 파일들 설치

    pip install -r requirements.txt

#### 3. 사용 방법

  - 소환사의 MatchIDs 수집 :
    
        python3 generator.py
    ![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/9ea856bb-c76c-4a85-b720-578ea1ef2748)

  - 리플레이 파일(.rofl) 다운로드드 :

        python3 downloader.py
    ![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/25af0427-a308-431f-90af-730881d00a3c)

  - 리플레이 재생 & 녹화  :

        python3 scraper.py
    ![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/1afbd285-ab26-4095-81a1-5513c78cac2b)

#### 4. 미니맵 캡처 이미지

![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/83d01e33-0c15-4e59-a83c-1d42991a0ca5)



#### 5. 아래와 같이 만들 수 있다( 미니맵 Frame dataset을 이 )

- 챔피언 추적 (Roboflow)
![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/0c678dbf-82e7-4219-9f77-3faf3a58b358)


추적 모델을 사용할 수 있다. ( Performance | mAP : 92.2% | precision : 91.3% | recall : 90.2% )
- Infer on Local and Hosted Images
    To install dependencies,

        pip install roboflow.

    Then, add the following the following code snippet to a Python script:
  
        from roboflow import Roboflow
        rf = Roboflow(api_key="API_KEY")
        project = rf.workspace().project("lolpago-multi-tracking-service")
        model = project.version(18).model
        
        # infer on a local image
        print(model.predict("your_image.jpg", confidence=40, overlap=30).json())
        
        # visualize your prediction
        # model.predict("your_image.jpg", confidence=40, overlap=30).save("prediction.jpg")
        
        # infer on an image hosted elsewhere
        # print(model.predict("URL_OF_YOUR_IMAGE", hosted=True, confidence=40, overlap=30).json())


