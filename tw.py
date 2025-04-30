# from twilio.rest import Client

# account_sid = 'AC82d4df645ea7161b060e97d44de1ab73'
# auth_token = 'bcac4174e0e34ec54789118adad89aaf'
# client = Client(account_sid, auth_token)

# message = client.messages.create(
#   from_='whatsapp:+14155238886',
#   content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
#   content_variables='{"1":"Paras","2":"Majethiya"}',
#   to='whatsapp:+916355370464'
# )

# print(message.sid)

from twilio.rest import Client

account_sid = 'AC82d4df645ea7161b060e97d44de1ab73'
auth_token = 'bcac4174e0e34ec54789118adad89aaf'
client = Client(account_sid, auth_token)

message = client.messages.create(
    body="Hello there!",
    from_="whatsapp:+14155238886",
    to="whatsapp:+916355370464",
)

print(message.body)