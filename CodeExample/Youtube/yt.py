# 重新授權腳本（執行一次即可）
from google_auth_oauthlib.flow import InstalledAppFlow

# 擴大授權範圍
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube'  # 包含播放清單權限
]

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=8080)

# 覆蓋舊的 token.json
with open('token.json', 'w') as token:
    token.write(creds.to_json())

print("重新授權完成！")