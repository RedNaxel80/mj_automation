import config
import requests


def pass_prompt_to_self_bot(prompt: str):
    payload = {"type": 2, "application_id": config.MIDJOURNEY_ID, "guild_id": config.SERVER_ID,
               "channel_id": config.CHANNEL_ID, "session_id": "2fb980f65e5c9a77c96ca01f2c242cf6",
               "data": {"version": "1077969938624553050", "id": "938956540159881230", "name": "imagine", "type": 1,
                        "options": [{"type": 3, "name": "prompt", "value": prompt}],
                        "application_command": {"id": "938956540159881230",
                                                "application_id": config.MIDJOURNEY_ID,
                                                "version": "1077969938624553050",
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
        'authorization': config.MAIN_TOKEN
    }
    response = requests.post(config.DISCORD_API_URL, json=payload, headers=header)
    return response


def upscale(index: int, message_id: str, message_hash: str):
    payload = {"type": 3,
               "guild_id": config.SERVER_ID,
               "channel_id": config.CHANNEL_ID,
               "message_flags": 0,
               "message_id": message_id,
               "application_id": config.MIDJOURNEY_ID,
               "session_id": "45bc04dd4da37141a5f73dfbfaf5bdcf",
               "data": {"component_type": 2,
                        "custom_id": "MJ::JOB::upsample::{}::{}".format(index, message_hash)}
               }
    header = {
        'authorization': config.MAIN_TOKEN
    }
    response = requests.post(config.DISCORD_API_URL, json=payload, headers=header)
    return response


# def max_upscale(message_id: str, message_hash: str):
#     payload = {"type": 3,
#                "guild_id": config.SERVER_ID,
#                "channel_id": config.CHANNEL_ID,
#                "message_flags": 0,
#                "message_id": message_id,
#                "application_id": config.MIDJOURNEY_ID,
#                "session_id": "1f3dbdf09efdf93d81a3a6420882c92c", "data":
#                    {"component_type": 2, "custom_id": "MJ::JOB::upsample_max::1::{}::SOLO".format(message_hash)}}
#     header = {
#         'authorization': config.MAIN_TOKEN
#     }
#     response = requests.post(config.DISCORD_API_URL, json=payload, headers=header)
#     return response
#
#
# def variation(index: int, message_id: str, message_hash: str):
#     payload = {"type": 3, "guild_id": config.SERVER_ID,
#                "channel_id": config.CHANNEL_ID,
#                "message_flags": 0,
#                "message_id": message_id,
#                "application_id": config.MIDJOURNEY_ID,
#                "session_id": "1f3dbdf09efdf93d81a3a6420882c92c",
#                "data": {"component_type": 2, "custom_id": "MJ::JOB::variation::{}::{}".format(index, message_hash)}}
#     header = {
#         'authorization': config.MAIN_TOKEN
#     }
#     response = requests.post(config.DISCORD_API_URL, json=payload, headers=header)
#     return response
