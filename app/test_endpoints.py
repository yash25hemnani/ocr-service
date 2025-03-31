from app.main import app, BASE_DIR, UPLOAD_DIR, get_settings # Getting the variable
from fastapi.testclient import TestClient
import shutil
from PIL import Image, ImageChops
import io

client = TestClient(app)

def test_get_home():
    response = client.get("/") # request.get("/") --> Similar
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']

def test_invalid_file_upload_error():
    response = client.post("/") # request.get("/") --> Similar
    assert response.status_code == 422
    assert "application/json" in response.headers['content-type']

def test_prediction_upload_missing_header():
    img_saved_path = BASE_DIR / "images"

    for path in img_saved_path.glob("*"): # glob("*.png")
        # Sending without headers
        response = client.post("/",
        files={"file": open(path, 'rb')})
        assert response.status_code == 401


def test_prediction_upload():
    img_saved_path = BASE_DIR / "images"
    settings = get_settings()
    print("The settings are: ", settings)

    # glob allows you to make a list of all files of specified directory.
    for path in img_saved_path.glob("*"): # glob("*.png")
        # Upload the file to the endpoint

        try:
            img = Image.open(path)
        except:
            img = None

        response = client.post("/",
        files={"file": open(path, 'rb')},
        headers={"Authorization": f"JWT {settings.app_auth_token}"})

        if img is None:
            assert response.status_code == 400
        else:
            # print(response.text)
            assert response.status_code == 200
            data = response.json()
            # print(data)
            assert len(data.keys()) == 2

def test_echo_upload():
    img_saved_path = BASE_DIR / "images"

    # glob allows you to make a list of all files of specified directory.
    for path in img_saved_path.glob("*"): # glob("*.png")
        # Upload the file to the endpoint
        response = client.post("/img-echo/", files={"file": open(path, 'rb')})

        try:
            img = Image.open(path)
        except:
            img = None

        if img is None:
            assert response.status_code == 400
        else:
            # Returning a valid image
            assert response.status_code == 200
            r_stream = io.BytesIO(response.content)
            echo_img = Image.open(r_stream)
            difference = ImageChops.difference(echo_img, img).getbbox()
            assert difference is None


    # Empty the folder after testing is complete
    shutil.rmtree(UPLOAD_DIR)



