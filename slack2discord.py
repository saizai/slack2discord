#!/usr/bin/env python3
# Authors: Rocky Slavin
#          Felix Hallqvist
#          Yamiko Hikari
#          Sai (@saizai)
#          Alex Fink
#
# Slack message history importer for Discord
# Note that some functionality won't work properly if not using the import_all command,
# such as messages in threads created in older .json logs (created in the text channel instead),
# or referencing channels not created yet.
# Also note that mentions will only be properly migrated for users already on the discord server.
# To facilitate the fact that people use different nicks, there is a slack2discord.json file where you can map those (if no mapping exists, it just attempts to match name).
# TODO 
#     Post messages looking like the mapped user (webhooks? send() can specify username there)
#     user correlation
#         Add example json file to repo
#             check repo directory for it
#         Use Slack ID rather than name to correlate - Slack ID U... is unique [this part now done], match to Discord long number (not nick#discriminator); see parse_user()
#             Allow mention of people not in same server - discord long ID should work, dunno if discord nick#discriminator can be looked up if they're not on the server
#             Allow bot to propose inviting mapped people?
#         Try using each Slack name to correlate
#         Add command to correlate slack ID to discord mention, edit prior messages to match
#             Get OAuth permission for the user so it can be edited to actually be from them
#         First enumerate all Slack users in import and get import command executor to confirm or change the Discord handle mapping
#     channel correlation
#         Support different names for channels and Discord's category structure
#     replies & threads
#         Transfer replies as replies
#         Name threads better
#         Support Slack's RT of previous messages (both within and between channels) & 'crosspost thread message to channel' - maybe as reply (though that merges), maybe as link to discord message, maybe embed…?
#             Discord doesn't seem to support "reply to message in different channel" https://discord.com/developers/docs/resources/channel#message-reference-object-message-reference-structure
#             Track & save correlation of discord message ID <-> slack message ID so it can be referenced
#                 on re-imports just edit previous message if it exists
#         Translate Slack URLs (for same server)
#     Slack edited messages
#         check if this is supported / translated
#     attachments & embeds
#         If total embeds length > 6000, send as separate messages
#         If embed is for a file, file has to go on the same message as its embed
#             see e.g. first send() command within send_message()
#         Add embeds for URLs
#             If URL is external image location, use image embed type and maybe just reupload image
#             If multiple URLs in a message, maybe multiple embeds (for preview cards)?
#     message pinning
#     other message support
#         bot messages
#         join/part messages
#         reactions
#             on behalf of actual user? by bot spoofing user using webhook?
#         emotes?
#             check if Slack has markup for this
#         use Slack's "blocks" rather than its textdump?
#             would require enumerating all the types
#             but no regex issues
#             could more easily determine where to split the message if needed
#         is it possible to backdate messages?
#             AFAICT no but should check API more

# discord.py async calls https://discordpy.readthedocs.io/en/stable/api.html :
#     Connectable, Client, AutoShardedClient, VoiceProtocol
#         connect
#     Messageable, PartialMessageable, Member, User, TextChannel, Thread, VoiceChannel, DMChannel, GroupChannel
#        fetch_message
#        history
#        pins
#        send
#     Widget, Client
#         fetch_invite
#     PartialMessage, WebhookMessage, Message
#        add_reaction
#        clear_reaction
#        clear_reactions
#        create_thread
#        delete
#        edit
#        fetch
#        pin
#        publish
#        remove_reaction
#        reply
#        unpin
#     GuildChannel, TextChannel, ForumChannel, VoiceChannel, StageChannel, CategoryChannel
#        clone
#        create_invite
#        delete
#        invites
#        move
#        set_permissions
#     Client
#         application_info
#         before_identify_hook
#         change_presence
#         close
#         create_dm
#         create_guild
#         delete_invite
#         fetch_channel
#         fetch_guild
#         fetch_guilds
#         fetch_premium_sticker_packs
#         fetch_stage_instance
#         fetch_sticker
#         fetch_template
#         fetch_user
#         fetch_webhook
#         fetch_widget
#         login
#         on_error
#         setup_hook
#         start
#         wait_for
#         wait_until_ready
#    AutoShardedClient
#        change_presence
#        close
#    VoiceClient
#        disconnect
#        move_to
#     VoiceProtocol
#        disconnect
#        on_voice_server_update
#        on_voice_state_update
#     Webhook (but not SyncWebhook)
#        edit
#        edit_message
#        fetch
#        fetch_message
#        send
#     WebhookMessage
#        add_files
#        remove_attachments
#     ClientUser
#         edit
#     User
#        create_dm
#     Attachment, Asset
#        read
#        save
#        to_file
#     Message
#        add_files
#        remove_attachments
#     Reaction
#        clear
#        remove
#        users
#     CategoryChannel, Guild
#        create_forum
#        create_stage_channel
#        create_text_channel
#        create_voice_channel
#        edit
#     Guild
#        active_threads
#        audit_logs
#        ban
#        bans
#        change_voice_state
#        chunk
#        create_automod_rule
#        create_category
#        create_category_channel
#        create_custom_emoji
#        create_integration
#        create_role
#        create_scheduled_event
#        create_sticker
#        create_template
#        delete
#        delete_emoji
#        delete_sticker
#        edit_role_positions
#        edit_welcome_screen
#        edit_widget
#        estimate_pruned_members
#        fetch_automod_rule
#        fetch_automod_rules
#        fetch_ban
#        fetch_channel
#        fetch_channels
#        fetch_emoji
#        fetch_emojis
#        fetch_member
#        fetch_members
#        fetch_roles
#        fetch_scheduled_event
#        fetch_scheduled_events
#        fetch_sticker
#        fetch_stickers
#        integrations
#        invites
#        kick
#        leave
#        prune_members
#        query_members
#        templates
#        unban
#        vanity_invite
#        webhooks
#        welcome_screen
#        widget
#    ScheduledEvent
#        cancel
#        delete
#        edit
#        end
#        start
#        users
#     Member
#        add_roles
#        ban
#        create_dm
#        edit
#        kick
#        move_to
#        remove_roles
#        request_to_speak
#        timeout
#        typing
#     PartialEmoji, Emoji
#        read
#        save
#        to_file
#     Emoji, Role
#        delete
#        edit
#    ForumChannel, TextChannel
#        create_thread
#        create_webhook
#        edit
#        webhooks
#     TextChannel
#        archived_threads
#        delete_messages
#        follow
#        purge
#     Thread
#        add_user
#        delete
#        delete_messages
#        edit
#        fetch_member
#        fetch_members
#        join
#        leave
#        purge
#        remove_user
#     VoiceChannel
#        connect
#        create_webhook
#        delete_messages
#        edit
#        purge
#        webhooks
#     StageChannel
#        connect
#        create_instance
#        edit
#        fetch_instance
#     WelcomeScreen
#         edit
#     StageInstance, GuildSticker
#        delete
#        edit
#     GroupChannel
#        leave
#     Invite
#         delete
#     Template
#        create_guild
#        delete
#        edit
#        sync
#     StickerItem
#         fetch
#     StandardSticker
#         pack
#     ShardInfo
#        connect
#        disconnect
#        reconnect

