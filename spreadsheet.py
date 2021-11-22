from google.oauth2 import service_account
from googleapiclient.discovery import build

import utils


def get_spreadsheet():
    scopes = utils.SCOPES
    service_account_file = utils.GOOGLE_KEY
    creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build('sheets', 'v4', credentials=creds)

    return service.spreadsheets()


def read(_range):
    sheet = get_spreadsheet()
    result = sheet.values().get(spreadsheetId=utils.SPREADSHEET_ID, range=_range).execute()
    return result.get('values')[1::]


def append_to_sheet(_range, data):
    sheet = get_spreadsheet()
    request = sheet.values().append(
        spreadsheetId=utils.SPREADSHEET_ID,
        valueInputOption='USER_ENTERED',
        range=_range,
        body={'values': data})
    request.execute()


def update_data(data, _range):
    sheet = get_spreadsheet()
    request = sheet.values().update(
        spreadsheetId=utils.SPREADSHEET_ID,
        valueInputOption='USER_ENTERED',
        range=_range,
        body={'values': data})
    request.execute()


def find_user_row(_range, user_id):
    data = read(_range)
    ids = [int(row[0]) for row in data]
    for row, id in enumerate(ids):
        if id == int(user_id):
            return row
    return 1000


def upload_data(data, update=False):
    new_data = [data]

    if update:
        sheet_row = find_user_row(_range=utils.TAB_DATA, user_id=int(data[0])) + 2
        if sheet_row != 0:
            update_data(new_data, _range=utils.TAB_DATA + '!A{0}'.format(sheet_row))

    else:
        append_to_sheet(_range=utils.TAB_DATA, data=new_data)


def upload_war_signup(data):
    new_data = [data]

    # Check if player exist in war signup
    all_data = read(_range=utils.TAB_WARSIGNUP)
    index_id = 0
    index_date = -2
    index_zone = -3
    for i, j in enumerate(all_data):
        if j[index_id] == data[index_id] and j[index_date] == data[index_date] and j[index_zone] == data[index_zone]:
            update_data(data=new_data, _range=utils.TAB_WARSIGNUP + '!A{0}'.format(i + 2))
            return

    append_to_sheet(utils.TAB_WARSIGNUP, new_data)
