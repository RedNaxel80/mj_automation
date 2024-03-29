import requests
from settings import Settings


def pass_prompt_to_self_bot(settings: Settings, prompt: str):
    payload = {"type": 2,
               "application_id": settings.read(Settings.discord_mj_app_id),
               "guild_id": settings.read(Settings.discord_server_id),
               "channel_id": settings.read(Settings.discord_channel_id),
               "session_id": "2fb980f65e5c9a77c96ca01f2c242cf6",
               "data": {"version": settings.read(Settings.discord_mj_app_version),
                        "id": settings.read(Settings.discord_mj_command_imagine), "name": "imagine", "type": 1,
                        "options": [{"type": 3, "name": "prompt", "value": prompt}],
                        "application_command": {"id": settings.read(Settings.discord_mj_command_imagine),
                                                "application_id": settings.read(Settings.discord_mj_app_id),
                                                "version": settings.read(Settings.discord_mj_app_version),
                                                "default_permission": True,
                                                "default_member_permissions": None,
                                                "type": 1, "nsfw": False, "name": "imagine",
                                                "description": "Create images with Midjourney",
                                                "dm_permission": True,
                                                "options": [{"type": 3, "name": "prompt",
                                                             "description": "The prompt to imagine",
                                                             "required": True}]},
                        "attachments": []}}

    header = {
        'authorization': settings.read(Settings.discord_main_token)
    }
    response = requests.post(settings.read(Settings.discord_api_url), json=payload, headers=header)
    return response

# v5
# payload = {
#     "type": 2,
#     "application_id": "936929561302675456",
#     "guild_id": "1097284163872227420",
#     "channel_id": "1109230314204700882",
#     "session_id": "d8126e072e5a575d80dc5871d2c99c5e",
#     "data": {
#         "version": "1077969938624553050",
#         "id": "938956540159881230",
#         "name": "imagine",
#         "type": 1,
#         "options": [{"type": 3, "name": "prompt", "value": "newton with an apple tree"}],
#         "application_command": {"id": "938956540159881230", "application_id": "936929561302675456",
#                                 "version": settings.read(Settings.discord_mj_app_version), "default_member_permissions": None, "type": 1,
#                                 "nsfw": False, "name": "imagine", "description": "Create images with Midjourney",
#                                 "dm_permission": True, "contexts": None, "options": [
#                 {"type": 3, "name": "prompt", "description": "The prompt to imagine", "required": True}]},
#         "attachments": []}, "nonce": "1111221304406573056"}


# raw data from fiddler
def upscale(settings: Settings, index: int, message_id: str, message_hash: str):
    payload = {"type": 3,
               "guild_id": settings.read(Settings.discord_server_id),
               "channel_id": settings.read(Settings.discord_channel_id),
               "message_flags": 0,
               "message_id": message_id,
               "application_id": settings.read(Settings.discord_mj_app_id),
               "session_id": "45bc04dd4da37141a5f73dfbfaf5bdcf",
               "data": {"component_type": 2,
                        "custom_id": "MJ::JOB::upsample::{}::{}".format(index, message_hash)}
               }
    header = {
        'authorization': settings.read(Settings.discord_main_token)
    }
    response = requests.post(settings.read(Settings.discord_api_url), json=payload, headers=header)
    return response


# only works for v4, it will throw an error for v5
def upscale_max(settings: Settings, message_id: str, message_hash: str):
    payload = {"type": 3,
               "guild_id": settings.read(Settings.discord_server_id),
               "channel_id": settings.read(Settings.discord_channel_id),
               "message_flags": 0,
               "message_id": message_id,
               "application_id": settings.read(Settings.discord_mj_app_id),
               "session_id": "1f3dbdf09efdf93d81a3a6420882c92c",
               "data":
                   {"component_type": 2,
                    "custom_id": "MJ::JOB::upsample_beta::1::{}::SOLO".format(message_hash)}}
    header = {
        'authorization': settings.read(Settings.discord_main_token)
    }
    response = requests.post(settings.read(Settings.discord_api_url), json=payload, headers=header)
    return response

# def variation(index: int, message_id: str, message_hash: str):
#     payload = {"type": 3,
#                "guild_id": settings.read(Settings.discord_server_id),
#                "channel_id": settings.read(Settings.discord_channel_id),
#                "message_flags": 0,
#                "message_id": message_id,
#                "application_id": settings.read(Settings.discord_mj_app_id),
#                "session_id": "1f3dbdf09efdf93d81a3a6420882c92c",
#                "data": {"component_type": 2, "custom_id": "MJ::JOB::variation::{}::{}".format(index, message_hash)}}
#     header = {
#         'authorization': settings.read(Settings.discord_main_token)
#     }
#     response = requests.post(settings.read(Settings.discord_api_url), json=payload, headers=header)
#     return response
