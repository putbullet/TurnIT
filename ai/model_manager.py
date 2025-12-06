"""
AI Models Manager for TurnIT
Handles loading and managing all AI models for offline operation
"""

import os
import sys
import torch
import numpy as np
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add utils to path for logger import
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)

class AIModelsManager:
    """Manages all AI models for TurnIT application"""
    
    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
        self.models = {}
        self.processors = {}
        self.loaded_models = set()
        
        # Check device availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

    def load_whisper_model(self) -> bool:
        """Load Whisper speech-to-text model"""
        try:
            if "whisper" in self.loaded_models:
                return True
            
            logger.info("Loading Whisper model...")
            
            from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
            import torch
            
            model_path = self.models_dir / "whisper"
            # Use smaller model for better compatibility
            model_name = "openai/whisper-small"
            
            # Load processor and model separately (no pipeline)
            self.processors["whisper"] = AutoProcessor.from_pretrained(
                model_name,
                cache_dir=str(model_path)
            )
            
            self.models["whisper"] = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_name,
                cache_dir=str(model_path),
                torch_dtype=torch.float32,  # Use float32 for CPU compatibility
                low_cpu_mem_usage=True,
                use_safetensors=True
            ).to("cpu")  # Force CPU for stability
            
            self.loaded_models.add("whisper")
            logger.info("Whisper model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            return False

    def load_qwen_audio_model(self) -> bool:
        """Load Qwen Audio model as fallback"""
        try:
            if "qwen_audio" in self.loaded_models:
                return True
            
            logger.info("Loading Qwen Audio model...")
            
            from transformers import AutoProcessor, AutoModelForSeq2SeqLM
            
            model_path = self.models_dir / "qwen_audio"
            
            # Load processor
            self.processors["qwen_audio"] = AutoProcessor.from_pretrained(
                "Qwen/Qwen2-Audio-7B-Instruct",
                cache_dir=str(model_path),
                local_files_only=True
            )
            
            # Load model
            self.models["qwen_audio"] = AutoModelForSeq2SeqLM.from_pretrained(
                "Qwen/Qwen2-Audio-7B-Instruct",
                cache_dir=str(model_path),
                local_files_only=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map=self.device
            )
            
            self.loaded_models.add("qwen_audio")
            logger.info("Qwen Audio model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Qwen Audio model: {str(e)}")
            return False

    def load_vit_model(self) -> bool:
        """Load Vision Transformer model for image feature extraction"""
        try:
            if "vit" in self.loaded_models:
                return True
            
            logger.info("Loading ViT model...")
            
            from transformers import AutoImageProcessor, AutoModel
            
            model_path = self.models_dir / "vit"
            model_name = "google/vit-base-patch16-224-in21k"
            
            # Load processor (allow download if not cached)
            self.processors["vit"] = AutoImageProcessor.from_pretrained(
                model_name,
                cache_dir=str(model_path)
            )
            
            # Load model (allow download if not cached)
            self.models["vit"] = AutoModel.from_pretrained(
                model_name,
                cache_dir=str(model_path),
                torch_dtype=torch.float32  # ViT typically uses float32
            ).to(self.device)
            
            self.loaded_models.add("vit")
            logger.info("ViT model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load ViT model: {str(e)}")
            return False

    def load_all_models(self) -> Dict[str, bool]:
        """Load all models and return status"""
        results = {}
        
        # Load Whisper (primary speech model)
        results["whisper"] = self.load_whisper_model()
        
        # Load ViT (image features)
        results["vit"] = self.load_vit_model()
        
        # Optionally load Qwen Audio (only if needed)
        # results["qwen_audio"] = self.load_qwen_audio_model()
        
        return results

    def transcribe_audio(self, audio_data, sample_rate: int = 16000, language: str = "en") -> str:
        """Transcribe audio using Whisper model"""
        try:
            if "whisper" not in self.loaded_models:
                if not self.load_whisper_model():
                    raise Exception("Failed to load Whisper model")
            
            processor = self.processors["whisper"]
            model = self.models["whisper"]
            
            # Ensure audio is the right format for Whisper
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)  # Convert to mono if stereo
            
            # Check if audio has content
            audio_power = np.mean(audio_data ** 2)
            logger.info(f"Audio power: {audio_power:.6f}, length: {len(audio_data)/16000:.2f}s")
            
            if audio_power < 1e-6:
                return "No audio detected. Please speak louder or check your microphone."
            
            # Resample if needed (Whisper expects 16kHz)
            if sample_rate != 16000:
                try:
                    import librosa
                    audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
                except ImportError:
                    logger.warning("librosa not available, assuming audio is already 16kHz")
            
            # Process audio using the processor (avoid pipeline completely)
            inputs = processor(
                audio_data,
                sampling_rate=16000,
                return_tensors="pt"
            )
            
            # Move inputs to device
            input_features = inputs["input_features"].to("cpu")
            
            # Generate transcription with specific parameters
            with torch.no_grad():
                predicted_ids = model.generate(
                    input_features,
                    max_new_tokens=224,  # Reduced to stay within model limits
                    num_beams=1,
                    do_sample=False,
                    temperature=0.0,
                    use_cache=True
                )
            
            # Decode transcription
            transcription = processor.batch_decode(
                predicted_ids, 
                skip_special_tokens=True
            )[0]
            
            logger.info(f"Audio transcribed successfully: {len(transcription)} characters")
            return transcription.strip()
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {str(e)}")
            # Return the actual error for debugging, but make it user-friendly
            error_msg = str(e)
            if "max_target_positions" in error_msg:
                return "Audio too long for processing. Please try a shorter recording."
            elif "CUDA" in error_msg or "device" in error_msg:
                return "GPU processing error. Please restart the application."
            elif "memory" in error_msg.lower():
                return "Insufficient memory for processing. Please try a shorter audio clip."
            else:
                return f"Transcription failed: {error_msg}"

    def _transcribe_with_fallback(self, audio_data, sample_rate: int, language: str) -> str:
        """Fallback transcription using Qwen Audio model"""
        try:
            if "qwen_audio" not in self.loaded_models:
                if not self.load_qwen_audio_model():
                    return "Transcription failed - no models available"
            
            processor = self.processors["qwen_audio"]
            model = self.models["qwen_audio"]
            
            # Process with Qwen
            inputs = processor(
                audio_data,
                sampling_rate=sample_rate,
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                outputs = model.generate(**inputs, max_length=512)
            
            transcription = processor.batch_decode(outputs, skip_special_tokens=True)[0]
            
            logger.info("Audio transcribed using fallback model")
            return transcription.strip()
            
        except Exception as e:
            logger.error(f"Fallback transcription also failed: {str(e)}")
            return "Transcription failed"

    def extract_image_features(self, image) -> Dict[str, Any]:
        """Extract features from image using ViT model"""
        try:
            if "vit" not in self.loaded_models:
                if not self.load_vit_model():
                    raise Exception("Failed to load ViT model")
            
            processor = self.processors["vit"]
            model = self.models["vit"]
            
            # Process image
            inputs = processor(images=image, return_tensors="pt").to(self.device)
            
            # Extract features
            with torch.no_grad():
                outputs = model(**inputs)
                
                # Get last hidden states (feature embeddings)
                features = outputs.last_hidden_state
                
                # Get pooled output for classification
                pooled_output = outputs.pooler_output if hasattr(outputs, 'pooler_output') else None
                
                # Convert to CPU and numpy for easier handling
                feature_vector = features.mean(dim=1).cpu().numpy().flatten()
                
                results = {
                    "feature_vector": feature_vector.tolist(),
                    "feature_dimensions": feature_vector.shape[0],
                    "model_used": "google/vit-base-patch16-224-in21k",
                    "pooled_features": pooled_output.cpu().numpy().flatten().tolist() if pooled_output is not None else None
                }
                
                logger.info(f"Image features extracted: {results['feature_dimensions']} dimensions")
                return results
                
        except Exception as e:
            logger.error(f"Image feature extraction failed: {str(e)}")
            return {
                "error": str(e),
                "feature_vector": [],
                "feature_dimensions": 0
            }

    def get_model_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about loaded models"""
        info = {}
        
        for model_name in ["whisper", "qwen_audio", "vit"]:
            info[model_name] = {
                "loaded": model_name in self.loaded_models,
                "device": self.device if model_name in self.loaded_models else "not_loaded"
            }
        
        return info

    def unload_model(self, model_name: str) -> bool:
        """Unload a specific model to free memory"""
        try:
            if model_name in self.loaded_models:
                if model_name in self.models:
                    del self.models[model_name]
                if model_name in self.processors:
                    del self.processors[model_name]
                
                self.loaded_models.discard(model_name)
                
                # Clear GPU cache if using CUDA
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                logger.info(f"Model {model_name} unloaded successfully")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unload model {model_name}: {str(e)}")
            return False

    def unload_all_models(self):
        """Unload all models to free memory"""
        for model_name in list(self.loaded_models):
            self.unload_model(model_name)
        
        # Final cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("All models unloaded")
