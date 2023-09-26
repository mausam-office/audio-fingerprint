# import ast
import json
import os
import http
import shutil
import uvicorn

from core.utils import adv_exists, init_dejavu, create_fingerprint, debug_error_log
from core.db import get_advertisement_id
from decouple import config
from fastapi import FastAPI, UploadFile, File


app = FastAPI(title="Audio-API")


ROOT_UPLOAD_DIR = config('ROOT_UPLOAD_DIR')
BACKUP_DIR = config('BACKUP_DIR')
FILE_EXTENSION = config('FILE_EXTENSION')
CONFIG_DIR = config('CONFIG_DIR')
CONFIG_PATH = config('CONFIG_PATH')


@app.get("/")
def root():
    return {'message':'FastAPI app'}


@app.post("/upload")
async def upload(
    name: str, # = Query(..., description="Name of the file"),
    file:UploadFile = File(...)
    ):

    advertisement_id = None

    filename = file.filename
    # print(f"{filename = }")
    file_ext = filename.split('.').pop()
    if file_ext != 'wav':
        debug_error_log(f"File with `{file_ext}` extension provided instead of `.wav`.")
        return {
            "success"   : False, 
            "status"    : http.HTTPStatus.NOT_ACCEPTABLE, 
            'message'   : 'File with `.wav` extension is only accepted.'
        }

    filename = name if name.endswith('.wav') else name + '.wav'
    uploaded_filepath = f"{ROOT_UPLOAD_DIR}/{filename}"
    
    debug_error_log(f"Request with file {filename}")
    advertisement_name = filename[:-4]
    advertisement_id = get_advertisement_id(advertisement_name)

    with open(uploaded_filepath, 'wb') as f:
        content = await file.read()
        f.write(content)
    
    djv = init_dejavu(CONFIG_PATH)
    adv_sts = adv_exists(djv, uploaded_filepath)

    if adv_sts or advertisement_id:
        print(f"Advertisemet `{advertisement_name}`  already exists.")
        return {
            "success"   : False, 
            "status"    : http.HTTPStatus.NOT_ACCEPTABLE,
            'message'   : 'Advertisemet already exists'
        }
    
    await create_fingerprint(djv, uploaded_filepath)

    # grab the song/advertisement id 
    # print(f"2. {advertisement_name = }")
    advertisement_id = get_advertisement_id(advertisement_name)

    try:
        shutil.move(uploaded_filepath, BACKUP_DIR)
    except shutil.Error as error:
        os.remove(uploaded_filepath)
    return {
        "success"   : True,
        "status"    : http.HTTPStatus.CREATED,
        "message"   : "Advertisement Created",
        "advertisement_id" : advertisement_id
    }


def read_conf():
    conf = {}
    conf["database"] = {}
    conf["database"]["host"] = config('HOST')
    conf["database"]["user"] = config('USER')
    conf["database"]["password"] = config('PASSWORD')
    conf["database"]["database"] = config('DATABASE')
    conf["database_type"] = config('DATABASE_TYPE')

    # conf file works for double quotation only as dictionary uses single quotation
    conf = json.dumps(conf)

    with open("D:/Anaconda/Audio-FingerPrinting/FastAPI-Application/venv/Scripts/configs/dejavu.cnf.SAMPLE", 'w') as dejavu_conf_file:
        dejavu_conf_file.write(conf)

def create_dirs():
    for dir in [ROOT_UPLOAD_DIR, BACKUP_DIR, CONFIG_DIR]:
        if not os.path.exists(dir):
            os.makedirs(dir)

if __name__ == "__main__":
    create_dirs()
    read_conf()
    
    uvicorn.run("main:app", host="0.0.0.0", port=2470, log_level="info", reload=False)