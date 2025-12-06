"""
Image Analysis UI for TurnIT
Image feature extraction and analysis interface
"""

import sys
import os
import json
import threading
from pathlib import Path
from typing import Optional, Dict, List

# Import PySide6 components
try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QTextEdit, QProgressBar,
        QFileDialog, QGroupBox, QFrame, QMessageBox, QScrollArea,
        QSlider, QSpinBox, QCheckBox, QListWidget, QListWidgetItem,
        QSplitter, QTableWidget, QTableWidgetItem
    )
    from PySide6.QtCore import Qt, QThread, Signal, QTimer
    from PySide6.QtGui import QFont, QIcon, QPixmap
except ImportError:
    print("PySide6 not installed. Installing...")

# Image processing imports
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import easyocr
    import pytesseract
except ImportError:
    # Set None for missing imports so we can handle gracefully
    cv2 = None
    np = None
    Image = None
    ImageDraw = None
    ImageFont = None
    plt = None
    patches = None
    FigureCanvas = None
    Figure = None
    easyocr = None
    pytesseract = None

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger
from utils.global_settings import GlobalSettings
from ai.model_manager import AIModelsManager

logger = get_logger(__name__)

class ImageProcessor:
    """Image processing and analysis utilities"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    def load_image(self, image_path):
        """Load image from file"""
        if Image is None:
            raise ImportError("PIL (Pillow) not installed. Please install: pip install pillow")
            
        try:
            # Load with PIL for compatibility
            pil_image = Image.open(image_path)
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            if np is None:
                raise ImportError("numpy not installed. Please install: pip install numpy")
            image_array = np.array(pil_image)
            
            logger.info(f"Image loaded: {image_path}, Shape: {image_array.shape}")
            return image_array, pil_image
            
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {str(e)}")
            return None, None
    
    def extract_basic_features(self, image_array):
        """Extract basic image features"""
        try:
            height, width = image_array.shape[:2]
            channels = image_array.shape[2] if len(image_array.shape) == 3 else 1
            
            # Color statistics
            if channels == 3:
                mean_rgb = np.mean(image_array, axis=(0, 1))
                std_rgb = np.std(image_array, axis=(0, 1))
                
                # Dominant colors (simplified)
                reshaped = image_array.reshape(-1, 3)
                unique_colors = np.unique(reshaped, axis=0)
                
                # Brightness and contrast
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
                brightness = np.mean(gray)
                contrast = np.std(gray)
            else:
                mean_rgb = [np.mean(image_array)]
                std_rgb = [np.std(image_array)]
                brightness = np.mean(image_array)
                contrast = np.std(image_array)
                unique_colors = np.unique(image_array)
            
            features = {
                'dimensions': {'width': int(width), 'height': int(height), 'channels': int(channels)},
                'file_size_pixels': int(width * height),
                'color_stats': {
                    'mean_rgb': [float(x) for x in mean_rgb],
                    'std_rgb': [float(x) for x in std_rgb],
                    'unique_colors': len(unique_colors),
                    'brightness': float(brightness),
                    'contrast': float(contrast)
                }
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            return None
    
    def detect_edges(self, image_array, low_threshold=50, high_threshold=150):
        """Detect edges using Canny edge detection"""
        try:
            # Convert to grayscale
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Canny edge detection
            edges = cv2.Canny(blurred, low_threshold, high_threshold)
            
            return edges
            
        except Exception as e:
            logger.error(f"Edge detection failed: {str(e)}")
            return None
    
    def create_histogram(self, image_array):
        """Create color histogram"""
        try:
            if len(image_array.shape) == 3:
                # RGB histogram
                colors = ['red', 'green', 'blue']
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
                
                # Individual channel histograms
                for i, color in enumerate(colors):
                    hist = cv2.calcHist([image_array], [i], None, [256], [0, 256])
                    ax1.plot(hist, color=color, alpha=0.7, linewidth=2)
                
                ax1.set_title('RGB Channel Histograms')
                ax1.set_xlabel('Pixel Intensity')
                ax1.set_ylabel('Frequency')
                ax1.legend(['Red', 'Green', 'Blue'])
                ax1.grid(True, alpha=0.3)
                
                # Combined grayscale histogram
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
                hist_gray = cv2.calcHist([gray], [0], None, [256], [0, 256])
                ax2.plot(hist_gray, color='gray', linewidth=2)
                ax2.set_title('Grayscale Histogram')
                ax2.set_xlabel('Pixel Intensity')
                ax2.set_ylabel('Frequency')
                ax2.grid(True, alpha=0.3)
                
            else:
                # Grayscale histogram only
                fig, ax = plt.subplots(1, 1, figsize=(8, 4))
                hist = cv2.calcHist([image_array], [0], None, [256], [0, 256])
                ax.plot(hist, color='gray', linewidth=2)
                ax.set_title('Grayscale Histogram')
                ax.set_xlabel('Pixel Intensity')
                ax.set_ylabel('Frequency')
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            logger.error(f"Histogram creation failed: {str(e)}")
            return None
    
    def extract_text_from_image(self, image_array):
        """Extract text from image using OCR"""
        try:
            ocr_results = {}
            
            # Try EasyOCR first (more modern)
            if easyocr is not None:
                try:
                    reader = easyocr.Reader(['en'])
                    results = reader.readtext(image_array)
                    
                    extracted_text = []
                    confidence_scores = []
                    bounding_boxes = []
                    
                    for (bbox, text, confidence) in results:
                        if confidence > 0.5:  # Filter low-confidence detections
                            extracted_text.append(text)
                            confidence_scores.append(confidence)
                            bounding_boxes.append(bbox)
                    
                    ocr_results['easyocr'] = {
                        'text': ' '.join(extracted_text),
                        'individual_texts': extracted_text,
                        'confidences': confidence_scores,
                        'bounding_boxes': bounding_boxes,
                        'total_words': len(extracted_text)
                    }
                    
                except Exception as e:
                    logger.warning(f"EasyOCR failed: {str(e)}")
                    ocr_results['easyocr'] = {'text': '', 'error': str(e)}
            
            # Try Tesseract as backup
            if pytesseract is not None:
                try:
                    # Convert numpy array to PIL Image for tesseract
                    if Image is not None:
                        pil_image = Image.fromarray(image_array)
                        text = pytesseract.image_to_string(pil_image)
                        
                        # Get detailed data
                        data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
                        
                        # Filter confident text
                        confident_words = []
                        for i, conf in enumerate(data['conf']):
                            if int(conf) > 30:  # Confidence threshold
                                word = data['text'][i].strip()
                                if word:
                                    confident_words.append(word)
                        
                        ocr_results['tesseract'] = {
                            'text': text.strip(),
                            'confident_words': confident_words,
                            'total_words': len(confident_words)
                        }
                        
                except Exception as e:
                    logger.warning(f"Tesseract failed: {str(e)}")
                    ocr_results['tesseract'] = {'text': '', 'error': str(e)}
            
            # Combine results
            if ocr_results:
                combined_text = ""
                if 'easyocr' in ocr_results and ocr_results['easyocr'].get('text'):
                    combined_text = ocr_results['easyocr']['text']
                elif 'tesseract' in ocr_results and ocr_results['tesseract'].get('text'):
                    combined_text = ocr_results['tesseract']['text']
                
                ocr_results['combined'] = {
                    'text': combined_text,
                    'has_text': bool(combined_text.strip())
                }
            
            return ocr_results
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return {'error': str(e), 'combined': {'text': '', 'has_text': False}}

class AnalysisThread(QThread):
    """Thread for handling image analysis"""
    analysis_complete = Signal(dict)
    error_occurred = Signal(str)
    progress_update = Signal(str)
    
    def __init__(self, image_path, models_manager, processor):
        super().__init__()
        self.image_path = image_path
        self.models_manager = models_manager
        self.processor = processor
    
    def run(self):
        """Run analysis in separate thread"""
        try:
            self.progress_update.emit("Loading image...")
            
            # Load image
            image_array, pil_image = self.processor.load_image(self.image_path)
            if image_array is None:
                self.error_occurred.emit("Failed to load image")
                return
            
            results = {
                'image_path': self.image_path,
                'image_array': image_array,
                'pil_image': pil_image
            }
            
            # Basic features
            self.progress_update.emit("Extracting basic features...")
            basic_features = self.processor.extract_basic_features(image_array)
            if basic_features:
                results['basic_features'] = basic_features
            
            # AI-based feature extraction
            if self.models_manager:
                self.progress_update.emit("Extracting AI features...")
                try:
                    ai_features = self.models_manager.extract_image_features(image_array)
                    results['ai_features'] = ai_features
                except Exception as e:
                    logger.error(f"AI feature extraction failed: {str(e)}")
                    results['ai_features'] = None
            
            # Edge detection
            self.progress_update.emit("Detecting edges...")
            edges = self.processor.detect_edges(image_array)
            if edges is not None:
                results['edges'] = edges
            
            # Histogram
            self.progress_update.emit("Creating histogram...")
            histogram_fig = self.processor.create_histogram(image_array)
            if histogram_fig is not None:
                results['histogram'] = histogram_fig
            
            # OCR - Text extraction
            self.progress_update.emit("Extracting text from image...")
            ocr_results = self.processor.extract_text_from_image(image_array)
            if ocr_results:
                results['ocr'] = ocr_results
            
            self.progress_update.emit("Analysis complete")
            self.analysis_complete.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class ImageAnalysisWindow(QMainWindow):
    """Image Analysis interface"""
    
    def __init__(self):
        super().__init__()
        self.current_language = GlobalSettings().get_language()
        self.processor = ImageProcessor()
        self.models_manager = None
        self.analysis_thread = None
        self.current_results = None
        
        # Load models
        self.init_models()
        self.init_ui()
        self.setup_connections()
        
        # Connect to global language changes
        GlobalSettings().language_changed.connect(self.on_language_changed)
    
    def init_models(self):
        """Initialize AI models manager (lazy loading)"""
        try:
            models_dir = Path(__file__).parent.parent / "models"
            self.models_manager = AIModelsManager(str(models_dir))
            # Don't load models immediately - load when needed
            logger.info("Models manager initialized (lazy loading)")
        except Exception as e:
            logger.error(f"Error initializing models manager: {str(e)}")
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("TurnIT - Image Analysis")
        self.setFixedSize(1200, 800)
        self.center_window()
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create sections
        self.create_header_section(main_layout)
        self.create_main_content(main_layout)
        self.create_actions_section(main_layout)
        
        self.apply_dark_theme()
    
    def create_header_section(self, layout):
        """Create header section"""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Image Analysis")
        title_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Progress info
        self.progress_label = QLabel("Ready")
        self.progress_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.progress_label)
        
        layout.addLayout(header_layout)
    
    def create_main_content(self, layout):
        """Create main content area"""
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 8px;
                background: #2a2a2a;
                height: 20px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00d4ff, stop: 1 #7b68ee);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Image display
        self.create_image_panel(main_splitter)
        
        # Right panel - Analysis results
        self.create_results_panel(main_splitter)
        
        # Set splitter proportions
        main_splitter.setSizes([400, 600])
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background: #404040;
                border: 1px solid #606060;
            }
            QSplitter::handle:horizontal {
                width: 3px;
            }
        """)
        
        layout.addWidget(main_splitter)
    
    def create_image_panel(self, parent):
        """Create image display panel"""
        image_widget = QWidget()
        image_layout = QVBoxLayout(image_widget)
        
        # Image display area
        image_group = QGroupBox("Image Preview")
        image_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 10px;
                margin: 10px 0;
                padding-top: 10px;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        image_group_layout = QVBoxLayout(image_group)
        
        # Image label
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(350, 300)
        self.image_label.setStyleSheet("""
            QLabel {
                background: #1a1a1a;
                border: 2px dashed #404040;
                border-radius: 10px;
                color: #808080;
                font-size: 16px;
            }
        """)
        self.image_label.setScaledContents(False)
        image_group_layout.addWidget(self.image_label)
        
        # Image info
        self.image_info_label = QLabel("")
        self.image_info_label.setStyleSheet("color: #808080; font-size: 12px;")
        self.image_info_label.setWordWrap(True)
        image_group_layout.addWidget(self.image_info_label)
        
        image_layout.addWidget(image_group)
        
        # Load image button
        load_btn = QPushButton("📁 Load Image")
        load_btn.setFixedHeight(40)
        load_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00d4ff, stop: 1 #7b68ee);
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00b8e6, stop: 1 #6a5bdb);
            }
        """)
        load_btn.clicked.connect(self.load_image)
        image_layout.addWidget(load_btn)
        
        parent.addWidget(image_widget)
    
    def create_results_panel(self, parent):
        """Create analysis results panel"""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Results tabs (using stacked widget simulation)
        self.results_tabs = QComboBox()
        self.results_tabs.addItems([
            "Basic Features", "AI Features", "Edge Detection", "Color Analysis", "Text Extraction (OCR)"
        ])
        self.results_tabs.setStyleSheet("""
            QComboBox {
                background: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #00d4ff;
            }
        """)
        self.results_tabs.currentTextChanged.connect(self.switch_results_tab)
        results_layout.addWidget(self.results_tabs)
        
        # Results display area
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        self.results_area.setStyleSheet("""
            QScrollArea {
                background: #1a1a1a;
                border: 2px solid #404040;
                border-radius: 10px;
            }
        """)
        
        # Results content widget
        self.results_content = QWidget()
        self.results_content.setStyleSheet("background: #1a1a1a;")
        self.results_layout = QVBoxLayout(self.results_content)
        
        # Default message
        self.no_results_label = QLabel("Load an image to see analysis results")
        self.no_results_label.setAlignment(Qt.AlignCenter)
        self.no_results_label.setStyleSheet("""
            QLabel {
                color: #808080;
                font-size: 16px;
                font-style: italic;
                padding: 50px;
            }
        """)
        self.results_layout.addWidget(self.no_results_label)
        
        self.results_area.setWidget(self.results_content)
        results_layout.addWidget(self.results_area)
        
        parent.addWidget(results_widget)
    
    def create_actions_section(self, layout):
        """Create action buttons section"""
        actions_layout = QHBoxLayout()
        
        # Analyze button
        self.analyze_btn = QPushButton("🔍 Analyze Image")
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setFixedHeight(40)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background: #404040;
                color: #808080;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 20px;
                padding: 0 30px;
            }
            QPushButton:enabled {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00d4ff, stop: 1 #7b68ee);
                color: white;
            }
            QPushButton:enabled:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00b8e6, stop: 1 #6a5bdb);
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_image)
        actions_layout.addWidget(self.analyze_btn)
        
        actions_layout.addStretch()
        
        # Export results button
        self.export_btn = QPushButton("💾 Export Results")
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: #2a2a2a;
                color: #e0e0e0;
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background: #404040;
                border-color: #00d4ff;
            }
            QPushButton:disabled {
                background: #1a1a1a;
                color: #606060;
                border-color: #303030;
            }
        """)
        self.export_btn.clicked.connect(self.export_results)
        actions_layout.addWidget(self.export_btn)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setStyleSheet(self.export_btn.styleSheet())
        clear_btn.clicked.connect(self.clear_results)
        actions_layout.addWidget(clear_btn)
        
        layout.addLayout(actions_layout)
    
    def apply_dark_theme(self):
        """Apply dark theme to window"""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1a1a1a, stop: 0.5 #2a2a2a, stop: 1 #1a1a1a);
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def on_language_changed(self, language):
        """Handle global language change"""
        self.current_language = language
        self.setWindowTitle(f"Image Analysis - {language.upper()}")
        logger.info(f"Image window language changed to: {language}")
    
    def center_window(self):
        """Center window on screen"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def load_image(self):
        """Load image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Image",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff *.webp);;All Files (*)"
        )
        
        if file_path:
            try:
                # Load and display image
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # Scale image to fit label while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        self.image_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    self.image_label.setText("")
                    
                    # Update image info
                    file_size = os.path.getsize(file_path)
                    file_size_mb = file_size / (1024 * 1024)
                    
                    info_text = f"File: {os.path.basename(file_path)}\n"
                    info_text += f"Size: {pixmap.width()}x{pixmap.height()}\n"
                    info_text += f"File Size: {file_size_mb:.2f} MB"
                    
                    self.image_info_label.setText(info_text)
                    
                    # Enable analyze button
                    self.analyze_btn.setEnabled(True)
                    
                    # Store image path
                    self.current_image_path = file_path
                    
                    self.progress_label.setText("Image loaded - Ready to analyze")
                    self.progress_label.setStyleSheet("QLabel { color: #00ff00; }")
                    
                    logger.info(f"Image loaded: {file_path}")
                    
                else:
                    self.show_error("Failed to load image. Unsupported format.")
                    
            except Exception as e:
                self.show_error(f"Failed to load image: {str(e)}")
    
    def analyze_image(self):
        """Start image analysis"""
        if not hasattr(self, 'current_image_path'):
            self.show_error("No image loaded.")
            return
        
        # Show progress
        self.progress_bar.show()
        self.analyze_btn.setEnabled(False)
        self.progress_label.setText("Analyzing...")
        self.progress_label.setStyleSheet("QLabel { color: #ffa500; }")
        
        # Start analysis thread
        self.analysis_thread = AnalysisThread(
            self.current_image_path,
            self.models_manager,
            self.processor
        )
        self.analysis_thread.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_thread.error_occurred.connect(self.on_analysis_error)
        self.analysis_thread.progress_update.connect(self.on_progress_update)
        self.analysis_thread.start()
    
    def on_analysis_complete(self, results):
        """Handle completed analysis"""
        self.progress_bar.hide()
        self.analyze_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        self.current_results = results
        
        # Display results
        self.display_results()
        
        self.progress_label.setText("Analysis complete")
        self.progress_label.setStyleSheet("QLabel { color: #00ff00; }")
        
        logger.info("Image analysis completed successfully")
    
    def on_analysis_error(self, error):
        """Handle analysis error"""
        self.progress_bar.hide()
        self.analyze_btn.setEnabled(True)
        
        self.show_error(f"Analysis failed: {error}")
        
        self.progress_label.setText("Analysis failed")
        self.progress_label.setStyleSheet("QLabel { color: #ff6b6b; }")
    
    def on_progress_update(self, message):
        """Handle progress updates"""
        self.progress_label.setText(message)
    
    def display_results(self):
        """Display analysis results"""
        if not self.current_results:
            return
        
        # Clear existing results
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)
        
        # Show results based on selected tab
        current_tab = self.results_tabs.currentText()
        self.switch_results_tab(current_tab)
    
    def switch_results_tab(self, tab_name):
        """Switch between results tabs"""
        if not self.current_results:
            return
        
        # Clear current content
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)
        
        if tab_name == "Basic Features":
            self.show_basic_features()
        elif tab_name == "AI Features":
            self.show_ai_features()
        elif tab_name == "Edge Detection":
            self.show_edge_detection()
        elif tab_name == "Color Analysis":
            self.show_color_analysis()
        elif tab_name == "Text Extraction (OCR)":
            self.show_ocr_results()
    
    def show_basic_features(self):
        """Show basic image features"""
        if 'basic_features' not in self.current_results:
            self.show_no_data("Basic features not available")
            return
        
        features = self.current_results['basic_features']
        
        # Create features table
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Property", "Value"])
        table.setStyleSheet("""
            QTableWidget {
                background: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #404040;
                gridline-color: #404040;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background: #404040;
                color: #e0e0e0;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
        """)
        
        # Populate table
        rows = []
        
        # Dimensions
        dims = features['dimensions']
        rows.append(["Width", f"{dims['width']} pixels"])
        rows.append(["Height", f"{dims['height']} pixels"])
        rows.append(["Channels", str(dims['channels'])])
        rows.append(["Total Pixels", f"{features['file_size_pixels']:,}"])
        
        # Color statistics
        color_stats = features['color_stats']
        rows.append(["Brightness", f"{color_stats['brightness']:.2f}"])
        rows.append(["Contrast", f"{color_stats['contrast']:.2f}"])
        rows.append(["Unique Colors", f"{color_stats['unique_colors']:,}"])
        
        if len(color_stats['mean_rgb']) == 3:
            rows.append(["Mean Red", f"{color_stats['mean_rgb'][0]:.2f}"])
            rows.append(["Mean Green", f"{color_stats['mean_rgb'][1]:.2f}"])
            rows.append(["Mean Blue", f"{color_stats['mean_rgb'][2]:.2f}"])
        
        table.setRowCount(len(rows))
        for i, (prop, value) in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(prop))
            table.setItem(i, 1, QTableWidgetItem(str(value)))
        
        table.resizeColumnsToContents()
        self.results_layout.addWidget(table)
    
    def show_ai_features(self):
        """Show AI-extracted features"""
        if 'ai_features' not in self.current_results or self.current_results['ai_features'] is None:
            self.show_no_data("AI features not available.\nEnsure ViT model is loaded.")
            return
        
        features = self.current_results['ai_features']
        
        # Handle both dict and array types
        if isinstance(features, dict):
            info_text = "AI Feature Analysis:\n\n"
            for key, value in features.items():
                if hasattr(value, 'shape'):
                    info_text += f"{key}: shape {value.shape}, dtype {value.dtype}\n"
                else:
                    info_text += f"{key}: {value}\n"
            info_text += "\nThese are deep learning features extracted using Vision Transformer (ViT) model."
        else:
            # Show feature vector information for array type
            info_text = f"AI Feature Vector Shape: {features.shape}\n"
            info_text += f"Feature Dimensions: {features.shape[0] if len(features.shape) > 0 else 0}\n"
            info_text += f"Data Type: {features.dtype}\n\n"
            info_text += "These are deep learning features extracted using Vision Transformer (ViT) model.\n"
            info_text += "The features represent high-level semantic information about the image."
        
        label = QLabel(info_text)
        label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
                padding: 20px;
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)
        label.setWordWrap(True)
        self.results_layout.addWidget(label)
        
        # Show feature statistics
        stats_text = f"Statistics:\n"
        stats_text += f"Min: {np.min(features):.6f}\n"
        stats_text += f"Max: {np.max(features):.6f}\n"
        stats_text += f"Mean: {np.mean(features):.6f}\n"
        stats_text += f"Std: {np.std(features):.6f}"
        
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet(label.styleSheet())
        self.results_layout.addWidget(stats_label)
    
    def show_edge_detection(self):
        """Show edge detection results"""
        if 'edges' not in self.current_results:
            self.show_no_data("Edge detection not available")
            return
        
        edges = self.current_results['edges']
        
        # Convert edges to QPixmap and display
        # Create a figure with original and edges side by side
        fig = Figure(figsize=(12, 6))
        
        # Original image
        ax1 = fig.add_subplot(1, 2, 1)
        ax1.imshow(self.current_results['image_array'])
        ax1.set_title('Original Image')
        ax1.axis('off')
        
        # Edges
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.imshow(edges, cmap='gray')
        ax2.set_title('Edge Detection (Canny)')
        ax2.axis('off')
        
        fig.tight_layout()
        
        # Create canvas widget
        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background: #2a2a2a;")
        self.results_layout.addWidget(canvas)
        
        # Edge statistics
        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.shape[0] * edges.shape[1]
        edge_percentage = (edge_pixels / total_pixels) * 100
        
        stats_text = f"Edge Statistics:\n"
        stats_text += f"Edge Pixels: {edge_pixels:,}\n"
        stats_text += f"Total Pixels: {total_pixels:,}\n"
        stats_text += f"Edge Percentage: {edge_percentage:.2f}%"
        
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
                padding: 15px;
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)
        self.results_layout.addWidget(stats_label)
    
    def show_color_analysis(self):
        """Show color analysis results"""
        if 'histogram' not in self.current_results:
            self.show_no_data("Color analysis not available")
            return
        
        # Display histogram
        canvas = FigureCanvas(self.current_results['histogram'])
        canvas.setStyleSheet("background: #2a2a2a;")
        self.results_layout.addWidget(canvas)
    
    def show_ocr_results(self):
        """Show OCR (Text Extraction) results"""
        if 'ocr' not in self.current_results:
            self.show_no_data("Text extraction not available")
            return
        
        ocr_data = self.current_results['ocr']
        
        # Create scroll area for OCR results
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Title
        title_label = QLabel("🔤 Text Extraction Results")
        title_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background: #1a1a1a;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        content_layout.addWidget(title_label)
        
        # Combined text result
        combined_text = ocr_data.get('combined', {}).get('text', '')
        has_text = ocr_data.get('combined', {}).get('has_text', False)
        
        if has_text and combined_text.strip():
            # Text found
            text_group = QGroupBox("✅ Extracted Text")
            text_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #00ff00;
                    border-radius: 10px;
                    margin: 10px 0;
                    padding-top: 15px;
                    color: #00ff00;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
            
            text_layout = QVBoxLayout(text_group)
            
            # Extracted text display
            text_display = QTextEdit()
            text_display.setPlainText(combined_text)
            text_display.setReadOnly(True)
            text_display.setMaximumHeight(200)
            text_display.setStyleSheet("""
                QTextEdit {
                    background: #1a1a1a;
                    color: #e0e0e0;
                    border: 1px solid #404040;
                    border-radius: 5px;
                    padding: 10px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 12px;
                    line-height: 1.4;
                }
            """)
            text_layout.addWidget(text_display)
            
            # Word count
            word_count = len(combined_text.split())
            char_count = len(combined_text)
            stats_label = QLabel(f"📊 Words: {word_count} | Characters: {char_count}")
            stats_label.setStyleSheet("""
                QLabel {
                    color: #a0a0a0;
                    font-size: 12px;
                    padding: 5px;
                }
            """)
            text_layout.addWidget(stats_label)
            
            content_layout.addWidget(text_group)
        else:
            # No text found
            no_text_label = QLabel("❌ No text detected in this image")
            no_text_label.setAlignment(Qt.AlignCenter)
            no_text_label.setStyleSheet("""
                QLabel {
                    color: #ff9999;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 30px;
                    background: #2a1a1a;
                    border: 2px dashed #ff9999;
                    border-radius: 10px;
                    margin: 20px;
                }
            """)
            content_layout.addWidget(no_text_label)
        
        # OCR Engine Details
        details_group = QGroupBox("🔍 OCR Engine Details")
        details_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 10px;
                margin: 10px 0;
                padding-top: 15px;
                color: #e0e0e0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        details_layout = QVBoxLayout(details_group)
        
        # Engine results
        for engine_name, engine_data in ocr_data.items():
            if engine_name == 'combined':
                continue
                
            engine_label = QLabel(f"🔧 {engine_name.title()} Engine:")
            engine_label.setStyleSheet("QLabel { color: #00d4ff; font-weight: bold; }")
            details_layout.addWidget(engine_label)
            
            if 'error' in engine_data:
                error_label = QLabel(f"   ❌ Error: {engine_data['error']}")
                error_label.setStyleSheet("QLabel { color: #ff6b6b; margin-left: 20px; }")
                details_layout.addWidget(error_label)
            else:
                text_found = engine_data.get('text', '').strip()
                if text_found:
                    success_label = QLabel(f"   ✅ Extracted {len(text_found.split())} words")
                    success_label.setStyleSheet("QLabel { color: #00ff00; margin-left: 20px; }")
                    details_layout.addWidget(success_label)
                    
                    # Show confidence if available (EasyOCR)
                    if 'confidences' in engine_data and engine_data['confidences']:
                        avg_confidence = sum(engine_data['confidences']) / len(engine_data['confidences'])
                        conf_label = QLabel(f"   📊 Average Confidence: {avg_confidence:.2%}")
                        conf_label.setStyleSheet("QLabel { color: #a0a0a0; margin-left: 20px; }")
                        details_layout.addWidget(conf_label)
                else:
                    no_text_label = QLabel(f"   ℹ️  No text detected")
                    no_text_label.setStyleSheet("QLabel { color: #a0a0a0; margin-left: 20px; }")
                    details_layout.addWidget(no_text_label)
        
        content_layout.addWidget(details_group)
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        self.results_layout.addWidget(scroll)
    
    def show_no_data(self, message):
        """Show no data message"""
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #808080;
                font-size: 16px;
                font-style: italic;
                padding: 50px;
                background: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """)
        self.results_layout.addWidget(label)
    
    def export_results(self):
        """Export analysis results"""
        if not self.current_results:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "image_analysis.json",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                export_data = {
                    'image_path': self.current_results['image_path'],
                    'analysis_timestamp': str(Path(self.current_results['image_path']).stat().st_mtime),
                    'basic_features': self.current_results.get('basic_features'),
                    'ai_features_available': self.current_results.get('ai_features') is not None,
                    'edge_detection_available': 'edges' in self.current_results,
                    'ocr_results': self.current_results.get('ocr')
                }
                
                # Convert numpy arrays to lists for JSON serialization
                if self.current_results.get('ai_features') is not None:
                    export_data['ai_features_stats'] = {
                        'shape': list(self.current_results['ai_features'].shape),
                        'min': float(np.min(self.current_results['ai_features'])),
                        'max': float(np.max(self.current_results['ai_features'])),
                        'mean': float(np.mean(self.current_results['ai_features'])),
                        'std': float(np.std(self.current_results['ai_features']))
                    }
                
                if file_path.lower().endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2)
                else:
                    # Export as text
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("Image Analysis Results\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(f"Image: {export_data['image_path']}\n\n")
                        
                        if export_data['basic_features']:
                            f.write("Basic Features:\n")
                            f.write("-" * 20 + "\n")
                            for key, value in export_data['basic_features'].items():
                                f.write(f"{key}: {value}\n")
                            f.write("\n")
                        
                        if export_data['ai_features_available']:
                            f.write("AI Features Available: Yes\n")
                            stats = export_data.get('ai_features_stats', {})
                            for key, value in stats.items():
                                f.write(f"  {key}: {value}\n")
                        else:
                            f.write("AI Features Available: No\n")
                
                self.progress_label.setText(f"Results exported to {os.path.basename(file_path)}")
                self.progress_label.setStyleSheet("QLabel { color: #00ff00; }")
                
                logger.info(f"Results exported to: {file_path}")
                
            except Exception as e:
                self.show_error(f"Failed to export results: {str(e)}")
    
    def clear_results(self):
        """Clear all results and reset interface"""
        # Clear image
        self.image_label.clear()
        self.image_label.setText("No image loaded")
        self.image_info_label.clear()
        
        # Clear results
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)
        
        self.results_layout.addWidget(self.no_results_label)
        
        # Reset buttons
        self.analyze_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        
        # Clear data
        self.current_results = None
        if hasattr(self, 'current_image_path'):
            delattr(self, 'current_image_path')
        
        self.progress_label.setText("Ready")
        self.progress_label.setStyleSheet("QLabel { color: #00ff00; }")
        
        logger.info("Interface cleared")
    
    def show_error(self, message):
        """Show error message"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Error")
        msg.setText("An error occurred")
        msg.setInformativeText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.setStyleSheet("""
            QMessageBox {
                background: #2a2a2a;
                color: #e0e0e0;
            }
            QMessageBox QPushButton {
                background: #ff6b6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: #ff5252;
            }
        """)
        msg.exec()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.analysis_thread and self.analysis_thread.isRunning():
            self.analysis_thread.quit()
            self.analysis_thread.wait()
        
        event.accept()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = ImageAnalysisWindow()
    window.show()
    sys.exit(app.exec())
