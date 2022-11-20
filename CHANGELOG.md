# https://github.com/rslavin/slack2discord/commit/4938c98292041b95210af0e544a4d61788c2c3c9
* use rich text embeds for hyperlinks
* reupload attachments to Discord rather than using Slack link, handling images and non-image attachments correctly
* mention channels correctly
* mention usernames better (including `@everyone`)
* when adding just one embed, use singular embed, so that it has a cleaner look
* fix some HTML entities in output - `&amp;` `&gt;` & `&lt;`
* messages are broken at the last available newline (still maximizing characters per message), rather than at character limit mid-word
* check bot token in `~/.secrets/discord_token.txt` and `./discord_token.txt`; if neither, prompt user and save bot token at the former

Combination of work by Yamiko & @saizai.

# 2022-11-20
* added changelog & expanded todo list
* used python library to convert all HTML entities in message
* moved `fill_references` to be within `parse_message`
* keep hash of messages to use in replies
* have bot reconnect
* fixed mentions in embeds
* cleaned up some duplicative code
* fixed erroneous warning about missing files
* allow blank message when there's embed or file
* allow messages of up to 6000 characters using multiple rich-text embeds (4096 char limit each)
