# league-of-legends-replay-extractor

League of Legends Replay Extractor Using CV

A program for gathering positional data and providing analytics from League of Legends videos. It can be used to automatically gather spatiotemporal data (player locations over time) from a series of Youtube/locally stored videos

![image](https://github.com/kimsy1106/league-of-legends-replay-extractor/assets/53938323/c33b106a-63eb-4b2e-9fca-dd89e445c2c3)

# What is pyLoL?

pyLoL is 'League of Legends' replays data extracting program.

# What can pyLoL do?

[1] can save replay files(.rofl) automatically.

[2] can get the location of players every one second.

[3] can get the location of wards.

# Quickstart

Get started with W&B in four steps:

1. First, clone this repository.

```bash
git clone https://github.com/league-of-legends-replay-extractor
```

2. Install Requirements

```bash
pip install -r requirements.txt
```

3. Make python project to Package
   
```bash
python setup.py develop
```

4. Directory settings
   In replay_scraper.ipynb, modify the path to suit your local environment
   game_dir: League of Legends game directory.
   replay_dir: League of Legends *.rofl replay directory.
   dataset_dir: JSON replay files output directory.
   replay_speed: League of Legends client replay speed multiplier.
   scraper_dir: Directory of the scraper program.
   
```python
rd.set_replays_dir(rd,folder_dir = r'C:\Users\username\Documents\League of Legends\Replays')  # replay download directory

rs.__init__(rs, game_dir = r'C:\Riot Games\League of Legends\Game',                          
            replay_dir = r'C:\Users\username\Documents\League of Legends\Replays',               
            dataset_dir = r'C:\Users\username\Documents\League of Legends\Dataset',              
            scraper_dir = r'C:\Users\username\Desktop\pyLoL\pyLoL\autoLeague\replays',
            replay_speed=40,
            region="KR")
ie.__init__(ie,dataset_dir=r'C:\Users\username\Desktop\pyLoL')
```

5. API KEY
   You can get API KEY from riot developer portal : https://developer.riotgames.com
   
```python
dg.__init__(dg, api_key='RIOT_API_KEY' , count=20)
```

6. Gathering MatchIds filtered by {queue, tier, division, max_ids, patch_start_datetime}

   if you wanna download matchIds from 5000 MASTER I in SOLORANK users in specific patch,
   
```python
dg.get_tier_matchIds(dg, queue='RANKED_SOLO_5x5', tier='MASTER', division='I' , max_ids=5000, patch_start_datetime='2023.10.26')
```

7. 

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

