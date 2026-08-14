from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal

### DATA ###
class GameData:
    '''Central data, stores everything for player, money outfit, placed items etc'''
    def __init__(self):
        self.money = 300
        self.inventory_clothes = []
        self.worn_clothes = []
        self.equipped_clothes = {}
        self.inventory_furniture = []
        self.placed_furniture = []

### UNIVERSAL_STYLES ###
class UniversalStyles:
    '''takes colorpallete and makes consistent stylesheet strings for the ui'''
    def __init__(self, primary, secondary, border, hover, text, scroll, scroll_hover):
        self.col_primary = primary
        self.col_secondary = secondary
        self.col_border = border
        self.col_hover = hover
        self.col_text = text
        self.col_scroll = scroll
        self.col_scroll_hover = scroll_hover
        
    def header_button_style(self):
        return f"""
        QPushButton {{
            background-color: {self.col_primary};
            border: 2px solid {self.col_border};
            font-size: 20px;
            color: {self.col_text};
        }}
        QPushButton:hover {{
            background-color: {self.col_hover};
        }}
        """
    def money_label_style(self):
        return f"""
        QLabel {{
            background-color: {self.col_secondary};
            border: 1.5px solid {self.col_border};
            border-radius: 12px;
            font-weight: 900;
            font-size: 18px;
            color: {self.col_text};
        }}
        """

    def frame_style(self):
        return f"""
        QFrame {{
            background-color: {self.col_secondary};
            border: 1.5px solid {self.col_border};
            border-radius: 25px;
        }}
        """

    def action_button_style(self):
        return f"""
        QPushButton {{
            background-color: {self.col_border};
            color: {self.col_primary};
            border-radius: 20px;
            font-weight: bold;
            font-size: 16px;
            border: none;
        }}
        QPushButton:hover {{
            background-color: {self.col_hover};
        }}
        """

    def scrollbar_style(self):
        return f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 14px; margin: 10px 0px; }}
        QScrollBar::handle:vertical {{ background: {self.col_scroll}; min-height: 30px; border-radius: 7px; }}
        QScrollBar::handle:vertical:hover {{ background: {self.col_scroll_hover}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

        QScrollBar:horizontal {{ background: transparent; height: 14px; margin: 0px 10px; border: none; }}
        QScrollBar::handle:horizontal {{ background: {self.col_scroll}; min-width: 30px; border-radius: 7px; }}
        QScrollBar::handle:horizontal:hover {{ background: {self.col_scroll_hover}; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; background: none; }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}
        """
    def button_style(self):
        return f"""
            QPushButton {{
                background: {self.col_secondary};
                border: 2px solid {self.col_text};
                border-radius: 8px;
                padding: 5px;
                color: {self.col_text};
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {self.col_hover};}}
        """
    def task_style(self):
        return f'''
            #Card {{
                background-color: {self.col_secondary}; 
                color: {self.col_text}; 
                border: 2px solid {self.col_border}; 
                border-radius: 10px;
            }}
            QCheckBox {{
                spacing: 8px; 
                font-size: 14px; 
                color: {self.col_text};
                background: transparent;
                border: none;
                margin-left: 5px; 
            }}
            QCheckBox::indicator {{
                width: 18px;   
                height: 18px;
                border: 2px solid {self.col_border}; 
                border-radius: 4px;
                background: {self.col_primary}; 
            }}
            QCheckBox::indicator:checked {{
                background-color: #4CAF50;
                border: 2px solid #4CAF50; 
            }}
            QLabel {{
                color: {self.col_text}; 
                font-size: 9px; 
                background: transparent;
                border: none;
                padding: 0px; margin: 0px; 
            }}
            QPushButton {{
                background-color: {self.col_text};
                color: white;
                border: none;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: ; }}
        '''
    def panel_style(self):
        return f'''
        QPushButton {{
            background-color: {self.col_secondary};
            color: {self.col_text};
            border: 2px solid {self.col_border};
            border-radius: 10px; /* Makes it a circle if size is 20x20 */
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {self.col_hover};
        }}
        '''
    
    def settings_button_style(self):
        return f''' 
        QPushButton {{
            background-color: {self.col_secondary};
            color: {self.col_text};
            border: 2px solid {self.col_border};
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {self.col_hover};
        }}'''
    
    def bottom_button_style(self):
        return f"""
            QPushButton {{
                background-color: {self.col_text};
                border: 2px solid {self.col_text};
                border-bottom: none; 
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                color: {self.col_primary};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.col_hover};
                border-color: {self.col_hover};
            }}"""

    def side_button_style(self):
        return f"""
            QPushButton {{
                background-color: {self.col_text};
                border: 2px solid {self.col_text};
                border-right: none; 
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
                color: {self.col_primary};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.col_hover};
                border-color: {self.col_hover};
            }}
        """

    def input_page_style(self):
        return f"""
            QSlider::groove:horizontal {{
                border: 1px solid {self.col_border};
                height: 8px;
                background: {self.col_secondary};
                margin: 2px 0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {self.col_text};
                border: 1px solid {self.col_border};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {self.col_border};
                border-radius: 5px;
                background: {self.col_secondary};
            }}
            QCheckBox::indicator:checked {{
                background: {self.col_text};
            }}
        """

### STORE_HEADER ###
class store_header(QWidget):
    '''reusable nav bar for home button and money disp'''
    home_clicked = pyqtSignal() #used for nav in the main

    def __init__(self, styles):
        super().__init__()
        self.styles = styles 
        self.setStyleSheet("border: none;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(15) 

        self.btn_home = QPushButton("🏠︎") 
        self.btn_home.setFixedSize(50, 50) 
        self.btn_home.setCursor(Qt.CursorShape.PointingHandCursor) 
        self.btn_home.setToolTip("Home") 
        self.btn_home.setStyleSheet(self.styles.header_button_style()) 
        self.btn_home.clicked.connect(self.home_clicked.emit) 

        self.lbl_money = QLabel("$0") #from the database
        self.lbl_money.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.lbl_money.setFixedSize(150, 50) 
        self.lbl_money.setStyleSheet(f"""
            background-color: {self.styles.col_secondary};
            border: 2.5px solid {self.styles.col_text};
            border-radius: 12px;
            font-weight: 900;
            font-size: 18px;
            color: {self.styles.col_text};
        """) 
        layout.addWidget(self.btn_home) 
        layout.addStretch() 
        layout.addWidget(self.lbl_money) 

    def update_money(self, amount):
        self.lbl_money.setText(f"${amount}")

### HORIZONTAL SCROLL AREA ###
class HorizontalScrollArea(QScrollArea):
    '''custom area to allow horizontal scrolling'''
    def wheelEvent(self, event):
      """Enable horizontal scrolling with mouse wheel"""
      delta = event.angleDelta().y()
      if delta != 0:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)
            event.accept()
      else:
            return super().wheelEvent(event)
      
      
### THEME DEFAULT ###
default_theme = UniversalStyles(
    primary="#f8f8f8",
    secondary="#ffffff",
    border="#000000",
    hover="#a9a9a9",
    text="#000000",
    scroll="#888888",
    scroll_hover="#555555"
)