# pyLoL
python module for "League of Legends" dataset settings 

## warning 

  if you want to see replay file, the ver. of replay file must be "equal" to the ver. of client (!)

## software settings

  

  so
  1. 가상환경 생성
    conda create -n lolpago python=3.9.11
    
  2. 가상환경 시작
    conda activate lolpago

  3. tensorflow 설치
    pip install tensorflow-gpu=2.10.0

  4. 아래 설정
    cuDNN = v8.1.0 for CUDA 11.2  :  https://developer.nvidia.com/rdp/cudnn-download   => lib, include, bin 폴더만 따로 CUDA(C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2) 에 저장.

    CUDA = 11.2  :  https://developer.nvidia.com/cuda-11.2.0-download-archive

    tensorflow  :  2.10.0

  5. 롤 세팅
    C:\Riot Games\League of Legends\Game\DATA\cfg\game.cfg => EnableReplayApi=1

    C:\Riot Games\League of Legends\Game\DATA\cfg\PersistedSettings.json => "name": "MinimapScale", "value": "5.0000"
    
    PersistedSettings.json 에서 편집해도 됨.

## <command>
  setup.py develop
