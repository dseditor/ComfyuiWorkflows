換衣服的Frontend介紹  

https://huggingface.co/dseditor/FLUXFillGGUF/blob/main/ComfyUI_FLUXTryon.zip
完整配置包，啟動run.bat就可以。

==
自行配置說明 (補充中)   
在ComfyUI目錄下執行Frontend.bat，注意先要安裝gradio (.\python_embeded\python.exe -s -m pip install gradio)  
comfyui-launcher.py，用以檢查模型以及啟動Gradio前端，包括T5以及Fill模型。  
gradiotw.py 換衣服前端介面  
TryOnsimpleAPI.json 換衣服的API  
【FluxTool】TryOnsimple.json 工作流本體  
所有檔案放在與run_nvidia_gpu.bat同一資料夾下。
先開啟工作流本體insall missing nodes，確保工作流可運作後再執行前端  
確認自己有以下兩個檔案在模型與CLIP底下，這兩個會自動下載到正確的位置。  
https://huggingface.co/dseditor/FLUXFillGGUF/resolve/main/flux1-fill-dev-Q8_0.gguf    
https://huggingface.co/city96/t5-v1_1-xxl-encoder-gguf/resolve/main/t5-v1_1-xxl-encoder-Q8_0.gguf    
Lora部分  
/ComfyUI/models/lora  
CatVitonLora：  
https://huggingface.co/xiaozaa/catvton-flux-lora-alpha/resolve/main/pytorch_lora_weights.safetensors  
AliFLUXTurbolora:  
https://huggingface.co/alimama-creative/FLUX.1-Turbo-Alpha/blob/main/diffusion_pytorch_model.safetensors  