import json
import re
import sys
import os
import html
import time
from datetime import datetime
import discord
from discord.ext import commands

MAX_EMBEDS = 1
if discord.__version__[0] >= "2":
    MAX_EMBEDS = 10

MAX_CHARACTERS = 2000
MAX_EMBED_CHARACTERS = 4096
MAX_TOTAL_EMBEDS_CHARACTERS = 6000 # https://discord.com/developers/docs/resources/channel#embed-object-embed-limits

THROTTLE = True
THROTTLE_TIME_SECONDS = 0.1


def check_optional_dependencies():
    print(f"[INFO] Checking (optional) dependency versions:")
    if discord.__version__[0] < "2":
        # Pre discord.py v2.0 the bot can only give messages 1 embed,
        #  so has to be split into multiple messages.
        # Creating threads was added in discord.py v2.0
        # discord.py v2.0 also increased the package's requirements,
        #  requiring a higher python version.
        # It is thus treated as optional.
        print(f"[WARNING] discord.py version < 2.0, currently using version: {discord.__version__}")
        print(f"          Some features are unsupported with current version:")
        print(f"          * Unable to create Threads")
        print(f"            - Messages will be sent directly to the owner's TextChannel instead.")
        print(f"          * Messages are unable to contain more than 1 Embed each")
        print(f"            - Multiple attachments they will be split into multiple messages,")
        print(f"               linking to their 'parent' message.")
        print(f"          Upgrade discord.py to >= 2.0 to enable those features.")
        
        if sys.version_info[1] < 8:
            print(f"[INFO] Current python version does not satisfy discord.py v2.0 dependency. Current: {'.'.join(map(str, sys.version_info[:3]))}")
            print(f"       You will be unable to upgrade discord.py to v2.0,")
            print(f"        unless you first upgrade python to >= 3.8")
    else:
        print(f"       All features enabled! - No dependencies unsatisfied")
    print(f"")


def get_basename(file_path):
    if os.path.basename(file_path):
        return os.path.basename(file_path)
    else: # 'foo/bar/' has no basename, but os.path.split strips trailing slash and returns 'foo/bar'
        return os.path.basename(os.path.split(file_path)[0])


def get_filename(file_path):
    return get_basename(os.path.splitext(file_path)[0])

