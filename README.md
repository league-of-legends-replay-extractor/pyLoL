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
   In replay_scraper.ipynb, ㅡodify the path to suit your local environment
   


#### 1. Download or clone the repo

Download directly from github and unzip or clone from the command line

#### 2. Install Requirements

    pip install -r requirements.txt


# Quickstart

Get started with W&B in four steps:

1. First, sign up for a [free W&B account](https://wandb.ai/login?utm_source=github&utm_medium=code&utm_campaign=wandb&utm_content=quickstart).

2. Second, install the W&B SDK with [pip](https://pip.pypa.io/en/stable/). Navigate to your terminal and type the following command:

```bash
pip install wandb
```

3. Third, log into W&B:

```python
wandb.login()
```

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

