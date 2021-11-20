from googleapiclient.discovery import build
from google.oauth2 import service_account
import utils


def get_spreadsheet():
    scopes = utils.SCOPES
    service_account_file = utils.GOOGLE_KEY
    creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build('sheets', 'v4', credentials=creds)

    return service.spreadsheets()


def read():
    sheet = get_spreadsheet()
    result = sheet.values().get(spreadsheetId=utils.SPREADSHEET_ID, range='data').execute()
    return result.get('values')[1::]


def append(data):
    sheet = get_spreadsheet()
    request = sheet.values().append(
        spreadsheetId=utils.SPREADSHEET_ID,
        valueInputOption='USER_ENTERED',
        range='data',
        body={'values': data})
    request.execute()


def update(data, range):
    sheet = get_spreadsheet()
    request = sheet.values().update(
        spreadsheetId=utils.SPREADSHEET_ID,
        valueInputOption='USER_ENTERED',
        range=range,
        body={'values': data})
    request.execute()
