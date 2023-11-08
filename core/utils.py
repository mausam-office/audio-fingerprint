"""Author: Mausam Rajbanshi (AI Engineer)"""
from datetime import datetime
import json
import os
import re
import string
import subprocess
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
    try:
        results_check = djv.recognize(
            FileRecognizer, 
            uploaded_filepath
        )
    except Exception as e:
        debug_error_log(str(e))
        return False, None, None

    if results_check['results']:
        fingerprinted_confidence = results_check['results'][0]['fingerprinted_confidence']
        input_confidence = results_check['results'][0]['input_confidence']
        if fingerprinted_confidence > 0.8 and input_confidence > 0.9:
            advertisement_id = results_check['results'][0]['song_id']
            advertisement_name = str(results_check['results'][0]['song_name'], encoding='utf-8')
            os.remove(uploaded_filepath)
            return True, advertisement_id, advertisement_name
    return False, None, None


async def create_fingerprint(djv, uploaded_filepath):
    djv.fingerprint_file(uploaded_filepath)
    

def debug_error_log(text:str, timestamp:bool=True):
    # with open("D:/Anaconda/Audio-FingerPrinting/FastAPI-Application/debug_error.log", 'a') as err_file:
    with open("C:/python-apps/Advertisement-APP/audio-fingerprint/debug_error.log", 'a') as err_file:
        text = f"{datetime.now()} {text}" if timestamp else text
        print(text, file=err_file)


def get_bitrate(response, ROOT_TEMP_DIR):
    os.makedirs(ROOT_TEMP_DIR, exist_ok=True)
    filepath = os.path.join(ROOT_TEMP_DIR, 'audio_rec.wav')
    output_filepath = os.path.join(ROOT_TEMP_DIR, 'audio_rec_output.wav')
    iterations = 16000
    clip_duration = 3

    with open(filepath, 'wb') as rec_file:
        for idx, chunk in enumerate(response.iter_content(chunk_size=1)):
            if chunk:
                rec_file.write(chunk)
                
            if idx>=iterations*clip_duration:
                break
    cmd = ['powershell', f"""ffmpeg -i '{filepath}' '{output_filepath}' -y"""]
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )

    # Read the outputs line by line
    pattern = r'bitrate: (\d+) kb/s'
    bitrate = 0
    while True:
        output_line = process.stdout.readline()
        error_line = process.stderr.readline()
        
        if output_line == '' and error_line == '' and process.poll() is not None:
            break
        
        # if output_line:
        #     print(f"ffmpeg output: {output_line.strip()}")
        
        if error_line: 
            line = error_line.strip()
            if all([val in line for val in ['bitrate', 'Duration']]):
                # print(f"ffmpeg error: {line}")
                # val = line.split(':')[-1][:-4].strip()
                # print(f"{int(val) = }")

                match = re.search(pattern, line)
                bitrate = int(match.group(1)) if match else 0
            
    return bitrate

def remove_quatation_marks(original_str:str):
    '''removes quatation marks''' 
    modified_str = original_str.translate(str.maketrans('', '', '"'))   # removes all quotation marks
    return modified_str