# async
def parse_slack_directory(file_path, force_all=False):
    """
    Parses the path to find important root-files and relevant .json logs, and stores them in a dict of the form:\n
    {
        "root_files": {"file": path},\n
        "history": {"channel": [path_json_logs]}
    }
    :param file_path: String path to directory or file
    :return: The resulting dict.
    """
    slack_dir = {}
    slack_dir["root_files"] = {}
    slack_dir["history"] = {}
    
    slack_root_files = {
        "users.json" : "A file that maps internal user-ids to usernames, allowing message headers and mentions to display their human readable names",
        "channels.json" : "A file that maps internal channel-ids to channel-names, allowing channel-mentions to display their human readable names",
        "integration_logs.json" : "This file has no associated feature, and can safely be ignored with no effect."
    }
    user_root_files = {
        "slack2discord_users.json": "A file used to map slack-names to discord-names, allowing slack-mentions to be exported into discord-mentions even when usernames change between platforms."
    }
    root_files = dict(slack_root_files, **user_root_files)

    # Locate root
    print(f"[INFO] Attempting to locate slack-root directory from path: {file_path}")
    root = file_path
    if os.path.isfile(file_path):
        print("[WARNING] Path points at a file and not a directory")
        print("[INFO] Assumes parent-directory is either root or a channel-subdir")
        print("       | slack-root/  <- directory?")
        print("       |__  *.json")
        print("          | channel/  <- directory?")
        print("          |    *.json")
        root = os.path.dirname(file_path)
        
    if any([os.path.exists(os.path.join(root, f)) for f in slack_root_files]):
        print(f"[INFO] Success! slack-root found: {root}")
    else:
        print(f"[WARNING] Directory is not root of a slack-log directory: {root}")
        print("[INFO] Assumes directory is a channel-subdir, and parent-directory is the root.")
        print("       | slack-root/  <- root?")
        print("       |__  *.json")
        print("          | channel/  <- directory")
        print("          |    *.json")
        root = os.path.dirname(root)
        if any([os.path.exists(os.path.join(root, f)) for f in slack_root_files]):
            print(f"[INFO] Success! slack-root found: {root}")
        else:
            print("[WARNING] Parent-directory is not root of a slack-log directory; Unable to locate root")
            query = input("\nDo you want to ignore and continue with input path forcefully treated as 'root'? (Y/N): ")
            if query.lower() in ["y", "yes"]:
                print(f"[INFO] Reverts to treating input path as root: {file_path}")
                root = file_path
            else:
                print(f"[ERROR] User aborted - no root")
                return None

    # Assert existence of root-files, querying user to ignore errors
    for ft, ft_files in {"slack": slack_root_files, "user-created": user_root_files}.items():
        print("[INFO] Checking for {ft} files")
        if ft == "user-created":
            print("       Note: User is expected to manually create and fill these files if their functionality is desired.")
        for f, descr in ft_files.items():
            f_path = os.path.join(root, f)
            if os.path.exists(f_path):
                print(f"[INFO] Successfully located {ft} file: {f}")
                slack_dir["root_files"][get_filename(f)] = f_path
            else:
                print(f"[ERROR] Unable to locate {ft} file: {f}")
                print(f"        Description: {descr}")
                query = input("\nDo you want to ignore and continue? (Y/N): ")
                if query.lower() in ["y", "yes"]:
                    print(f"[OK] User ignored missing {ft} file.")
                else:
                    print(f"[ERROR] User aborted at missing {ft} file: {f}")
                    return None
    
    # locate .json logs
    print(f"[INFO] Attempting to locate relevant .json logs")
    if force_all is True:
        subdirs = [d for d in [os.path.join(root, n) for n in os.listdir(root)] if os.path.isdir(d)]
        for d in subdirs:
            slack_dir["history"][get_basename(d)] = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".json")]
    else:
        if os.path.isfile(file_path):
            print(f"[WARNING] Path does not point at a directory.")
            print(f"[INFO] Assumes path points at the exact .json log file user wants to export.")
            if file_path.endswith(".json"):
                slack_dir["history"][get_basename(os.path.dirname(file_path))] = file_path
            else:
                print(f"[ERROR] Path does not point at a .json file - skipping path.")
                return None
        else:
            subdirs = [file_path] + [d for d in [os.path.join(file_path, n) for n in os.listdir(file_path)] if os.path.isdir(d)]
            for d in subdirs:
                slack_dir["history"][get_basename(d)] = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".json")]
    
    slack_dir["root"] = root

    if not slack_dir["history"]:
        print(f"[ERROR] No history .json logs found at: {file_path}")
        return None
    else:
        print(f"[INFO] Success! {len(slack_dir['history'])} .json logs loaded")
        if not all([get_filename(f) in slack_dir["root_files"] for f in root_files]):
            print(f"[WARNING] Missing important .json files: {({f: ('exists' if get_filename(f) in slack_dir['root_files'] else 'missing') for f in root_files})}")

    return slack_dir


def get_display_names(slack_dir):
    """
    Generates a dictionary of user_id => display_name pairs
    :param slack_dir: Dict representing the slack-log directory
    :return: Dictionary or None if no file is found
    """
    users = {}

    print(f"[INFO] Attempting to locate users.json")

    file_path = slack_dir["root_files"].get("users", None)
    if (not file_path) or (not os.path.isfile(file_path)):
        print(f"[ERROR] Unable to locate users.json: {file_path}")
        return None
    try:
        with open(file_path, encoding="utf-8") as f:
            users_json = json.load(f)
            for user in users_json:
                users[user['id']] = (
                    user['profile']['display_name'] if user['profile']['display_name'] else user['profile'][
                        'real_name'])
                print(f"\tUser ID: {user['id']} -> Display Name: {users[user['id']]}")
    except OSError as e:
        print(f"[ERROR] Unable to load display names: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Unable to load users.json.\n  JSONDecodeError: {e}")
    return users


def get_slack2discord_user_mapping(slack_dir, users):
    """
    Generates a dictionary of (slack user ID) => (discord username).
    Rewrites slack2discord_users.json with the user IDs if there are any entries
    containing only names.
    :param slack_dir: Dict representing the slack-log directory
    :param users: Dict from Slack user IDs to names
    :return: Dictionary or None if no file is found
    """
    slack2discord_uids = {}

    print(f"[INFO] Attempting to locate slack2discord_users.json")
    
    file_path = slack_dir["root_files"].get("slack2discord_users", None)
    if (not file_path) or (not os.path.isfile(file_path)):
        print(f"[ERROR] Unable to locate slack2discord_users.json: {file_path}")
        return None

    try:
        with open(file_path, encoding="utf-8") as f:
            slack2discord_users_json = json.load(f)
            dirty = False # Should we rewrite the json?
            for user in slack2discord_users_json:
                try:
                    slack_id = user["slack"]["id"]
                except KeyError:
                    slack_name = user["slack"]["name"]
                    possible_slack_ids = [id
                        for (id,name) in users.items()
                        if name == slack_name]
                    if len(possible_slack_ids) == 0:
                        print(f"[WARNING] There is no Slack user named \"{slack_name}\"")
                        continue
                    elif len(possible_slack_ids) == 1:
                        slack_id = possible_slack_ids[0]
                    else:
                        print(f"[WARNING] There is more than one Slack user named \"{slack_name}\"")
                        print(f"[FIX] Querying user which is the intended mapping")
                        print(f"[ERROR] ... but that's not implemented") # TODO
                        continue
                    user["slack"]["id"] = slack_id
                    dirty = True
                discord_name = user["discord"]["name"]
                if user["discord"]["id"]:
                    discord_name = discord_name + f'#{user["discord"]["id"]}'
                slack2discord_uids[slack_id] = discord_name
                print(f"\tslack2discord user mapping: {slack_id} -> {discord_name}")
    except OSError as e:
        print(f"[ERROR] Unable to load slack2discord user mapping: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Unable to load slack2discord_users.json.\n  JSONDecodeError: {e}")
    
    if dirty:
        try:
            with open(file_path, mode="w", encoding="utf-8") as f:
                json.dump(slack2discord_users_json, f, indent=1)
        except OSError as e:
            print(f"[ERROR] Unable to save modified slack2discord user mapping: {e}")

    return slack2discord_uids


