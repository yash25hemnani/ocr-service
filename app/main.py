from fastapi import (
                     FastAPI,
                     Request,
                     Depends,
                     File,
                     UploadFile,
                     HTTPException,
                     Header
                     )
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import pathlib
from pydantic_settings import BaseSettings
from functools import lru_cache
import io
import uuid
from PIL import Image
from dotenv import load_dotenv
import pytesseract
from pydantic import ConfigDict, Field
from typing import Optional
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"

load_dotenv(".env")

class Settings(BaseSettings):
    debug: bool = Field(default=False, env="DEBUG")
    echo_active: bool = Field(default=False, env="ECHO_ACTIVE")
    app_auth_token: Optional[str] = Field(default=None, env="APP_AUTH_TOKEN")
    app_auth_token_prod: Optional[str] = Field(default=None, env="APP_AUTH_TOKEN_PROD")
    skip_auth: bool = Field(default=False, env="SKIP_AUTH")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# @lru_cache
def get_settings():
    return Settings()

settings = get_settings()
DEBUG = settings.debug
print("Outside the route ", DEBUG)


app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
# print(BASE_DIR / "templates")

# Since FastAPI returns JSON by default, we will need to specify the response_class to HTML Response if we need the HTML pages.
@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings:Settings = Depends(get_settings)):
    print("In Route ", settings.debug)
    return templates.TemplateResponse("home.html", {"request":request, "abc":123})


def verify_auth(authorization = Header(None), settings:Settings = Depends(get_settings)):
    """
        The header looks like this
            Authorization: Bearer <token>
        and as key value pair
            {"authorization: "Bearer <token>" }

        What Header(None) does is that it gives us the value of authorization key.
    """
    if settings.debug and settings.skip_auth:
        return

    if authorization is None:
        raise HTTPException(detail="Invalid Auth", status_code=401)

    label, token = authorization.split(" ")
    print(dict(settings))

    if token != settings.app_auth_token:
        raise HTTPException(detail="Invalid Auth", status_code=401)



@app.post("/")
async def prediction_view(file: UploadFile = File(...), authorization = Header(None), settings:Settings = Depends(get_settings)):
    verify_auth(authorization, settings)

    bytes_str = io.BytesIO(await file.read())

    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid Image", status_code=400)

    predictions = pytesseract.image_to_string(img)
    predictions_list = [x for x in predictions.split("\n")]

    return {"results": predictions_list, "original": predictions}

@app.post("/img-echo", response_class=FileResponse)
async def img_echo_view(file: UploadFile = File(...), settings:Settings = Depends(get_settings)):

    if not settings.echo_active:
        raise HTTPException(detail="Invalid Endpoint", status_code=400)

    UPLOAD_DIR.mkdir(exist_ok=True)

    bytes_str = io.BytesIO(await file.read())

    # If it is not an image, or is a text file, we will get an error.
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid Image", status_code=400)

    fname = pathlib.Path(file.filename)
    fext = fname.suffix # .jpg, .txt
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"

    # with open(str(dest), 'wb') as out:
    #     out.write(bytes_str.read())
    # We can write this as -
    img.save(dest)

    return dest
