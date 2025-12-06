"""
App Setup Utility for TurnIT
Handles automatic model downloads, dependency installation, and offline preparation
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional
import json

class AppSetup:
    """Handles application setup including model downloads and dependency checks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.app_root = Path(__file__).parent.parent
        self.models_dir = self.app_root / "models"
        self.cache_dir = self.app_root / "cache"
        
        # Ensure directories exist
        self.models_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Model configurations
        self.models_config = {
            "whisper": {
                "name": "openai/whisper-large-v3",
                "path": self.models_dir / "whisper",
                "type": "speech_recognition",
                "size_gb": 3.1
            },
            "qwen_audio": {
                "name": "Qwen/Qwen2-Audio-7B-Instruct",
                "path": self.models_dir / "qwen_audio",
                "type": "speech_recognition_fallback",
                "size_gb": 14.5
            },
            "vit": {
                "name": "google/vit-base-patch16-224-in21k",
                "path": self.models_dir / "vit",
                "type": "image_features",
                "size_gb": 0.33
            }
        }
        
        # Required packages
        self.required_packages = [
            "torch", "transformers", "PySide6", "librosa", 
            "soundfile", "numpy", "requests", "pyaudio", 
            "pyttsx3", "sounddevice", "Pillow", "tqdm"
        ]
        
        self.setup_status = {
            "dependencies_installed": False,
            "models_downloaded": False,
            "setup_complete": False
        }
        
        self.load_setup_status()
    
    def load_setup_status(self):
        """Load setup status from cache"""
        status_file = self.cache_dir / "setup_status.json"
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    self.setup_status.update(json.load(f))
            except Exception as e:
                self.logger.warning(f"Could not load setup status: {e}")
    
    def save_setup_status(self):
        """Save setup status to cache"""
        status_file = self.cache_dir / "setup_status.json"
        try:
            with open(status_file, 'w') as f:
                json.dump(self.setup_status, f)
        except Exception as e:
            self.logger.error(f"Could not save setup status: {e}")
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        missing_packages = []
        
        for package in self.required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.logger.info(f"Missing packages: {missing_packages}")
            return False
        
        self.logger.info("All dependencies are installed")
        self.setup_status["dependencies_installed"] = True
        return True
    
    def install_dependencies(self) -> bool:
        """Install missing dependencies"""
        try:
            self.logger.info("Installing required dependencies...")
            
            # Get the requirements file path
            requirements_file = self.app_root / "requirements.txt"
            
            if not requirements_file.exists():
                self.logger.error("requirements.txt not found")
                return False
            
            # Install packages
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Dependencies installed successfully")
                self.setup_status["dependencies_installed"] = True
                self.save_setup_status()
                return True
            else:
                self.logger.error(f"Failed to install dependencies: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing dependencies: {e}")
            return False
    
    def check_models(self) -> Dict[str, bool]:
        """Check which models are already downloaded"""
        model_status = {}
        
        for model_key, config in self.models_config.items():
            model_path = config["path"]
            
            # Check if model directory exists and has content
            if model_path.exists() and any(model_path.iterdir()):
                # Check for key model files
                has_config = (model_path / "config.json").exists()
                has_model_files = any(
                    f.suffix in ['.bin', '.safetensors', '.pt', '.pth'] 
                    for f in model_path.rglob('*')
                )
                
                model_status[model_key] = has_config and has_model_files
            else:
                model_status[model_key] = False
        
        return model_status
    
    def download_model(self, model_key: str, progress_callback=None) -> bool:
        """Download a specific model"""
        if model_key not in self.models_config:
            self.logger.error(f"Unknown model: {model_key}")
            return False
        
        config = self.models_config[model_key]
        model_name = config["name"]
        model_path = config["path"]
        
        try:
            self.logger.info(f"Downloading model: {model_name}")
            
            # Import transformers here to ensure it's installed
            from transformers import AutoConfig, AutoModel, AutoProcessor
            from transformers import AutoModelForSpeechSeq2Seq, AutoImageProcessor
            
            # Create model directory
            model_path.mkdir(parents=True, exist_ok=True)
            
            # Download based on model type
            if model_key == "whisper":
                # Download Whisper model
                processor = AutoProcessor.from_pretrained(
                    model_name, 
                    cache_dir=str(model_path)
                )
                model = AutoModelForSpeechSeq2Seq.from_pretrained(
                    model_name, 
                    cache_dir=str(model_path)
                )
                
                # Save locally
                processor.save_pretrained(str(model_path))
                model.save_pretrained(str(model_path))
                
            elif model_key == "qwen_audio":
                # Download Qwen Audio model
                processor = AutoProcessor.from_pretrained(
                    model_name, 
                    cache_dir=str(model_path)
                )
                # Note: This is a large model, might need special handling
                model = AutoModel.from_pretrained(
                    model_name, 
                    cache_dir=str(model_path)
                )
                
                # Save locally
                processor.save_pretrained(str(model_path))
                model.save_pretrained(str(model_path))
                
            elif model_key == "vit":
                # Download ViT model
                processor = AutoImageProcessor.from_pretrained(
                    model_name, 
                    cache_dir=str(model_path)
                )
                model = AutoModel.from_pretrained(
                    model_name, 
                    cache_dir=str(model_path)
                )
                
                # Save locally
                processor.save_pretrained(str(model_path))
                model.save_pretrained(str(model_path))
            
            if progress_callback:
                progress_callback(f"Downloaded {model_name} successfully")
            
            self.logger.info(f"Successfully downloaded {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading {model_name}: {e}")
            return False
    
    def download_all_models(self, progress_callback=None) -> bool:
        """Download all required models"""
        model_status = self.check_models()
        models_to_download = [k for k, v in model_status.items() if not v]
        
        if not models_to_download:
            self.logger.info("All models already downloaded")
            self.setup_status["models_downloaded"] = True
            return True
        
        total_models = len(models_to_download)
        
        for i, model_key in enumerate(models_to_download):
            if progress_callback:
                progress_callback(f"Downloading model {i+1}/{total_models}: {model_key}")
            
            if not self.download_model(model_key, progress_callback):
                self.logger.error(f"Failed to download {model_key}")
                return False
        
        self.setup_status["models_downloaded"] = True
        self.save_setup_status()
        return True
    
    def get_setup_requirements(self) -> Dict:
        """Get setup requirements info"""
        model_status = self.check_models()
        
        total_size = sum(
            config["size_gb"] for key, config in self.models_config.items()
            if not model_status.get(key, False)
        )
        
        return {
            "dependencies_needed": not self.setup_status["dependencies_installed"],
            "models_needed": not all(model_status.values()),
            "total_download_size_gb": total_size,
            "models_status": model_status,
            "models_to_download": [
                k for k, v in model_status.items() if not v
            ]
        }
    
    def is_setup_complete(self) -> bool:
        """Check if complete setup is done"""
        if not self.setup_status.get("dependencies_installed", False):
            return False
        
        model_status = self.check_models()
        if not all(model_status.values()):
            return False
        
        self.setup_status["setup_complete"] = True
        self.save_setup_status()
        return True
    
    def get_model_path(self, model_key: str) -> Optional[Path]:
        """Get local path for a model"""
        if model_key in self.models_config:
            return self.models_config[model_key]["path"]
        return None
    
    def cleanup(self):
        """Clean up application setup resources"""
        try:
            # Save current setup status
            self.save_setup_status()
            self.logger.info("AppSetup cleanup completed")
        except Exception as e:
            self.logger.error(f"AppSetup cleanup error: {str(e)}")
