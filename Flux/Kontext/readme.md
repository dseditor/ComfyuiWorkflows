Kontext的工作流整合  
BasicLLM，基礎連接LLM的做法  
Rendering，室內線稿繪製的示範  
OutPaint，OutPaint的示範   
使用的節點(目前需要自行GitClone到Custom_nodes下，才會出現FLUXKontext範本)，作者還沒有推送版本更新到Manager   
[OllamaGemini](https://github.com/al-swaiti/ComfyUI-OllamaGemini)    
如果你已經安裝了現有的版本，而沒有看到正確的節點內容(沒有FLUXKontext範本)，可能是因為節點在Manager上還沒有更新，你需要手動更新節點，更新方法如下：

```bash
CD custom_nodes
#切換到ComfyUI的custom_nodes資料夾下
CD ComfyUI-OllamaGemini
#切換到OllamaGemini節點資料夾下
git pull
#拉取最新更新
