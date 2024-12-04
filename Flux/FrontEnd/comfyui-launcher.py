import os
import sys
import subprocess
import requests
import webbrowser
import time
from pathlib import Path
import socket
from urllib.error import URLError
import urllib.request
import threading
import queue
import re
import psutil
import win32job
import win32api
import win32con
import atexit

def create_job_object():
    """Create a job object to manage child processes"""
    job = win32job.CreateJobObject(None, "")
    extended_info = win32job.QueryInformationJobObject(
        job, win32job.JobObjectExtendedLimitInformation)
    extended_info['BasicLimitInformation']['LimitFlags'] = (
        win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    )
    win32job.SetInformationJobObject(
        job, win32job.JobObjectExtendedLimitInformation, extended_info)
    return job

def assign_to_job_object(job, process):
    """Assign a process to the job object"""
    try:
        win32job.AssignProcessToJobObject(job, process._handle)
    except Exception as e:
        print(f"Failed to assign process to job object: {e}")

class ComfyUIProcess:
    def __init__(self, job):
        self.process = None
        self.output_queue = queue.Queue()
        self.is_running = False
        self.job = job

    def _stream_output(self, pipe, queue):
        try:
            for line in iter(pipe.readline, b''):
                try:
                    decoded_line = line.decode('utf-8', errors='replace').strip()
                    queue.put(decoded_line)
                except Exception as e:
                    queue.put(f"Decoding error: {str(e)}")
        except Exception as e:
            queue.put(f"Stream reading error: {str(e)}")
        finally:
            pipe.close()

    def start(self):
        comfyui_path = Path("ComfyUI/main.py")
        if not comfyui_path.exists():
            print("Error: ComfyUI/main.py not found")
            return False

        try:
            os.environ['BROWSER'] = 'none'
            
            self.process = subprocess.Popen(
                [sys.executable, str(comfyui_path), "--windows-standalone-build"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Assign process to job object
            assign_to_job_object(self.job, self.process)
            
            stdout_thread = threading.Thread(
                target=self._stream_output, 
                args=(self.process.stdout, self.output_queue)
            )
            stderr_thread = threading.Thread(
                target=self._stream_output, 
                args=(self.process.stderr, self.output_queue)
            )
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            
            self.is_running = True
            return True

        except Exception as e:
            print(f"Error starting ComfyUI: {e}")
            return False

    def stop(self):
        if self.process:
            self.process.terminate()
            self.is_running = False

class GradioProcess:
    def __init__(self, job):
        self.process = None
        self.job = job

    def start(self):
        gradio_path = Path("gradiotw.py")
        if not gradio_path.exists():
            print("Error: gradiotw.py not found")
            return False

        try:
            print("Starting Gradio...")
            os.environ['BROWSER'] = 'none'
            
            self.process = subprocess.Popen(
                [sys.executable, str(gradio_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Assign process to job object
            assign_to_job_object(self.job, self.process)

            time.sleep(3)
            print("Opening Gradio interface...")
            webbrowser.open('http://127.0.0.1:7860')
            
            return True

        except Exception as e:
            print(f"Error starting Gradio: {e}")
            return False

    def stop(self):
        if self.process:
            self.process.terminate()

def download_file(url, filepath):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filepath, 'wb') as file:
        if total_size == 0:
            file.write(response.content)
        else:
            downloaded = 0
            for data in response.iter_content(chunk_size=4096):
                downloaded += len(data)
                file.write(data)
                progress = int(50 * downloaded / total_size)
                sys.stdout.write(f"\rDownload progress: [{'=' * progress}{' ' * (50-progress)}] {downloaded}/{total_size} bytes")
                sys.stdout.flush()
    print("\nDownload complete!")

def check_and_download_models():
    base_path = Path("ComfyUI/models")
    
    unet_path = base_path / "unet"
    clip_path = base_path / "clip"
    unet_path.mkdir(parents=True, exist_ok=True)
    clip_path.mkdir(parents=True, exist_ok=True)
    
    flux_model = unet_path / "flux1-fill-dev-Q8_0.gguf"
    if not flux_model.exists():
        print("Downloading flux1-fill-dev-Q8_0.gguf...")
        flux_url = "https://huggingface.co/dseditor/FLUXFillGGUF/resolve/main/flux1-fill-dev-Q8_0.gguf"
        download_file(flux_url, flux_model)
    
    t5_model = clip_path / "t5-v1_1-xxl-encoder-Q8_0.gguf"
    if not t5_model.exists():
        print("Downloading t5-v1_1-xxl-encoder-Q8_0.gguf...")
        t5_url = "https://huggingface.co/city96/t5-v1_1-xxl-encoder-gguf/resolve/main/t5-v1_1-xxl-encoder-Q8_0.gguf"
        download_file(t5_url, t5_model)

def wait_for_comfyui_ready(timeout=300):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = urllib.request.urlopen('http://127.0.0.1:8188/history')
            if response.status == 200:
                print("ComfyUI API is ready!")
                return True
        except URLError:
            print("Waiting for ComfyUI to start...", end='\r')
            time.sleep(2)
    return False

def cleanup_processes():
    """Clean up any remaining Python processes"""
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Skip the current process
            if proc.info['pid'] == current_pid:
                continue
            # Kill any Python processes that might be related
            if 'python' in proc.info['name'].lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def main():
    # Register cleanup function
    atexit.register(cleanup_processes)
    
    # Create job object
    job = create_job_object()
    
    print("Starting model check and download...")
    check_and_download_models()
    
    # Start ComfyUI
    comfyui = ComfyUIProcess(job)
    print("\nStarting ComfyUI...")
    if not comfyui.start():
        print("ComfyUI failed to start")
        return
    
    # Wait for ComfyUI to be ready
    if not wait_for_comfyui_ready():
        print("ComfyUI startup timeout")
        comfyui.stop()
        return
    
    # Start Gradio
    gradio = GradioProcess(job)
    if gradio.start():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            gradio.stop()
            comfyui.stop()
    else:
        comfyui.stop()

if __name__ == "__main__":
    main()
