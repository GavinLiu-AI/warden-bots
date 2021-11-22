from google.oauth2 import service_account
from googleapiclient.discovery import build

import utils


def get_spreadsheet():
    scopes = utils.SCOPES
    service_account_file = utils.GOOGLE_KEY
    creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build('sheets', 'v4', credentials=creds)

    return service.spreadsheets()


def read(tab):
    sheet = get_spreadsheet()
    result = sheet.values().get(spreadsheetId=utils.SPREADSHEET_ID, range=tab).execute()
    return result.get('values')[1::]


def append_to_sheet(tab, data):
    sheet = get_spreadsheet()
    request = sheet.values().append(
        spreadsheetId=utils.SPREADSHEET_ID,
        valueInputOption='USER_ENTERED',
        range=tab,
        body={'values': data})
    request.execute()


def update_data(data, range):
    sheet = get_spreadsheet()
    request = sheet.values().update(
        spreadsheetId=utils.SPREADSHEET_ID,
        valueInputOption='USER_ENTERED',
        range=range,
        body={'values': data})
    request.execute()


def find_user_row(user_id, data=None):
    if not data:
        data = read(tab=utils.TAB_DATA)
    ids = [int(row[0]) for row in data]
    for row, id in enumerate(ids):
        if id == user_id:
            # Account for 0-index and sheet header
            return row
    return 1000


def upload_data(data, update=False):
    new_data = [data]

    if update:
        row = find_user_row(int(data[0])) + 2
        if row != 0:
            update_data(new_data, range='data!A{0}'.format(row))

    else:
        append_to_sheet(utils.TAB_DATA, new_data)


def upload_war_signup(data):
    new_data = [data]
    append_to_sheet(utils.TAB_WARSIGNUP, new_data)