def get_channel_names(slack_dir):
    """
    Generates a dictionary of channel_id => channel_name pairs
    :param slack_dir: Dict representing the slack-log directory
    :return: Dictionary or None if no file is found
    """
    channels = {}

    print(f"[INFO] Attempting to locate channels.json")

    file_path = slack_dir["root_files"].get("channels", None)
    if (not file_path) or (not os.path.isfile(file_path)):
        print(f"[ERROR] Unable to locate channels.json: {file_path}")
        return None

    try:
        with open(file_path, encoding="utf-8") as f:
            channels_json = json.load(f)
            for channel in channels_json:
                channels[channel['id']] = channel['name']
                print(f"\tChannel ID: {channel['id']} -> Channel Name: {channels[channel['id']]}")
    except OSError as e:
        print(f"[ERROR] Unable to load channel names: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Unable to load channels.json.\n  JSONDecodeError: {e}")
    return channels

def process_link(match_obj):
    return f"[{match_obj.group(1)}]({match_obj.group(2)})"

# async
def fill_references(ctx, message, users, slack2discord_uids, channels, messages):
    """
    Fills in @mentions and #channels with their known display names
    :param message: Raw message to be filled with usernames and channel names instead of IDs
    :param users: Dictionary of user_id => display_name pairs
    :param channels: Dictionary of channel_id => channel_name pairs
    :return: Filled message string
    """


    if users:
        for uid, slack_name in users.items():
            old_str = f"<@{uid}>"
            if old_str in message and slack_name:
                new_str = f"@{slack_name}"
                if slack2discord_uids and uid in slack2discord_uids:
                    discord_name = slack2discord_uids[uid]
                    discord_user = ctx.guild.get_member_named(discord_name)
                    if discord_user:
                        new_str = f"{discord_user.mention}"
                    else:
                        print(f"[ERROR] Mapped user not found on discord: [{slack_name}: {discord_name}]")
                        print(f"        @mentions of user will not be translated to discord-equivalent")
                else:
                    print(f"[WARNING] User not mapped: {slack_name}")
                    print(f"[FIX] Attempt to match the slack name instead")
                    discord_user = ctx.guild.get_member_named(slack_name)
                    if discord_user:
                        new_str = f"{discord_user.mention}"
                    else:
                        print(f"[ERROR] User not found on discord: {slack_name}")
                        print(f"        @mentions of user will contain their ID instead of display name")

                message = message.replace(old_str, new_str)
    if channels:
        for cid, name in channels.items():
            old_str = f"<#{cid}|{name}>"
            if old_str in message:
                new_str = f"#{name}"
                channel = discord.utils.get(ctx.guild.channels, name=name)
                if channel:
                    new_str = f"<#{channel.id}>"
                else:
                    print(f"[ERROR] Channel not found on discord: {name}")
                    print(f"        #channel references of channel will not be translated to discord-equivalent")

                message = message.replace(old_str, new_str)

    return message


def parse_important_files(slack_dir):
    users = get_display_names(slack_dir)
    if users:
        print(f"[INFO] users.json found - attempting to fill @mentions")
    else:
        print(f"[WARNING] No users.json found - @mentions will contain user IDs instead of display names")

    slack2discord_uids = get_slack2discord_user_mapping(slack_dir, users)
    if slack2discord_uids:
        print(f"[INFO] slack2discord_users.json found - attempting to map @mentions")
    else:
        print(f"[ERROR] No slack2discord_users.json found.")
        print(f"[FIX] Querying user for known mappings to generate file") # TODO
        print(f"[ERROR] Querying feature not implemented - @mentions will not map")

    channels = get_channel_names(slack_dir)
    if channels:
        print(f"[INFO] channels.json found - attempting to fill #channel references")
    else:
        print(f"[WARNING] No channels.json found - #channel references will contain their IDs instead of names")

    return users, slack2discord_uids, channels

# async because of guild.create_text_channel
async def get_or_create_channel(ctx, name):
    channel = discord.utils.get(ctx.guild.channels, name=name, type=discord.ChannelType.text)
    if not channel:
        print(f"[INFO] Could not find channel: {name}")
        print(f"       Creating channel")
        channel = await ctx.guild.create_text_channel(name, reason="Migrating Slack channel")
    return channel


def parse_timestamp(message):
    if 'ts' in message:
        return datetime.fromtimestamp(float(message['ts'])).strftime('%Y-%m-%d at %H:%M:%S')
    else:
        print(f"[WARNING] No timestamp in message")
    return '<no timestamp>'


def parse_user(ctx, message, users, slack2discord_uids):
    username = "<unknown user>"
    if "user" in message:
        print(f"[INFO] Located 'user' field, attempting to map uid to username")
        uid = message['user']
        try:
            username = slack2discord_uids[uid]
        except KeyError:
            username = f"<unknown user {uid}>"
            print(f"[WARNING] Failed to map uid to slack username - name will remain the unmapped uid: {username}")
    else:
        print(f"[ERROR] No 'user' field in message - defaulting to '<unknown user>'")

    discord_user = ctx.guild.get_member_named(username)
    if discord_user:
        mention = f"{discord_user.mention}"
    else:
        mention = f"@{username}"

    return mention


def parse_text(ctx, message, username, users, slack2discord_uids, channels, messages):
    text = message.get('text')
    if text:
        timestamp = parse_timestamp(message)
        text = fill_references(ctx, text, users, slack2discord_uids, channels, messages)
        return f"*{timestamp}* **{username}**: {text}"
    else:
        return None

