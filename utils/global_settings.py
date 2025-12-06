"""
Global Settings Singleton for TurnIT Application
Manages application-wide settings and language changes
"""

from PySide6.QtCore import QObject, Signal
from pathlib import Path
import json

class GlobalSettings(QObject):
    """Singleton class for global application settings"""
    
    language_changed = Signal(str)  # Emits when language changes
    theme_changed = Signal(str)     # Emits when theme changes
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        
        self.settings_file = Path(__file__).parent.parent / "config" / "settings.json"
        self.current_language = "en"
        self.current_theme = "dark"
        
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_language = settings.get('language', 'en')
                    self.current_theme = settings.get('theme', 'dark')
        except Exception:
            pass
    
    def save_settings(self):
        """Save settings to file"""
        try:
            self.settings_file.parent.mkdir(exist_ok=True, parents=True)
            settings = {
                'language': self.current_language,
                'theme': self.current_theme
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception:
            pass
    
    def set_language(self, language: str):
        """Set application language and emit signal"""
        if language != self.current_language:
            self.current_language = language
            self.save_settings()
            self.language_changed.emit(language)
    
    def set_theme(self, theme: str):
        """Set application theme and emit signal"""
        if theme != self.current_theme:
            self.current_theme = theme
            self.save_settings()
            self.theme_changed.emit(theme)
    
    def get_language(self) -> str:
        """Get current language"""
        return self.current_language
    
    def get_theme(self) -> str:
        """Get current theme"""
        return self.current_theme
