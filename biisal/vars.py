# (c) adarsh-goel (c) @biisal
import os
from os import getenv, environ
from dotenv import load_dotenv



load_dotenv()
bot_name = "Bɪɪsᴀʟ Fɪʟᴇ2Lɪɴᴋ Bᴏᴛ"
bisal_channel = "https://telegram.me/bots_up"
bisal_grp = "https://t.me/isko_join_nhi_kya_toh_kya_kiya"

class Var(object):
    MULTI_CLIENT = False
    API_ID = int(getenv('API_ID', '24503270'))
    API_HASH = str(getenv('API_HASH', '53b04d58c085c3136ceda8036ee9a1da'))
    BOT_TOKEN = str(getenv('BOT_TOKEN' , '7129593614:AAH4gC-EYtC1icnfOiUWsuR4aP6YAx0FA4s'))
    name = str(getenv('name', 'File_Press_bot'))
    SLEEP_THRESHOLD = int(getenv('SLEEP_THRESHOLD', '60'))
    WORKERS = int(getenv('WORKERS', '4'))
    BIN_CHANNEL = int(getenv('BIN_CHANNEL', '-1001720210775'))
    NEW_USER_LOG = int(getenv('NEW_USER_LOG', '-1001720210775'))
    PORT = int(getenv('PORT', '9097'))
    BIND_ADRESS = str(getenv('WEB_SERVER_BIND_ADDRESS', '0.0.0.0'))
    PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
    OWNER_ID = [int(x) for x in os.environ.get("OWNER_ID", "6133440326").split()]
    NO_PORT = bool(getenv('NO_PORT', False))
    APP_NAME = None
    OWNER_USERNAME = str(getenv('OWNER_USERNAME', 'Attitude2688'))
    if 'DYNO' in environ:
        ON_HEROKU = True
        APP_NAME = str(getenv('APP_NAME')) #dont need to fill anything here
    
    else:
        ON_HEROKU = False
    FQDN = str(getenv('FQDN', 'BIND_ADRESS:PORT')) if not ON_HEROKU or getenv('FQDN', '') else APP_NAME+'.herokuapp.com'
    HAS_SSL=bool(getenv('HAS_SSL',True))
    if HAS_SSL:
        URL = "https://{}/".format(FQDN)
    else:
        URL = "http://{}/".format(FQDN)  
    DATABASE_URL = str(getenv('DATABASE_URL', 'mongodb+srv://abdulmk184:abdulmk18@cluster0.fv4ffn1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'))
    UPDATES_CHANNEL = str(getenv('UPDATES_CHANNEL', 'bots_up')) 
    BANNED_CHANNELS = list(set(int(x) for x in str(getenv("BANNED_CHANNELS", "")).split()))   
    BAN_CHNL = list(set(int(x) for x in str(getenv("BAN_CHNL", "")).split())) 
    BAN_ALERT = str(getenv('BAN_ALERT' , '<b>ʏᴏᴜʀ ᴀʀᴇ ʙᴀɴɴᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.Pʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ @biisal_bot ᴛᴏ ʀᴇsᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇ!!</b>'))
    DB_URI = str(getenv('DB_URI', 'mongodb+srv://abdulmk184:abdulmk18@cluster0.fv4ffn1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'))
    DB_NAME = str(getenv("DB_NAME", "Khalik"))
    SECOND_BOTUSERNAME = str(getenv("SECOND_BOTUSERNAME", "File_Sender_oBot"))
    FILE_BOT_TOKEN = str(getenv('FILE_BOT_TOKEN', '7523273025:AAH4S11te27oeOouFOhi64xdaCZyBUnXQvg'))