import io
import requests
def parse_files(message):
    # using mapping from https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
    # because mimetypes.guess_extension returns silly results https://stackoverflow.com/questions/53541343/content-type-text-plain-has-file-extension-ksh
    # within embeds, Discord only supports .gif .jpeg .jpg .json (Lottie) .png .webp images https://discord.com/developers/docs/reference#image-formatting-image-formats
    extensions = {
        "audio/aac": ".aac",
        "application/x-abiword": ".abw",
        "application/x-freearc": ".arc",
        "image/avif": ".avif",
        "video/x-msvideo": ".avi",
        "application/vnd.amazon.ebook": ".azw",
        "application/octet-stream": ".bin",
        "image/bmp": ".bmp",
        "application/x-bzip": ".bz",
        "application/x-bzip2": ".bz2",
        "application/x-cdf": ".cda",
        "application/x-csh": ".csh",
        "text/css": ".css",
        "text/csv": ".csv",
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.ms-fontobject": ".eot",
        "application/epub+zip": ".epub",
        "application/gzip": ".gz",
        "image/gif": ".gif",
        "text/html": ".html",
        "image/vnd.microsoft.icon": ".ico",
        "text/calendar": ".ics",
        "application/java-archive": ".jar",
        "image/jpeg": ".jpg",
        "text/javascript": ".js",
        "application/json": ".json",
        "application/ld+json": ".jsonld",
        "audio/midi audio/x-midi": ".midi",
        "text/javascript": ".mjs",
        "audio/mpeg": ".mp3",
        "video/mp4": ".mp4",
        "video/mpeg": ".mpeg",
        "application/vnd.apple.installer+xml": ".mpkg",
        "application/vnd.oasis.opendocument.presentation": ".odp",
        "application/vnd.oasis.opendocument.spreadsheet": ".ods",
        "application/vnd.oasis.opendocument.text": ".odt",
        "audio/ogg": ".oga",
        "video/ogg": ".ogv",
        "application/ogg": ".ogx",
        "audio/opus": ".opus",
        "font/otf": ".otf",
        "image/png": ".png",
        "application/pdf": ".pdf",
        "application/x-httpd-php": ".php",
        "application/vnd.ms-powerpoint": ".ppt",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
        "application/vnd.rar": ".rar",
        "application/rtf": ".rtf",
        "application/x-sh": ".sh",
        "image/svg+xml": ".svg",
        "application/x-tar": ".tar",
        "image/tiff": ".tiff",
        "video/mp2t": ".ts",
        "font/ttf": ".ttf",
        "text/plain": ".txt",
        "application/vnd.visio": ".vsd",
        "audio/wav": ".wav",
        "audio/webm": ".weba",
        "video/webm": ".webm",
        "image/webp": ".webp",
        "font/woff": ".woff",
        "font/woff2": ".woff2",
        "application/xhtml+xml": ".xhtml",
        "application/vnd.ms-excel": ".xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/xml": ".xml",
        "text/xml": ".xml",
        "application/atom+xml": ".xml",
        "application/vnd.mozilla.xul+xml": ".xul",
        "application/zip": ".zip",
        "video/3gpp": ".3gp",
        "audio/3gpp": ".3gp",
        "video/3gpp2": ".3gp",
        "audio/3gpp2": ".3g2",
        "application/x-7z-compressed": ".7z"
    }
    # Slack files have params in the format:
    #  {
    #    "id": "F01A2BCDEFG",
    #    "created": 1659116022,
    #    "timestamp": 1659116022,
    #    "name": "Something.jpg",
    #    "title": "Something",
    #    "mimetype": "image/jpeg",
    #    "filetype": "jpg",
    #    "pretty_type": "JPEG",
    #    "user": "U02A4BCDEF5",
    #    "user_team": "T012A3B4CDE",
    #    "editable": false,
    #    "size": 15005,
    #    "mode": "hosted",
    #    "is_external": false,
    #    "external_type": "",
    #    "is_public": true,
    #    "public_url_shared": false,
    #    "display_as_bot": false,
    #    "username": "",
    #    "url_private": "https://files.slack.com/files-pri/T012A3B4CDE-F01A2BCDEFG/something.jpg?t=xoxe-1234567890123-2345678901234-3456789012345-0a1b2c3d4f5a6b7c8d9e0f1a2b3c4d5e",
    #    "url_private_download": "https://files.slack.com/files-pri/T012A3B4CDE-F01A2BCDEFG/download/image_from_ios.jpg?t=xoxe-1234567890123-2345678901234-3456789012345-0a1b2c3d4f5a6b7c8d9e0f1a2b3c4d5e",
    #    "media_display_type": "unknown",
    #    "thumb_64": "https://files.slack.com/files-tmb/T012A3B4CDE-F01A2BCDEFG-0a2b4c6d7e/image_from_ios_64.jpg?t=xoxe-1234567890123-2345678901234-3456789012345-0a1b2c3d4f5a6b7c8d9e0f1a2b3c4d5e",
    #    "thumb_80": "https://files.slack.com/files-tmb/T012A3B4CDE-F01A2BCDEFG-0a2b4c6d7e/image_from_ios_80.jpg?t=xoxe-1234567890123-2345678901234-3456789012345-0a1b2c3d4f5a6b7c8d9e0f1a2b3c4d5e",
    #    "thumb_360": "https://files.slack.com/files-tmb/T012A3B4CDE-F01A2BCDEFG-0a2b4c6d7e/image_from_ios_360.jpg?t=xoxe-1234567890123-2345678901234-3456789012345-0a1b2c3d4f5a6b7c8d9e0f1a2b3c4d5e",
    #    "thumb_360_w": 360,
    #    "thumb_360_h": 164,
    #    "thumb_480": "https://files.slack.com/files-tmb/T012A3B4CDE-F01A2BCDEFG-0a2b4c6d7e/image_from_ios_480.jpg?t=xoxe-1234567890123-2345678901234-3456789012345-0a1b2c3d4f5a6b7c8d9e0f1a2b3c4d5e",
    #    "thumb_480_w": 480,
    #    "thumb_480_h": 218,
    #    "thumb_160": "https://files.slack.com/files-tmb/T012A3B4CDE-F01A2BCDEFG-0a2b4c6d7e/image_from_ios_160.jpg?t=xoxe-1234567890123-2345678901234-3456789012345-0a1b2c3d4f5a6b7c8d9e0f1a2b3c4d5e",
    #    "thumb_720": "https://files.slack.com/files-tmb/T012A3B4CDE-F01A2BCDEFG-0a2b4c6d7e/image_from_ios_720.jpg?t=xoxe-1234567890123-2345678901234-3456789012345-0a1b2c3d4f5a6b7c8d9e0f1a2b3c4d5e",
    #    "thumb_720_w": 720,
    #    "thumb_720_h": 328,
    #    "thumb_800": "https://files.slack.com/files-tmb/T012A3B4CDE-F01A2BCDEFG-0a2b4c6d7e/image_from_ios_800.jpg?t=xoxe-1234567890123-2345678901234-3456789012345-0a1b2c3d4f5a6b7c8d9e0f1a2b3c4d5e",
    #    "thumb_800_w": 800,
    #    "thumb_800_h": 364,
    #    "original_w": 848,
    #    "original_h": 386,
    #    "thumb_tiny": "AbCDEFGHIJKlmNo1p/qR23stUVxyZABC45D6e/fG7HIJk78lmnoPqrSt9UVWXYZAB+Cd0EFGHIJKL1mNOPQRSTUVw2xY+zABCD3E456F7ghiJK/LmNOPqrS8tuVW9xyZ0abcde1FgHi23J4j/KlM/5n=",
    #    "permalink": "https://unlws.slack.com/files/U02A4BCDEF5/F01A2BCDEFG/something.jpg",
    #    "permalink_public": "https://slack-files.com/T012A3B4CDE-F01A2BCDEFG-0abcd1e2fg",
    #    "is_starred": false,
    #    "has_rich_preview": false,
    #    "file_access": "visible"
    #  }

    files = []
    embeds = []
    for file in message["files"]:
        if "url_private" in file:
            response = requests.get(file["url_private"])
            content = io.BytesIO(response.content)
            extension = file["filetype"]
            filename = file["name"]
            if not filename.endswith(extension):
                filename = f'{filename}{extension}'
            discord_file = discord.File(content, filename)

            if file["mimetype"].split('/')[0] == "image":
                # https://discordpy.readthedocs.io/en/stable/api.html#embed
                discord_embed = discord.Embed(
#                   colour=None,
                    title=file["title"],
                    type="image", # rich, image, video, gifv, article, link https://discord.com/developers/docs/resources/channel#embed-object-embed-types
#                    url=f'attachment://{filename}', # file["url_private"],
#                   description=None,
                    timestamp=datetime.fromtimestamp(file["timestamp"]),
                )
                discord_embed.set_image(url=f'attachment://{filename}') # e.url
                embeds.append(discord_embed)
                files.append(discord_file)
                print(f"[INFO] Embedded file: {file['title']}")
            else:
                files.append(discord_file)
                print(f"[INFO] Attached file: {file['title']}")

        else:
            print(f"[ERROR] File has no 'url_private' field - Unable to migrate file: {file}")
