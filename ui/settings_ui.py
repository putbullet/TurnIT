"""
Settings UI for TurnIT Application
Configuration interface for language, preferences, and app settings
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Import PySide6 components
try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QLabel, QPushButton, QComboBox, QCheckBox, QSlider, QSpinBox,
        QGroupBox, QFrame, QMessageBox, QTabWidget, QScrollArea,
        QFileDialog, QLineEdit, QTextEdit
    )
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QFont, QIcon
except ImportError:
    print("PySide6 not installed. Please run: pip install PySide6")
    sys.exit(1)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import get_logger
from utils.global_settings import GlobalSettings

logger = get_logger(__name__)

class SettingsManager:
    """Manages application settings and localization"""
    
    def __init__(self):
        self.settings_file = Path(__file__).parent.parent / "config" / "settings.json"
        self.languages_dir = Path(__file__).parent.parent / "config" / "languages"
        
        # Create directories if they don't exist
        self.settings_file.parent.mkdir(exist_ok=True)
        self.languages_dir.mkdir(exist_ok=True)
        
        # Default settings
        self.default_settings = {
            "language": "en",
            "theme": "dark",
            "audio": {
                "default_input_device": "auto",
                "default_output_device": "auto",
                "sample_rate": 16000,
                "buffer_size": 1024
            },
            "ai": {
                "whisper_model": "openai/whisper-large-v3",
                "vit_model": "google/vit-base-patch16-224",
                "use_gpu": True,
                "cache_models": True
            },
            "ui": {
                "window_opacity": 1.0,
                "show_animations": True,
                "auto_save": True,
                "confirm_exit": True
            }
        }
        
        # Language translations
        self.translations = {
            "en": {
                "app_title": "TurnIT - Settings",
                "language": "Language",
                "general": "General",
                "audio": "Audio",
                "ai_models": "AI Models",
                "interface": "Interface",
                "about": "About",
                "save": "Save Settings",
                "reset": "Reset to Defaults",
                "close": "Close",
                "english": "English",
                "arabic": "العربية",
                "french": "Français",
                "theme": "Theme",
                "dark_theme": "Dark Theme",
                "input_device": "Input Device",
                "output_device": "Output Device",
                "sample_rate": "Sample Rate",
                "buffer_size": "Buffer Size",
                "whisper_model": "Speech Recognition Model",
                "image_model": "Image Analysis Model",
                "use_gpu": "Use GPU if available",
                "cache_models": "Cache models locally",
                "window_opacity": "Window Opacity",
                "show_animations": "Show Animations",
                "auto_save": "Auto-save results",
                "confirm_exit": "Confirm before exit",
                "version": "Version",
                "developer": "Developer",
                "description": "AI-Powered Desktop Application"
            },
            "ar": {
                "app_title": "TurnIT - الإعدادات",
                "language": "اللغة",
                "general": "عام",
                "audio": "الصوت",
                "ai_models": "نماذج الذكاء الاصطناعي",
                "interface": "الواجهة",
                "about": "حول",
                "save": "حفظ الإعدادات",
                "reset": "إعادة تعيين",
                "close": "إغلاق",
                "english": "English",
                "arabic": "العربية",
                "french": "Français",
                "theme": "المظهر",
                "dark_theme": "المظهر الداكن",
                "input_device": "جهاز الإدخال",
                "output_device": "جهاز الإخراج",
                "sample_rate": "معدل العينة",
                "buffer_size": "حجم المخزن المؤقت",
                "whisper_model": "نموذج التعرف على الكلام",
                "image_model": "نموذج تحليل الصور",
                "use_gpu": "استخدام المعالج الرسومي",
                "cache_models": "حفظ النماذج محلياً",
                "window_opacity": "شفافية النافذة",
                "show_animations": "إظهار الحركات",
                "auto_save": "حفظ تلقائي للنتائج",
                "confirm_exit": "تأكيد قبل الخروج",
                "version": "الإصدار",
                "developer": "المطور",
                "description": "تطبيق مكتبي مدعوم بالذكاء الاصطناعي"
            },
            "fr": {
                "app_title": "TurnIT - Paramètres",
                "language": "Langue",
                "general": "Général",
                "audio": "Audio",
                "ai_models": "Modèles IA",
                "interface": "Interface",
                "about": "À propos",
                "save": "Sauvegarder",
                "reset": "Réinitialiser",
                "close": "Fermer",
                "english": "English",
                "arabic": "العربية",
                "french": "Français",
                "theme": "Thème",
                "dark_theme": "Thème sombre",
                "input_device": "Périphérique d'entrée",
                "output_device": "Périphérique de sortie",
                "sample_rate": "Fréquence d'échantillonnage",
                "buffer_size": "Taille du tampon",
                "whisper_model": "Modèle de reconnaissance vocale",
                "image_model": "Modèle d'analyse d'image",
                "use_gpu": "Utiliser le GPU si disponible",
                "cache_models": "Mettre en cache les modèles",
                "window_opacity": "Opacité de la fenêtre",
                "show_animations": "Afficher les animations",
                "auto_save": "Sauvegarde automatique",
                "confirm_exit": "Confirmer avant la sortie",
                "version": "Version",
                "developer": "Développeur",
                "description": "Application de bureau alimentée par l'IA"
            }
        }
        
        self.current_settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_settings = self.default_settings.copy()
                self._merge_dict(merged_settings, settings)
                return merged_settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            logger.error(f"Failed to load settings: {str(e)}")
            return self.default_settings.copy()
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.current_settings = settings
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {str(e)}")
            return False
    
    def get_translation(self, key: str, language: str = None) -> str:
        """Get translation for a key"""
        if language is None:
            language = self.current_settings.get("language", "en")
        
        return self.translations.get(language, {}).get(key, key)
    
    def _merge_dict(self, target: Dict, source: Dict):
        """Recursively merge dictionaries"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dict(target[key], value)
            else:
                target[key] = value

