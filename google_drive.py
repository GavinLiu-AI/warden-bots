from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import utils
from PIL import Image
import requests
import os

SCOPES = ['https://www.googleapis.com/auth/drive']
SCREENSHOTS_FOLDER_ID = '1Y49KWw_FUt-X8_Jz1xwKKLP8_YdXhQbe'


def get_drive():
    service_account_file = utils.GOOGLE_KEY
    creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    return service


def create_folder(name, parent_id):
    service = get_drive()
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    return service.files().create(body=file_metadata, fields='id', supportsAllDrives=True).execute()


def list_folders(parent_id):
    query = f"parents = '{parent_id}'"
    response = get_drive().files().list(q=query).execute()
    files = response.get('files')
    return files


def save_screenshot(name, url):
    _, ext = os.path.splitext(url)
    name += ext
    image = Image.open(requests.get(url, stream=True).raw)
    image.save(f'{utils.SCREENSHOTS_DIR}/{name}')

    return name


def upload_screenshot(parent_id, name):
    service = get_drive()
    file_metadata = {
        'name': name,
        'parents': [parent_id]
    }
    media = MediaFileUpload(f'{utils.SCREENSHOTS_DIR}/{name}', mimetype='image/jpeg')
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()


def remove_screenshot_from_dir(dir, name):
    try:
        os.remove(f'{dir}/{name}')
    except OSError:
        pass