#    files = [discord.Embed(**f) for f in files] 
#    files = [e.set_image(url=e.url) for e in files]
#    files_final = []
#    for f in files:
#        files_final.append(discord.File(img, filename))

    if not "user" in message:
        print(f"[DEBUG] files can't exist without a 'user' field!!!")

    return files, embeds


def parse_message(ctx, message, users, slack2discord_uids, channels, messages):
    msg = None
    files = None
    embeds = None

    if message.get("subtype", None) == "channel_join":
        print(f"[INFO] Message is a 'channel_join' message")
        return None

    if message.get("subtype", None) == "bot_message":
        print(f"[INFO] Message is a 'bot_message' message")
        return None
    
    msg_id = message.get("client_msg_id", None)
    username = parse_user(ctx, message, users, slack2discord_uids)
    
    if "text" in message:
        msg = parse_text(ctx, message, username, users, slack2discord_uids, channels, messages)
    
    if "files" in message:
        files, embeds = parse_files(message)

    if msg:
        msg = html.unescape(msg)
        msg = msg.replace("<!everyone>", "@everyone")

        #message = re.sub(r'<((?:http|ftp|https)://[\w_-]+(?:\.[\w_-]+)+[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])\|(.*)>', process_link, message)
        # slack_link = re.search(r'<((?:http|ftp|https)://[\w_-]+(?:\.[\w_-]+)+[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])\|(.*)>', message)
        # if slack_link:
        #     link, text = slack_link.groups()
        #     message = re.sub(r'<((?:http|ftp|https)://[\w_-]+(?:\.[\w_-]+)+[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])\|(.*)>', "[\1](\2)", message)
        msg_hyperlinked = re.sub(r'<(https?:[^|>]+)>', r"[\1](\1)", msg)
        msg_hyperlinked = re.sub(r'<(https?:[^|>]+)\|([^>]+)>', r"[\2](\1)", msg_hyperlinked)
        # FIXME: check MAX_TOTAL_EMBEDS_CHARACTERS and break up into separate messages if over 6000 char limit
        if (msg != msg_hyperlinked) or (len(msg_hyperlinked) > MAX_CHARACTERS):
            msg = msg_hyperlinked
            while msg and (len(msg) > 0):
                if len(msg) > MAX_EMBED_CHARACTERS:
                    excerpt = msg[:MAX_EMBED_CHARACTERS]
                    newline = excerpt.rfind('\n')
                    excerpt = msg[:newline]
                    next_msg = msg[newline:] # tail
                else:
                    excerpt = msg
                    next_msg = None
                rich_embed = discord.Embed(
                    type="rich",
                    description=excerpt #,
    #                timestamp=datetime.fromtimestamp(file["timestamp"])
    # TODO: see also url, title, type=(article, link, video); set_image, set_footer, set_thumbnail, set_author; video, provider
                )
                embeds = embeds or []
                embeds.append(rich_embed)
                msg = next_msg

    # Create message-header for pure attachments
    if files and not msg and not embeds:
        timestamp = parse_timestamp(message)
        
        msg = f"*{timestamp}* **{username}**: *Attachments:*"
    
    if not msg and not files and not embeds:
        print(f"[ERROR] Failed to parse message: {message}")
        return None

    thread = message.get("thread_ts", None)

    return msg_id, msg, files, embeds, thread

