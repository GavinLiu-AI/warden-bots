from google.oauth2 import service_account
from googleapiclient.discovery import build
import utils

# Google Spreadsheet
SPREADSHEET_WAR_ID = '1Pq5NkCikB5f1dXmWlLQ8nXYiZZTFcrEJggy7OJ3DkoQ'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB_DATA = 'data'
TAB_WARSIGNUP = 'warsignup'

SPREADSHEET_GAME_POLL_ID = '1gUou0_yJqARkcsXPsXAfEk7ahghlDOZyjQyFfHF931M'
TAB_GAMES = 'games'
TAB_PARTICIPANTS = 'participants'

SPREADSHEET_WAR_ATTENDANCE_ID = '1vtS833AMf8tpMX4alyA3Y57VRGQ2nzsRwQFdDtynXYs'
TAB_ALL_WARS = 'all wars'
TAB_ATTENDANCE = 'war attendance'
TAB_WAR_PERF_DM_LIST = 'war perf dm list'


def get_spreadsheet():
    scopes = SCOPES
    service_account_file = utils.GOOGLE_KEY
    creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build('sheets', 'v4', credentials=creds)

    return service.spreadsheets()


def read_sheet(sheet_id, _range):
    sheet = get_spreadsheet()
    result = sheet.values().get(spreadsheetId=sheet_id, range=_range).execute()
    return result.get('values')[1::]


def append_to_sheet(sheet_id, _range, data):
    sheet = get_spreadsheet()
    request = sheet.values().append(
        spreadsheetId=sheet_id,
        valueInputOption='USER_ENTERED',
        range=_range,
        body={'values': data})
    request.execute()


def update_sheet_data(sheet_id, data, _range):
    sheet = get_spreadsheet()
    request = sheet.values().update(
        spreadsheetId=sheet_id,
        valueInputOption='USER_ENTERED',
        range=_range,
        body={'values': data})
    request.execute()


def get_user_index(_range, user_id):
    data = read_sheet(sheet_id=SPREADSHEET_WAR_ID, _range=_range)
    ids = [int(row[0]) for row in data]
    for row, id in enumerate(ids):
        if id == int(user_id):
            return row
    return len(data) - 1


def upload_war_data(data, update=False):
    new_data = [data]

    if update:
        sheet_row = get_user_index(_range=TAB_DATA, user_id=int(data[0])) + 2
        if sheet_row != 0:
            update_sheet_data(sheet_id=SPREADSHEET_WAR_ID, data=new_data,
                              _range=TAB_DATA + f'!A{sheet_row}')

    else:
        append_to_sheet(sheet_id=SPREADSHEET_WAR_ID, _range=TAB_DATA, data=new_data)


def upload_war_signup(data):
    new_data = [data]

    # Check if player exist in war signup
    all_data = read_sheet(sheet_id=SPREADSHEET_WAR_ID, _range=TAB_WARSIGNUP)
    index_id = 0
    index_date = -2
    index_zone = -3
    for i, j in enumerate(all_data):
        if j[index_id] == data[index_id] and j[index_date] == data[index_date] and j[index_zone] == data[index_zone]:
            update_sheet_data(sheet_id=SPREADSHEET_WAR_ID, data=new_data,
                              _range=TAB_WARSIGNUP + f'!A{i + 2}')
            return

    append_to_sheet(sheet_id=SPREADSHEET_WAR_ID, _range=TAB_WARSIGNUP, data=new_data)


def get_game_index(game):
    data = read_sheet(sheet_id=SPREADSHEET_GAME_POLL_ID, _range=TAB_GAMES)
    for index, d in enumerate(data):
        if d[0] == game:
            return index, int(d[1])
    return len(data) - 1, 0


def clear_game_poll():
    data = read_sheet(sheet_id=SPREADSHEET_GAME_POLL_ID, _range=TAB_GAMES)
    new_data = [[d[0], 1] for d in data]
    update_sheet_data(sheet_id=SPREADSHEET_GAME_POLL_ID, data=new_data,
                      _range=TAB_GAMES + '!A2')

    get_spreadsheet().values().clear(spreadsheetId=SPREADSHEET_GAME_POLL_ID,
                                     range=TAB_PARTICIPANTS + '!A2:1000').execute()
