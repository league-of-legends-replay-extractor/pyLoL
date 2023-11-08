# league-of-legends-replay-extractor

League of Legends Replay Extractor Using CV

A program for gathering positional data and providing analytics from League of Legends videos. It can be used to automatically gather spatiotemporal data (player locations over time) from a series of Youtube/locally stored videos

![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/c33b106a-63eb-4b2e-9fca-dd89e445c2c3)


## warning 

  if you want to see replay file, the ver. of replay file must be "equal" to the ver. of client (!)

## software settings

  
  1. create venv
    conda create -n lolpago python=3.9.11
    
  2. start venv
    conda activate lolpago

  3. install tensorflow 
    pip install tensorflow-gpu=2.10.0

  4. software requirements
    cuDNN = v8.1.0 for CUDA 11.2  :  https://developer.nvidia.com/rdp/cudnn-download   => lib, include, bin 폴더만 따로 CUDA(C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2) 에 저장.

    CUDA = 11.2  :  https://developer.nvidia.com/cuda-11.2.0-download-archive

    tensorflow  :  2.10.0

  5. set game config file
    C:\Riot Games\League of Legends\Game\DATA\cfg\game.cfg => EnableReplayApi=1

    C:\Riot Games\League of Legends\Game\DATA\cfg\PersistedSettings.json => "name": "MinimapScale", "value": "5.0000"
    
    PersistedSettings.json 에서 편집해도 됨.

## <command>
  setup.py develop


For more information, see the wiki

#### 1. Download or clone the repo

Download directly from github and unzip or clone from the command line

#### 2. Install Requirements

    pip install -r requirements.txt

#### 3. How to Use

  - Collecting Player MatchIDs  :
    
        python3 generator.py
    ![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/9ea856bb-c76c-4a85-b720-578ea1ef2748)

  - Replay File(.rofl) Download :

        python3 downloader.py
    ![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/25af0427-a308-431f-90af-730881d00a3c)

  - Replay Running & Recording  :

        python3 scraper.py
    ![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/1afbd285-ab26-4095-81a1-5513c78cac2b)

#### 4. Get Minimap Capture Images

![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/83d01e33-0c15-4e59-a83c-1d42991a0ca5)



#### 5. You can make them( Using Minimap Frame dataset )

- Champion Tracking (Roboflow)
![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/0c678dbf-82e7-4219-9f77-3faf3a58b358)


Then, You can use this tracking model ( Performance | mAP : 92.2% | precision : 91.3% | recall : 90.2% )
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