# async because it uses ctx.send() which outputs a coroutine
async def send_message(ctx, msg, ref=None, embeds=None, files=None, allowed_mentions=None):
    if not msg and not files and not embeds:
        print(f"[DEBUG] Why are you here? - Skipping empty message")
        return None
    # this is using TextChannel.send https://discordpy.readthedocs.io/en/stable/api.html#discord.TextChannel.send
    # FIXME: use:
    # nonce (int) – The nonce to use for sending this message. If the message was successfully sent, then the message will have a nonce with this value.
    # reference (Union[Message, MessageReference, PartialMessage]) – A reference to the Message to which you are replying, this can be created using to_reference() or passed directly as a Message. You can control whether this mentions the author of the referenced message using the replied_user attribute of allowed_mentions or by setting mention_author.
    # ? view (discord.ui.View) – A Discord UI View to add to the message.
    
    first_ref = None
    last_ref = None
    # Split and send message *until* the remainder is within the limit, with references
    # FIXME: move this to parse_message and have it return multiple items
#    bot_prefix = "*continuation:*\n"

#    if msg:
#        while len(msg) > MAX_CHARACTERS:
#            excerpt = msg[:MAX_CHARACTERS]
#            newline = excerpt.rfind('\n')
#            excerpt = msg[:newline]
#            ref = await ctx.send(excerpt, reference=ref, allowed_mentions = allowed_mentions)
#            first_ref = first_ref or ref
#            msg = bot_prefix+msg[newline:] # tail
#            if THROTTLE:
#                time.sleep(THROTTLE_TIME_SECONDS)

    # Send the remainder, with any embeds attached
    if not embeds and not files:
        ref = await ctx.send(msg, reference=ref, allowed_mentions = allowed_mentions)
        first_ref = first_ref or ref
        if THROTTLE:
            time.sleep(THROTTLE_TIME_SECONDS)
    else:
        # FIXME: actually do the embed/file splitting
        if embeds and (len(embeds) > MAX_EMBEDS):
            print(f"[INFO] Message contains over {MAX_EMBEDS} embeds.")
            print(f"       They will be split into multiple messages,")
            print(f"        referencing their parent.")
        if files and embeds and len(embeds) == 1 and len(files) == 1:
            first_ref = await ctx.send(msg, file=files[0], embed=embeds[0], allowed_mentions = allowed_mentions)
        else:
            first_ref = await ctx.send(msg, files=files, embeds=embeds, allowed_mentions = allowed_mentions)

        # if discord.__version__[0] >= "2":
        #     while embeds:
        #         ref = await ctx.send(msg, embeds=embeds[:MAX_EMBEDS], reference=last_ref or ref, allowed_mentions = allowed_mentions)
        #         first_ref = first_ref or ref
        #         last_ref = last_ref or ref
        #         if THROTTLE:
        #             time.sleep(THROTTLE_TIME_SECONDS)
        #         msg = "*Additional attachments:*"
        #         embeds=embeds[MAX_EMBEDS:] # tail
        # else:
        #     for embed in embeds:
        #         ref = await ctx.send(msg, embed=embed, reference=last_ref or ref, allowed_mentions = allowed_mentions)
        #         first_ref = first_ref or ref
        #         last_ref = last_ref or ref
        #         if THROTTLE:
        #             time.sleep(THROTTLE_TIME_SECONDS)
        #         msg = "*Additional attachments:*"

    return first_ref

# async because it uses send_message which uses ctx.send() which outputs a coroutine
async def import_files(ctx, fs, users, slack2discord_uids, channels, messages={}):
    # dict mapping slack msg-id -> discord message for migrating replies.
    # messages = {}
    # dict mapping slack thread_timestamp -> discord thread
    #  If discord.py < 2.0 this is instead used to reference thread-owner
    # TODO: extract from or store with messages if present
    threads = {}
    for json_file in sorted(fs):
        print(f"[INFO] Parsing file: {json_file}")
        try:
            with open(json_file, encoding="utf-8") as f:
                for message in json.load(f):
                    print(f"[INFO] Parsing message:")
                    parsed = parse_message(ctx, message, users, slack2discord_uids, channels, messages)
                    if parsed:
                        msg_id, msg, files, embeds, thread_ts = parsed

                        if msg or embeds or files:
                            context = ctx
                            thread_owner = None
                            if not msg_id:
                                print(f"[WARNING] No message-id found - will be unlinkable")
                            # FIXME: Unicode
                            print(f"[INFO] Importing message: '{msg}'")
                            if thread_ts:
                                # Prefix to clarify message owns/belongs to thread
                                prefix = "[Thread OP] "
                                if thread_ts in threads:
                                    print(f"[INFO] Message belongs to thread: {thread_ts}")
                                    if discord.__version__[0] < "2":
                                        # Emulating threads by converting it into a reply-chain
                                        thread_owner = threads[thread_ts]
                                        prefix = "[Thread] "
                                    else:
                                        context = threads[thread_ts]
                                if discord.__version__[0] < "2":
                                    msg = prefix + msg


                            disable_notifications = discord.AllowedMentions.none()
                            message = await send_message(context, msg, ref=thread_owner, embeds=embeds if embeds else None, files=files if files else None, allowed_mentions = disable_notifications)
                            messages[msg_id] = message

                            if thread_ts:
                                if not thread_ts in threads:
                                    print(f"[INFO] Message owns a thread: {thread_ts}")
                                    if discord.__version__[0] < "2":
                                        print(f"       Contents will be sent directly to text-channel, referencing this, instead")
                                        threads[thread_ts] = message
                                    else:
                                        print(f"       Creating thread")
                                        threads[thread_ts] = await message.create_thread(name=thread_ts, reason="Migrating Slack thread")
                                if discord.__version__[0] >= "2":
                                    # Threads need to be archived after each message, as well as creation.
                                    await threads[thread_ts].edit(archived=True)
                            print(f"[INFO] Message imported!")

                        if not msg:
                            print(f"[ERROR] skipping message - Found neither text nor files in message: {message}")
                    else:
                        print(f"[INFO] Ignored unparsed message.")
                    print(f"") # empty line
        except OSError as e:
            print(f"[ERROR] {e}")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Unable to load json-file, skipping.\n  JSONDecodeError: {e}")
        print(f"") # extra empty line
    return messages

