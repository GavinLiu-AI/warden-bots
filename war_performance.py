from datetime import datetime
from pytz import timezone
import spreadsheet
import utils
import role_selection as rs
import discord
import google_drive as drive


def get_current_war():
    data = spreadsheet.read_sheet(sheet_id=spreadsheet.SPREADSHEET_WAR_ATTENDANCE_ID, _range=spreadsheet.TAB_ALL_WARS)
    if not data:
        return None

    for d in data:
        date_time = f'{d[0]} {d[1]}'
        date_time = datetime.strptime(date_time, utils.DATETIME_FORMAT)
        minutes = (datetime.now(timezone('US/Pacific')).now() - date_time).total_seconds() / 60
        print(minutes)
        if 0 <= minutes < 30:
            return [d[0]] + d[2:]

    return None


async def track_vc_members(bot, current_war):
    if not current_war:
        return

    members = bot.get_channel(utils.WAR_GENERAL_CHANNEL_ID).members

    data = spreadsheet.read_sheet(sheet_id=spreadsheet.SPREADSHEET_WAR_ATTENDANCE_ID, _range=spreadsheet.TAB_ATTENDANCE)
    attendance = [d[0] for d in data]

    for m in members:
        if str(m.id) not in attendance:
            spreadsheet.append_to_sheet(sheet_id=spreadsheet.SPREADSHEET_WAR_ATTENDANCE_ID, _range=spreadsheet.TAB_ATTENDANCE,
                                        data=[[str(m.id), str(m), current_war[0], current_war[1], current_war[2]]])


# def image_to_text(image_url):
#     image = Image.open(requests.get(image_url, stream=True).raw)
#     image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#
#     _, mask = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
#     bilateral = cv2.bilateralFilter(mask, 9, 100, 100)
#
#     reader = easyocr.Reader(['en'])
#     result = reader.readtext(bilateral)
#
#     text = [r[1] for r in result]
#
#     return


async def in_war_prompt(bot, user, current_war):
    emojis = [utils.YES_EMOJI, utils.NO_EMOJI]
    title = 'Did you participate in {zone} {offense} on {date}' \
        .format(zone=current_war[1], offense=current_war[2], date=current_war[0])
    description = f'Please click on {utils.YES_EMOJI} or {utils.NO_EMOJI}\n\n{utils.WAR_PERF_VERIFICATION}'

    embed = discord.Embed(title=title,
                          description=description,
                          colour=discord.Colour.gold())
    message = await user.send(embed=embed)
    await utils.add_emojis(msg=message, emojis=emojis)


async def end_message(user):
    title = 'Thank you for completing the survey!'
    description = 'Please stay tuned and sign up for future wars in **Wardens Event Channel** via **Warden Bot**'

    embed = discord.Embed(title=title,
                          description=description,
                          colour=discord.Colour.gold())
    await user.send(embed=embed)


async def ask_screenshot(bot, user):
    title = 'Upload Performance Screenshot / Manual Entry'
    description = 'Please send **one full screenshot** in this DM, screenshot example below.' \
                  '\n\nOr type **End** to end performance survey'

    embed = discord.Embed(title=title,
                          description=description,
                          colour=discord.Colour.gold())
    embed.set_image(url=utils.PERF_IMAGE_URL)
    q = await user.send(embed=embed)

    reply = await bot.wait_for(
        "message",
        timeout=1800,
        check=lambda m: m.author == user and m.channel.id == q.channel.id)

    if reply.attachments:
        return reply.attachments[0].url

    return None


async def dm_screenshots_prompts(bot):
    # [discordId, discordName, date, zone, format]
    dm_list = spreadsheet.read_sheet(sheet_id=spreadsheet.SPREADSHEET_WAR_ATTENDANCE_ID, _range=spreadsheet.TAB_WAR_PERF_DM_LIST)
    if not dm_list:
        return

    for person in dm_list:
        try:
            user_id = person[0]
            user = bot.get_user(int(user_id))

            # Ask if they were in war
            # war_content = [date, zone, format]
            war_content = person[2:]
            await in_war_prompt(bot, user, war_content)

        except Exception as e:
            await utils.log_in_channel(bot, e)

    spreadsheet.get_spreadsheet().values().clear(spreadsheetId=spreadsheet.SPREADSHEET_WAR_ATTENDANCE_ID,
                                                 range=spreadsheet.TAB_WAR_PERF_DM_LIST + '!A2:Z1000').execute()


async def end_current_war():
    attendance = spreadsheet.read_sheet(sheet_id=spreadsheet.SPREADSHEET_WAR_ATTENDANCE_ID, _range=spreadsheet.TAB_ATTENDANCE)
    spreadsheet.append_to_sheet(sheet_id=spreadsheet.SPREADSHEET_WAR_ATTENDANCE_ID, _range=spreadsheet.TAB_WAR_PERF_DM_LIST,
                                data=attendance)
    spreadsheet.get_spreadsheet().values().clear(spreadsheetId=spreadsheet.SPREADSHEET_WAR_ATTENDANCE_ID,
                                                 range=spreadsheet.TAB_ATTENDANCE + '!A2:Z1000').execute()


async def dm_screenshots(bot, user, war_content):
    # war_content = [zone, format, date]
    image_url = await ask_screenshot(bot, user)
    if image_url:
        war_content[1] = '-'.join(war_content[1])
        folder_name = '-'.join(war_content)

        folders = drive.list_folders(drive.SCREENSHOTS_FOLDER_ID)
        if folder_name not in [f.get('name') for f in folders]:
            folder_id = drive.create_folder(folder_name, drive.SCREENSHOTS_FOLDER_ID)['id']
        else:
            folder_id = next(f['id'] for f in folders if f['name'] == folder_name)

        name = drive.save_screenshot(name=str(user.id), url=image_url)
        drive.upload_screenshot(parent_id=folder_id, name=name)
        drive.remove_screenshot_from_dir(dir=utils.SCREENSHOTS_DIR, name=name)

    players_data = spreadsheet.read_sheet(sheet_id=spreadsheet.SPREADSHEET_WAR_ID, _range=spreadsheet.TAB_DATA)
    if rs.user_id_exists(players_data, user.id):
        player_data = players_data[spreadsheet.get_user_index(_range=spreadsheet.TAB_DATA, user_id=user.id)]
        finished = False
        while not finished:
            player_data, finished = await rs.update_player_data(bot, user, player_data, post_war=True)
    else:
        await rs.start_survey(bot, user, post_war=True)

    await end_message(user)


def get_war_content(title):
    # [zone, offense, 'on', date]
    zone = title[:len(title)-3]
    offense = title[-3]
    if offense == 'Defense':
        offense = 'D'
    elif offense == 'Offense':
        offense = 'O'
    else:
        offense = 'I'
    date = title[-1]

    return [date, zone, offense]
