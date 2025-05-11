import os

class Config(object):
     
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "6631772048:AAF4AoHOssXJqYMee6oJ_e2C9onB555GipE")
    API_ID = int(os.environ.get("API_ID", "27752560" ))
    API_HASH = os.environ.get("API_HASH", "67d3ec64db8031189962b5d4804884c0")
    #Add your channel id. For force Subscribe.
    CHANNEL = os.environ.get("CHANNEL", "-1002589776901")
    #Skip or add your proxy from https://github.com/rg3/youtube-dl/issues/1091#issuecomment-230163061
    HTTP_PROXY = ''
