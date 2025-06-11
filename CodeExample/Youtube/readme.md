ComfyUI進行Youtube上傳範例工作流  
基本操作流程請參考PPT內容  
注意內容是有預設播放清單功能，所以你必須要建立播放清單


Set up OAuth for a YouTube desktop application, you'll need to create a project in the Google Cloud Console, enable the relevant APIs, and obtain credentials. Specifically, you'll need to create an OAuth client ID for a "Desktop app" type and enable the YouTube Data API.   
Here's a more detailed breakdown:  
1. Create a Google Cloud Console Project:   
Log in to the Google Cloud Console.  
Create a new project or select an existing one.   
2. Enable the YouTube Data API:  
In the Cloud Console, navigate to the "APIs & Services" dashboard.  
Enable the "YouTube Data API".   
3. Create OAuth Credentials:  
Go to "APIs & Services" -> "Credentials".  
Click "Create Credentials" and select "OAuth client ID".  
Choose the "Desktop app" application type.  
Give your application a name.  
Click "Create". Note down the "Json file" for later use.   
4.Copy this JSON file into the ComfyUI directory—the same folder where run_nvidia_gpu.bat is located—and rename it to credentials.json.  
Copy yt.py into the same folder, then run it by executing python yt.py. This will generate a token.json file, which serves as your local authentication key.  
5.If running yt.py fails, try installing the required library by running pip install google-auth-oauthlib.  
During execution, your browser will open a Google login page—this is normal and indicates the script is running correctly.  
6.You need the FillNodes node. Since the logic of each Code node can differ, this setup uses FillNodes for completion. After installing it, simply import my workflow to proceed.  
7.You need to create a YouTube channel and a playlist. Then, enter the playlist ID into the playlist parameter.  
