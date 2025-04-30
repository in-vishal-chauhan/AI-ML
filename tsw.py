import requests

TWILIO_SID = "AC82d4df645ea7161b060e97d44de1ab73"
TWILIO_AUTH_TOKEN = "fb15c0011812bfa450ccc7b06221ed0a"
MEDIA_URL = "https://api.twilio.com/2010-04-01/Accounts/AC82d4df645ea7161b060e97d44de1ab73/Messages/MM0e9eae9793f11a00ea6560aad9c2b282/Media/ME5c49a95886b2a513221f22d98222082d"

response = requests.get(MEDIA_URL, auth=(TWILIO_SID, TWILIO_AUTH_TOKEN))

print("Status:", response.status_code)
if response.status_code == 200:
    with open("test_audio.ogg", "wb") as f:
        f.write(response.content)
    print("Download successful: test_audio.ogg")
else:
    print("Failed to download:", response.text)