class SettingsWindow(QMainWindow):
    """Settings configuration window"""
    
    settings_changed = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.current_language = self.settings_manager.current_settings["language"]
        
        self.init_ui()
        self.load_current_settings()
        self.center_window()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("TurnIT - Settings")
        self.setFixedSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create header
        self.create_header(main_layout)
        
        # Create tabs
        self.create_tabs(main_layout)
        
        # Create buttons
        self.create_buttons(main_layout)
        
        self.apply_dark_theme()
    
    def create_header(self, layout):
        """Create header section"""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel(self.tr("app_title"))
        title_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
    
    def create_tabs(self, layout):
        """Create settings tabs"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #404040;
                border-radius: 8px;
                background: #2a2a2a;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #00d4ff;
                color: white;
            }
            QTabBar::tab:hover {
                background: #404040;
            }
        """)
        
        # General tab
        self.general_tab = self.create_general_tab()
        self.tab_widget.addTab(self.general_tab, self.tr("general"))
        
        # Audio tab
        self.audio_tab = self.create_audio_tab()
        self.tab_widget.addTab(self.audio_tab, self.tr("audio"))
        
        # AI Models tab
        self.ai_tab = self.create_ai_tab()
        self.tab_widget.addTab(self.ai_tab, self.tr("ai_models"))
        
        # Interface tab
        self.interface_tab = self.create_interface_tab()
        self.tab_widget.addTab(self.interface_tab, self.tr("interface"))
        
        # About tab
        self.about_tab = self.create_about_tab()
        self.tab_widget.addTab(self.about_tab, self.tr("about"))
        
        layout.addWidget(self.tab_widget)
    
    def create_general_tab(self):
        """Create general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Language setting
        lang_group = QGroupBox(self.tr("language"))
        lang_group.setStyleSheet(self.get_group_style())
        lang_layout = QVBoxLayout(lang_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("العربية", "ar")
        self.language_combo.addItem("Français", "fr")
        self.language_combo.setStyleSheet(self.get_combo_style())
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.language_combo)
        
        layout.addWidget(lang_group)
        
        # Theme setting
        theme_group = QGroupBox(self.tr("theme"))
        theme_group.setStyleSheet(self.get_group_style())
        theme_layout = QVBoxLayout(theme_group)
        
        self.dark_theme_check = QCheckBox(self.tr("dark_theme"))
        self.dark_theme_check.setStyleSheet(self.get_checkbox_style())
        theme_layout.addWidget(self.dark_theme_check)
        
        layout.addWidget(theme_group)
        
        layout.addStretch()
        return widget
    
    def create_audio_tab(self):
        """Create audio settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Device settings
        device_group = QGroupBox(self.tr("audio"))
        device_group.setStyleSheet(self.get_group_style())
        device_layout = QGridLayout(device_group)
        
        # Input device
        device_layout.addWidget(QLabel(self.tr("input_device")), 0, 0)
        self.input_device_combo = QComboBox()
        self.input_device_combo.setStyleSheet(self.get_combo_style())
        device_layout.addWidget(self.input_device_combo, 0, 1)
        
        # Output device
        device_layout.addWidget(QLabel(self.tr("output_device")), 1, 0)
        self.output_device_combo = QComboBox()
        self.output_device_combo.setStyleSheet(self.get_combo_style())
        device_layout.addWidget(self.output_device_combo, 1, 1)
        
        # Sample rate
        device_layout.addWidget(QLabel(self.tr("sample_rate")), 2, 0)
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["8000", "16000", "22050", "44100", "48000"])
        self.sample_rate_combo.setStyleSheet(self.get_combo_style())
        device_layout.addWidget(self.sample_rate_combo, 2, 1)
        
        layout.addWidget(device_group)
        layout.addStretch()
        return widget
    
    def create_ai_tab(self):
        """Create AI models settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Model settings
        models_group = QGroupBox(self.tr("ai_models"))
        models_group.setStyleSheet(self.get_group_style())
        models_layout = QGridLayout(models_group)
        
        # Whisper model
        models_layout.addWidget(QLabel(self.tr("whisper_model")), 0, 0)
        self.whisper_model_combo = QComboBox()
        self.whisper_model_combo.addItems([
            "openai/whisper-large-v3",
            "openai/whisper-large-v2",
            "openai/whisper-medium",
            "openai/whisper-small"
        ])
        self.whisper_model_combo.setStyleSheet(self.get_combo_style())
        models_layout.addWidget(self.whisper_model_combo, 0, 1)
        
        # Image model
        models_layout.addWidget(QLabel(self.tr("image_model")), 1, 0)
        self.image_model_combo = QComboBox()
        self.image_model_combo.addItems([
            "google/vit-base-patch16-224",
            "google/vit-large-patch16-224",
            "microsoft/resnet-50"
        ])
        self.image_model_combo.setStyleSheet(self.get_combo_style())
        models_layout.addWidget(self.image_model_combo, 1, 1)
        
        layout.addWidget(models_group)
        
        # Performance settings
        perf_group = QGroupBox("Performance")
        perf_group.setStyleSheet(self.get_group_style())
        perf_layout = QVBoxLayout(perf_group)
        
        self.use_gpu_check = QCheckBox(self.tr("use_gpu"))
        self.use_gpu_check.setStyleSheet(self.get_checkbox_style())
        perf_layout.addWidget(self.use_gpu_check)
        
        self.cache_models_check = QCheckBox(self.tr("cache_models"))
        self.cache_models_check.setStyleSheet(self.get_checkbox_style())
        perf_layout.addWidget(self.cache_models_check)
        
        layout.addWidget(perf_group)
        layout.addStretch()
        return widget
    
    def create_interface_tab(self):
        """Create interface settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # UI settings
        ui_group = QGroupBox(self.tr("interface"))
        ui_group.setStyleSheet(self.get_group_style())
        ui_layout = QVBoxLayout(ui_group)
        
        # Window opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel(self.tr("window_opacity")))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setStyleSheet(self.get_slider_style())
        opacity_layout.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("100%")
        opacity_layout.addWidget(self.opacity_label)
        ui_layout.addLayout(opacity_layout)
        
        # Other UI options
        self.show_animations_check = QCheckBox(self.tr("show_animations"))
        self.show_animations_check.setStyleSheet(self.get_checkbox_style())
        ui_layout.addWidget(self.show_animations_check)
        
        self.auto_save_check = QCheckBox(self.tr("auto_save"))
        self.auto_save_check.setStyleSheet(self.get_checkbox_style())
        ui_layout.addWidget(self.auto_save_check)
        
        self.confirm_exit_check = QCheckBox(self.tr("confirm_exit"))
        self.confirm_exit_check.setStyleSheet(self.get_checkbox_style())
        ui_layout.addWidget(self.confirm_exit_check)
        
        layout.addWidget(ui_group)
        layout.addStretch()
        return widget
    
    def create_about_tab(self):
        """Create about tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(30)
        
        # App info
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignCenter)
        
        # App icon/title
        app_title = QLabel("TurnIT")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 36px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        info_layout.addWidget(app_title)
        
        # Description
        description = QLabel(self.tr("description"))
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #a0a0a0; font-size: 16px;")
        info_layout.addWidget(description)
        
        # Version
        version = QLabel(f"{self.tr('version')}: 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: #e0e0e0; font-size: 14px; margin-top: 20px;")
        info_layout.addWidget(version)
        
        # Developer
        developer = QLabel(f"{self.tr('developer')}: putbullet")
        developer.setAlignment(Qt.AlignCenter)
        developer.setStyleSheet("color: #e0e0e0; font-size: 14px;")
        info_layout.addWidget(developer)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        return widget
    
    def create_buttons(self, layout):
        """Create control buttons"""
        button_layout = QHBoxLayout()
        
        # Reset button
        reset_btn = QPushButton(self.tr("reset"))
        reset_btn.setStyleSheet(self.get_button_style("#ff6b6b", "#ff5252"))
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        # Save button
        save_btn = QPushButton(self.tr("save"))
        save_btn.setStyleSheet(self.get_button_style("#00d4ff", "#00b8e6"))
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def get_group_style(self):
        """Get group box style"""
        return """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 10px;
                margin: 10px 0;
                padding-top: 10px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
    
    def get_combo_style(self):
        """Get combo box style"""
        return """
            QComboBox {
                background: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 5px;
                padding: 8px;
                min-width: 150px;
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
        """
    
    def get_checkbox_style(self):
        """Get checkbox style"""
        return """
            QCheckBox {
                color: #e0e0e0;
                font-size: 14px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #404040;
                border-radius: 5px;
                background: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background: #00d4ff;
                border-color: #00d4ff;
            }
        """
    
    def get_slider_style(self):
        """Get slider style"""
        return """
            QSlider::groove:horizontal {
                border: 1px solid #404040;
                height: 8px;
                background: #2a2a2a;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00d4ff;
                border: 1px solid #00b8e6;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #00d4ff;
                border-radius: 4px;
            }
        """
    
    def get_button_style(self, bg_color, hover_color):
        """Get button style"""
        return f"""
            QPushButton {{
                background: {bg_color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background: {hover_color};
            }}
            QPushButton:pressed {{
                background: #1a1a1a;
            }}
        """
    
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
    
    def center_window(self):
        """Center window on screen"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def tr(self, key: str) -> str:
        """Get translation for current language"""
        return self.settings_manager.get_translation(key, self.current_language)
    
    def on_language_changed(self):
        """Handle language change"""
        current_data = self.language_combo.currentData()
        if current_data and current_data != self.current_language:
            self.current_language = current_data
            # Update global settings to propagate to all windows
            GlobalSettings().set_language(current_data)
            self.update_ui_language()
    
    def update_ui_language(self):
        """Update UI with new language"""
        # Update window title
        self.setWindowTitle(self.tr("app_title"))
        
        # Update tab titles
        self.tab_widget.setTabText(0, self.tr("general"))
        self.tab_widget.setTabText(1, self.tr("audio"))
        self.tab_widget.setTabText(2, self.tr("ai_models"))
        self.tab_widget.setTabText(3, self.tr("interface"))
        self.tab_widget.setTabText(4, self.tr("about"))
        
        # Note: In a full implementation, you'd update all labels here
        # For brevity, this is a simplified version
    
    def load_current_settings(self):
        """Load current settings into UI"""
        settings = self.settings_manager.current_settings
        
        # Language
        lang_index = self.language_combo.findData(settings["language"])
        if lang_index >= 0:
            self.language_combo.setCurrentIndex(lang_index)
        
        # Audio
        self.sample_rate_combo.setCurrentText(str(settings["audio"]["sample_rate"]))
        
        # AI
        self.whisper_model_combo.setCurrentText(settings["ai"]["whisper_model"])
        self.use_gpu_check.setChecked(settings["ai"]["use_gpu"])
        self.cache_models_check.setChecked(settings["ai"]["cache_models"])
        
        # Interface
        self.opacity_slider.setValue(int(settings["ui"]["window_opacity"] * 100))
        self.show_animations_check.setChecked(settings["ui"]["show_animations"])
        self.auto_save_check.setChecked(settings["ui"]["auto_save"])
        self.confirm_exit_check.setChecked(settings["ui"]["confirm_exit"])
        
        # Connect opacity slider
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
    
    def save_settings(self):
        """Save current settings"""
        try:
            settings = self.settings_manager.current_settings.copy()
            
            # Update settings from UI
            settings["language"] = self.language_combo.currentData() or "en"
            settings["audio"]["sample_rate"] = int(self.sample_rate_combo.currentText())
            settings["ai"]["whisper_model"] = self.whisper_model_combo.currentText()
            settings["ai"]["use_gpu"] = self.use_gpu_check.isChecked()
            settings["ai"]["cache_models"] = self.cache_models_check.isChecked()
            settings["ui"]["window_opacity"] = self.opacity_slider.value() / 100.0
            settings["ui"]["show_animations"] = self.show_animations_check.isChecked()
            settings["ui"]["auto_save"] = self.auto_save_check.isChecked()
            settings["ui"]["confirm_exit"] = self.confirm_exit_check.isChecked()
            
            if self.settings_manager.save_settings(settings):
                self.settings_changed.emit(settings)
                self.show_message("Settings saved successfully!")
                logger.info("Settings saved successfully")
            else:
                self.show_error("Failed to save settings.")
                
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            self.show_error(f"Error saving settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.settings_manager.save_settings(self.settings_manager.default_settings):
                self.load_current_settings()
                self.show_message("Settings reset to defaults!")
                logger.info("Settings reset to defaults")
            else:
                self.show_error("Failed to reset settings.")
    
    def show_message(self, message):
        """Show info message"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Settings")
        msg.setText("Success")
        msg.setInformativeText(message)
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background: #2a2a2a;
                color: #e0e0e0;
            }
            QMessageBox QPushButton {
                background: #00d4ff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 80px;
            }
        """)
        msg.exec()
    
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
        """)
        msg.exec()

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())
