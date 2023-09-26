"""Author: Mausam Rajbanshi (AI Engineer)"""
from datetime import datetime
import json
import os
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer

def init_dejavu(config_path):
    # initialize dejavu
    with open(config_path) as f:
        config = json.load(f)
    try:
        return Dejavu(config)
    except Exception as e:
        debug_error_log("ERROR: " + str(e))      # type:ignore


def adv_exists(djv, uploaded_filepath):
    results_check = djv.recognize(
        FileRecognizer, 
        uploaded_filepath
    )

    if results_check['results']:
        fingerprinted_confidence = results_check['results'][0]['fingerprinted_confidence']
        input_confidence = results_check['results'][0]['input_confidence']
        if fingerprinted_confidence > 0.8 and input_confidence > 0.9:
            advertisement_id = results_check['results'][0]['song_id']
            os.remove(uploaded_filepath)
            return True, advertisement_id
    return False, None


async def create_fingerprint(djv, uploaded_filepath):
    djv.fingerprint_file(uploaded_filepath)
    

def debug_error_log(text:str, timestamp:bool=True):
    with open("D:/Anaconda/Audio-FingerPrinting/FastAPI-Application/debug_error.log", 'a') as err_file:
        text = f"{datetime.now()} {text}" if timestamp else text
        print(text, file=err_file)