# async ecause it uses import_files which uses send_messages which uses ctx.send which outputs a coroutine
async def import_slack_directory(ctx, path, slack_dir, match_channel=True, messages={}):
    if not ctx:
        print(f"[ERROR] Import aborted - No context was given!")
    if not slack_dir:
        print(f"[ERROR] Import aborted - Failed to parse any slack-log directory at {path}")
    elif not slack_dir["history"]:
        print(f"[ERROR] Import aborted - No .json files found at {path}")
    else:
        if match_channel == True:
            print(f"[INFO] Creating missing channels to facilitate channel-references")
            for ch in slack_dir["history"]:
                print(f"[INFO] Checking channel: {ch}")
                await get_or_create_channel(ctx, ch)

        print(f"[INFO] Importing channels")
        users, slack2discord_uids, channels = parse_important_files(slack_dir)
        for ch, fs in slack_dir["history"].items():
            print(f"[INFO] Importing channel: {ch}")
            if match_channel == True:
                ctx = await get_or_create_channel(ctx, ch)
            messages = await import_files(ctx, fs, users, slack2discord_uids, channels)
            print(f"[INFO] Completed importing channel: {ch}")
        print(f"[INFO] Import complete")


# Command callbacks must be coroutines (i.e. async)
def register_commands():
    @bot.command(pass_context=True)
    async def import_all(ctx, *kwpath):
        """
        Attempts to import all slack history from the specified path (relative to the bot).
        The path should be the root of the json data, and not a specific channel.
        Only one path can be supplied, if more than one is given only the first will be used.
        The channels will be derived from the subdirectories corresponding to slack channels.
        Will automatically create channels if they don't exist.
        :param ctx:
        :param path:
        :return:
        """
        paths = list(kwpath)
        path = paths[0]
        print(f"[INFO] Attempting to import '{path}' to server '#{ctx.message.guild.name}'")
        # await
        slack_dir = parse_slack_directory(path, force_all=True)
        messages = await import_slack_directory(ctx, path, slack_dir, messages={})

    @bot.command(pass_context=True)
    async def import_path(ctx, *kwpath):
        """
        Attempts to import the slack history from the .json files at specified path (relative to the bot).
        The path should be the subdirectory corresponding to the desired channel, or exact .json files.
        Will automatically create the channel if it doesn't exist.
        Multiple paths can be passed, in which case the corresponding files will be imported in order.
        Note that this will fail to reference channels that neither exist nor wereincluded in the command
        :param ctx:
        :param path:
        :return:
        """
        paths = list(kwpath)
        
        print(f"[INFO] Attempting to import '{paths}' to server '#{ctx.message.guild.name}'")
        # await
        slack_dir = parse_slack_directory(paths[0])
        if not slack_dir:
            print(f"[ERROR] Failed to parse slack directory")
            return

        for path in paths[1:]:
            # await
            slack_dir_2 = parse_slack_directory(path)
            for k, v in slack_dir_2["history"].items():
                slack_dir["history"][k] = slack_dir["history"].get(k,[]) + v
        messages = await import_slack_directory(ctx, slack_dir["root"], slack_dir, messages={})

    @bot.command(pass_context=True)
    async def import_here(ctx, *kwpath):
        """
        Attempts to import .json files from the specified path (relative to the bot) to the channel from which the command is invoked.
        Multiple paths can be passed, in which case the corresponding files will be imported in order.
        Note that this will fail to reference channels that doesn't exist
        :param ctx:
        :param path:
        :return:
        """
        paths = list(kwpath)
        for path in paths:
            print(f"[INFO] Attempting to import '{path}' to channel '#{ctx.message.channel.name}'")
            # await
            slack_dir = parse_slack_directory(path)
            messages = await import_slack_directory(ctx, path, slack_dir, match_channel=False, messages={})


if __name__ == "__main__":
    check_optional_dependencies()
    token = ""
    for path in [f'{os.path.expanduser("~")}/.secrets/discord_token.txt', 'discord_token.txt']:
        if token == "":
            if os.path.isfile( path ):
                with open(path, "r") as f:
                    for line in f:
                        token = line.strip()
                if token == "":
                    print(f"Found {path} but it's empty")
                else:
                    print(f"Loaded token from {path}")
            else:
                print(f"Couldn't find {path}")

    # FIXME: needs exception handling and expansion of "~"
    if token == "":
        input("Enter bot token: ")
        f = open("~/.secrets/discord_token.txt", "a")
        f.write(token)
        f.close()
        print("Saved token to ~/.secrets/discord_token.txt")

    intents = discord.Intents.default()
    intents.members = True
    if discord.__version__[0] >= "2":
        intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    register_commands()
    bot.run(token, reconnect=True)

