"""Author: Mausam Rajbanshi (AI Engineer)"""
import json
import os
import http
import uvicorn

from core.utils import adv_exists, init_dejavu, create_fingerprint, debug_error_log
from core.db import get_advertisement_id
from decouple import config
from fastapi import FastAPI, UploadFile, File


app = FastAPI(title="Audio-API")


ROOT_UPLOAD_DIR = config('ROOT_UPLOAD_DIR')
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

    try:
        assert os.path.exists(ROOT_UPLOAD_DIR)
        assert os.path.exists(CONFIG_PATH)
    except Exception as e:
        debug_error_log("ERROR: " + "Assersion Error")      # type:ignore
        create_dirs()
        read_conf()

    filename = file.filename
    file_ext = filename.split('.').pop()    # type:ignore
    if file_ext != 'wav':
        debug_error_log(f"INFO: File with `{file_ext}` extension provided instead of `.wav`.")
        return {
            "success"   : False, 
            "status"    : http.HTTPStatus.NOT_ACCEPTABLE, 
            'message'   : 'File with `.wav` extension is only accepted.'
        }

    filename = name if name.endswith('.wav') else name + '.wav'

    os.makedirs(ROOT_UPLOAD_DIR, exist_ok=True)     # type:ignore
    uploaded_filepath = f"{ROOT_UPLOAD_DIR}/{filename}"
    
    debug_error_log(f"INFO: Request with file {filename}")
    advertisement_name = filename[:-4]

    try:
        with open(uploaded_filepath, 'wb') as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        debug_error_log("ERROR: " + str(e))      # type:ignore

    djv = init_dejavu(CONFIG_PATH)
    adv_sts, stored_advert_id = adv_exists(djv, uploaded_filepath)

    if adv_sts:
        debug_error_log(f"INFO: Advertisement `{advertisement_name}`  already exists.")
        return {
            "success"   : False, 
            "status"    : http.HTTPStatus.NOT_ACCEPTABLE,
            'message'   : 'Advertisemet already exists',
            "advertisement_id" : stored_advert_id
        }
    
    await create_fingerprint(djv, uploaded_filepath)

    # grab the song/advertisement id 
    new_advert_id = get_advertisement_id(advertisement_name)

    # # File is already stored in table. 
    # # Not necessary to store in disk. Just remove
    try:
        os.remove(uploaded_filepath)
    except Exception as e:
        debug_error_log("ERROR: " + str(e))      # type:ignore

    return {
        "success"   : True,
        "status"    : http.HTTPStatus.CREATED,
        "message"   : "Advertisement Created",
        "advertisement_id" : new_advert_id
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
    try: 
        with open("D:/Anaconda/Audio-FingerPrinting/FastAPI-Application/venv/Scripts/configs/dejavu.cnf.SAMPLE", 'w') as dejavu_conf_file:
            dejavu_conf_file.write(conf)
    except Exception as e:
        debug_error_log("ERROR: " + e)      # type:ignore


def create_dirs():
    for dir in [ROOT_UPLOAD_DIR, CONFIG_DIR]:
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)    # type:ignore
        except Exception as e:
            debug_error_log("ERROR: " + e)      # type:ignore


if __name__ == "__main__":
    create_dirs()
    read_conf()
    
    uvicorn.run("main:app", host="0.0.0.0", port=2470, log_level="info", reload=False)