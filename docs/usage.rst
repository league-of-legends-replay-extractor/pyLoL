Usage
=====

.. _installation:

🚀Quickstart
------------
* Youtube Guide
|ImageLink1|_

.. |ImageLink1| image:: http://img.youtube.com/vi/0z9_jyfS1TQ/0.jpg
.. _ImageLink1: https://youtu.be/0z9_jyfS1TQ

Get started with pyLoL in nine steps:

|ImageLink2|_

.. |ImageLink2| image:: https://colab.research.google.com/assets/colab-badge.svg 
.. _ImageLink2: https://colab.research.google.com/drive/1HAQjHIVXE__Pb1KiBHG1I2jIQbFfWJ3q?usp=sharing

1. First, clone this repository.

.. code-block:: bash

   $ git clone https://github.com/league-of-legends-replay-extractor

2. Install Requirements.

.. code-block:: bash

   $ pip install -r requirements.txt

3. Make python project to Package.

.. code-block:: bash

   $ python setup.py develop

4. Directory settings

   In replay_scraper.ipynb, modify the path to suit your local environment

   * game_dir: League of Legends game directory.
   
   * replay_dir: League of Legends *.rofl replay directory.
   
   * dataset_dir: JSON replay files output directory.
   
   * replay_speed: League of Legends client replay speed multiplier.
   
   * scraper_dir: Directory of the scraper program.

.. code-block:: python

   rd.set_replays_dir(rd,folder_dir = r'C:\Users\username\Documents\League of Legends\Replays')  # replay download directory
   rs.__init__(rs, game_dir = r'C:\Riot Games\League of Legends\Game',                          
               replay_dir = r'C:\Users\username\Documents\League of Legends\Replays',               
               dataset_dir = r'C:\Users\username\Documents\League of Legends\Dataset',              
               scraper_dir = r'C:\Users\username\Desktop\pyLoL\pyLoL\autoLeague\replays',
               replay_speed=40,
               region="KR")
   ie.__init__(ie,dataset_dir=r'C:\Users\username\Desktop\pyLoL')

5. API KEY
You can get API KEY from riot developer portal : `<https://developer.riotgames.com/>`_

.. code-block:: python

   dg.__init__(dg, api_key='RIOT_API_KEY' , count=20)

6. Gathering MatchIds filtered by {queue, tier, division, max_ids, patch_start_datetime}

   if you wanna download matchIds from 5000 MASTER I in SOLORANK users in specific patch,

.. code-block:: python

   dg.get_tier_matchIds(dg, queue='RANKED_SOLO_5x5', tier='MASTER', division='I' , max_ids=5000, patch_start_datetime='2023.10.26')

.. image:: https://github.com/league-of-legends-replay-extractor/pyLoL/raw/main/assets/extracting_kda.png

7. Save replay files for the match IDs obtained above

.. code-block:: python

   from tqdm import tqdm
   import time
   for matchId in tqdm(matchIds_challenger[:1000], 
                    desc = 'Gathering Replay_files(.rofl) from LoL Client... ', ## Print statement for progress at the front
                    ncols = 130, ## Adjust width for progress display
                    ascii = ' =', 
                    leave=True):
    
    try: #if this match id outdated, skip
        rd.download(rd, matchId)
        time.sleep(7)
    except:
        pass

.. image:: https://github.com/league-of-legends-replay-extractor/pyLoL/raw/main/assets/gathering_replay_files.png

8. Run replay => Save minimap capture video

* Option
   * All: no fog of war
   * Blue: fog of war in Blue team
   * Red: fog of war in Red team

.. code-block:: python

   for replay in tqdm(replays,
                    desc = 'Extracting Replay_Minimaps from LoL Client... ', ## Print statement for progress at the front
                    ncols = 200, ## Adjust width for progress display
                    ascii = ' =', 
                    leave=True
                    ):
    
    rs.run_client(rs,
                  replay_path = rf'{rs.get_replay_dir(rs)}\{replay}', 
                  gameId = replay.split('.')[0],
                  start=5*60 - 5, 
                  end=25*60 - 5, 
                  speed=10, 
                  paused=False, 
                  team="All")

.. image:: https://github.com/league-of-legends-replay-extractor/pyLoL/raw/main/assets/extracting_replay_minimaps.png

9. Extract Realtime KDA, CS using OCR

.. code-block:: python

   from autoLeague.preprocess.ocr_center_window import OcrCenter as oc
   oc.__init__(oc, project_folder_dir = r'C:\Users\username\Desktop\pyLoL')
   oc.get_ocr(oc)

.. image:: https://github.com/league-of-legends-replay-extractor/pyLoL/raw/main/assets/extracting_kda.png
