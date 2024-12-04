import gradio as gr
import json
import requests
import os
import shutil
from PIL import Image
import time
from datetime import datetime, timedelta
import glob

# ComfyUI API endpoint
COMFY_API_URL = "http://127.0.0.1:8188"
INPUT_DIR = "ComfyUI/input"
OUTPUT_DIR = "ComfyUI/output"

def ensure_dirs():
    """Ensure input and output directories exist"""
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_latest_image():
    """Get the latest image from the output directory"""
    # Look for both .png and .jpg files
    pattern = os.path.join(OUTPUT_DIR, '*.*')
    files = glob.glob(pattern)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        return None
        
    # Get the most recent file
    latest_file = max(image_files, key=os.path.getctime)
    
    # Check if the file was created in the last minute
    file_creation_time = datetime.fromtimestamp(os.path.getctime(latest_file))
    if datetime.now() - file_creation_time < timedelta(minutes=1):
        return latest_file
    
    return None

def save_uploaded_file(temp_path, filename):
    """Save uploaded file to ComfyUI input directory"""
    if temp_path is None:
        return None
        
    ensure_dirs()
    save_path = os.path.join(INPUT_DIR, filename)
    
    try:
        img = Image.open(temp_path)
        img = img.convert('RGB')
        img.save(save_path, 'JPEG')
        return save_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def process_uploads(clothes_path, people_path):
    """Process uploaded files and return status"""
    if not clothes_path or not people_path:
        return "請上傳衣服圖片和人物圖片 (Please upload both clothes and person images)"
    
    clothes_saved = save_uploaded_file(clothes_path, "clothes.jpg")
    people_saved = save_uploaded_file(people_path, "people.jpg")
    
    if clothes_saved and people_saved:
        return "圖片上傳成功！(Images uploaded successfully!)"
    else:
        return "圖片上傳失敗 (Image upload failed)"

def wait_for_generation(prompt_id):
    """Wait for generation to complete and return status"""
    max_attempts = 120  # Increased maximum wait time to 120 seconds
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{COMFY_API_URL}/history/{prompt_id}")
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    # Check if the generation is complete
                    if 'outputs' in history[prompt_id]:
                        time.sleep(2)  # Add a small delay to ensure file is written
                        return True
                    # Check for execution status
                    if 'executing' in history[prompt_id] and not history[prompt_id]['executing']:
                        time.sleep(2)  # Add a small delay to ensure file is written
                        return True
            time.sleep(1)
            attempt += 1
        except Exception as e:
            print(f"Error checking status: {e}")
            time.sleep(1)
            attempt += 1
    
    return False

def generate_image(clothes_path, people_path):
    """Generate image using ComfyUI API"""
    if not clothes_path or not people_path:
        return None, "請先上傳衣服圖片和人物圖片 (Please upload clothes and person images first)"
    
    # Process uploads first
    upload_status = process_uploads(clothes_path, people_path)
    if "成功" not in upload_status:
        return None, upload_status
    
    try:
        # Load workflow API
        with open("TryOnsimpleAPI.json", "r") as f:
            workflow = json.load(f)
        
        # Queue the prompt
        p = {"prompt": workflow}
        response = requests.post(f"{COMFY_API_URL}/prompt", json=p)
        
        if response.status_code != 200:
            return None, "生成請求發送失敗 (Generation request failed)"
        
        prompt_id = response.json()['prompt_id']
        
        # Wait for generation to complete
        generation_success = wait_for_generation(prompt_id)
        
        # Additional delay to ensure file system updates
        time.sleep(3)
        
        # Get latest generated image
        latest_image = get_latest_image()
        
        if latest_image:
            try:
                output_img = Image.open(latest_image)
                return output_img, "圖片生成成功！(Image generated successfully!)"
            except Exception as e:
                return None, f"輸出圖片載入失敗 (Output image loading failed)：{str(e)}"
        else:
            if generation_success:
                # If generation was successful but image not found, try one more time
                time.sleep(2)
                latest_image = get_latest_image()
                if latest_image:
                    output_img = Image.open(latest_image)
                    return output_img, "圖片生成成功！(Image generated successfully!)"
            
            return None, "未找到生成的圖片 (Generated image not found)"
            
    except Exception as e:
        return None, f"生成過程出錯 (Generation process error)：{str(e)}"

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft()) as app:
    gr.Markdown("# FLUX虛擬試衣系統 (Virtual Try-On System)")
    
    with gr.Row():
        # Input Section
        with gr.Column(scale=1):
            gr.Markdown("## 輸入圖片 (Input Images)")
            with gr.Row():
                with gr.Column():
                    clothes_input = gr.Image(
                        label="衣服圖片 (Clothes)",
                        type="filepath",
                        height=300,
                        image_mode="RGB"
                    )
                
                with gr.Column():
                    people_input = gr.Image(
                        label="人物圖片 (Person)",
                        type="filepath",
                        height=300,
                        image_mode="RGB"
                    )
            
            generate_button = gr.Button(
                "開始生成 (Start Generation)",
                variant="primary",
                size="lg"
            )
        
        # Output Section
        with gr.Column(scale=1):
            gr.Markdown("## 生成結果 (Generation Results)")
            output_image = gr.Image(
                label="預覽結果 (Preview)",
                height=600,
                image_mode="RGB"
            )
            output_text = gr.Textbox(
                label="生成狀態 (Generation Status)",
                interactive=False
            )
    
    # Set up generation event
    generate_button.click(
        generate_image,
        inputs=[clothes_input, people_input],
        outputs=[output_image, output_text]
    )

if __name__ == "__main__":
    app.launch()
