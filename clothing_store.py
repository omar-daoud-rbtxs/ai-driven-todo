from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout, 
    QVBoxLayout, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap 
from store_utils import store_header, default_theme


#CLOTHING_CARD CLASS
# Represents an individual item in the shop with its name, price, and actions.
class ClothingCard(QFrame):
    def __init__(self, name, price, parent_view, styles):
        '''Initializes the individual clothing item card

        Input: str, int, ClothingView, dict
        Output: None'''
        super().__init__()
        self.name = name
        self.price = price
        self.parent_view = parent_view
        self.styles = styles

        #GUI Styling and Layout Initialization
        self.setFixedHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"QFrame {{ background-color: {self.styles.col_secondary}; border: 1.5px solid {self.styles.col_border}; border-radius: 15px; }}")
        
        layout = QHBoxLayout(self)
        info_layout = QVBoxLayout()
        
        #labels for name and price of items
        self.lbl_name = QLabel(name)
        self.lbl_price = QLabel(f"${price}")
        self.lbl_name.setStyleSheet(f"color: {self.styles.col_text}; font-size: 16px; font-weight: bold; border: none;")
        self.lbl_price.setStyleSheet(f"color: {self.styles.col_text}; font-size: 14px; border: none;")

        info_layout.addWidget(self.lbl_name)
        info_layout.addWidget(self.lbl_price)

        #buttons for interacting with the item
        btn_layout = QVBoxLayout()
        self.btn_action = QPushButton("Try") #try/wear button
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)#makes cursor into hand
        self.btn_action.clicked.connect(self.handle_action)

        self.btn_buy = QPushButton("Buy")#buy button
        self.btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buy.setStyleSheet(f"QPushButton {{ background: {self.styles.col_border}; color: {self.styles.col_primary}; border:none; border-radius: 8px; font-weight: bold; padding: 4px; }} QPushButton:hover {{ background: {self.styles.col_hover};}}")
        self.btn_buy.clicked.connect(self.buy_item)
        
        btn_layout.addWidget(self.btn_action)
        btn_layout.addWidget(self.btn_buy)

        layout.addLayout(info_layout)
        layout.addLayout(btn_layout) 
        self.update_card_state()

    #wear or try button logic acording to ownership and if already worn
    def update_card_state(self):
        '''Updates the card UI based on ownership and worn status

        Input: None
        Output: None'''
        data = self.parent_view.clothes_data
        is_owned = self.name in data.inventory_clothes
        is_active = self.name in data.worn_clothes

        if is_owned:
            self.btn_buy.setText("Owned")
            self.btn_buy.setDisabled(True)
            self.lbl_price.setText("In Inventory")
        else:
            self.btn_buy.setText("Buy")
            self.btn_buy.setEnabled(True)
            self.lbl_price.setText(f"${self.price}")

        if is_active:
            self.btn_action.setText("Take Off")
            self.btn_action.setStyleSheet(f"QPushButton {{ background: {self.styles.col_text}; border: 2px solid {self.styles.col_text}; border-radius: 8px; padding: 4px; color: {self.styles.col_secondary}; font-weight: bold; }}")
        else:
            self.btn_action.setText("Wear" if is_owned else "Try")
            self.btn_action.setStyleSheet(f"QPushButton {{ background: {self.styles.col_secondary}; border: 2px solid {self.styles.col_text}; border-radius: 8px; padding: 4px; color: {self.styles.col_text}; font-weight: bold; }}")

    #uses attempt purchase to check for buying and then updates gui acordingly.
    def buy_item(self):
        '''Attempts to buy the item and updates the card if successful

        Input: None
        Output: None'''
        if self.parent_view.attempt_purchase(self.name, self.price):
            self.update_card_state()
    
    #looks at current text of the wear/try button and desides what it does.
    def handle_action(self):
        '''Determines if the item should be worn or taken off based on button text

        Input: None
        Output: None'''
        if self.btn_action.text() == "Take Off":
            self.parent_view.unwear_item(self.name)
        else:
            self.parent_view.wear_item(self.name)

# CLOTHING_VIEW CLASS
# Main view for the clothing shop. (has the character)
class ClothingView(QWidget):
    request_furniture_view = pyqtSignal()
    request_home_view = pyqtSignal()
    checkout_completed = pyqtSignal(list, dict) 
    money_changed = pyqtSignal(int)

    def __init__(self, clothes_data, styles=default_theme): 
        '''Initializes the main clothing shop view

        Input: Data object, dict
        Output: None'''
        super().__init__()
        self.clothes_data = clothes_data
        self.styles = styles
        
        # Defines which items belong to which body part catagory
        self.category_map = {
            "Head": ["Hat", "Sunglasses", "Kanye", "Silly", "Crazy", "Bird", "Sword", "Divine_General"],
            "Torso": ["T-Shirt", "Sweater"],
            "Legs": ["Jeans", "Skirt"],
            "Feet": ["Sneakers", "Boots"]
        }

        #available items and their prices
        self.clothing_items = [
            ("T-Shirt", 20), ("Jeans", 40), ("Sweater", 60), ("Sneakers", 50),
            ("Hat", 15), ("Sunglasses", 25), ("Skirt", 70), ("Boots", 80),
            ("Kanye", 300), ("Silly", 5), ("Crazy", 70),
            ("Bird", 120), ("Sword", 230), ("Divine_General", 300)
        ]
        
        self.cards = {} 
        self.init_ui()

        # Insufficient Funds Label for when not enough money
        self.error_label = QLabel("Insufficient Funds", self.preview_container)
        self.error_label.setStyleSheet("color: red; font-size: 24px; font-weight: bold; background: transparent; border: none;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        
        self.error_timer = QTimer()
        self.error_timer.setSingleShot(True)
        self.error_timer.timeout.connect(self.error_label.hide)

    # Handles the temporary display of the error message
    def show_error(self):
        '''Shows the insufficient funds error label for a short duration

        Input: None
        Output: None'''
        self.error_label.setFixedSize(self.preview_container.size())
        self.error_label.show()
        self.error_label.raise_()
        self.error_timer.start(2000) #2 seconds

    # Synchronizes the view data with the latest game data
    def update_clothes_data(self, game_data):
        '''Updates the view with new game data

        Input: Data object
        Output: None'''
        """Called upon login or data refresh"""
        self.clothes_data = game_data
        # puts loaded equiped into actual visuals
        self.clothes_data.worn_clothes = [v for v in game_data.equipped_clothes.values() if v]
        #Updates snapshot to match current data
        self.original_outfit = dict(game_data.equipped_clothes)
        self.refresh_page()

    # Saves current worn items to the inventory and emits checkout signal
    def finalize_checkout(self):
        '''Finalizes the outfit by keeping owned items and reverting unowned tries

        Input: None
        Output: None'''
        # inventory_list is now the source of truth for owned items so its used to revert try items(let me explain this please mostafa)
        inventory_list = self.clothes_data.inventory_clothes
        current_worn = self.clothes_data.worn_clothes
        final_equipped = {}

        for category, items in self.category_map.items():
            active_preview = next((i for i in current_worn if i in items), None)
            
            if active_preview and active_preview in inventory_list:
                final_equipped[category] = active_preview
            else:
                final_equipped[category] = self.original_outfit.get(category)
        
        self.clothes_data.equipped_clothes = final_equipped
        self.clothes_data.worn_clothes = [v for v in final_equipped.values() if v]
        # OMARRRRRR 
        self.checkout_completed.emit(inventory_list, final_equipped)

    # Checks if user has enough money to buy and adds item to inventory if successful
    def attempt_purchase(self, item_name, item_price):
        '''Processes a purchase and updates the money and inventory

        Input: str, int
        Output: bool'''
        if self.clothes_data.money >= item_price:
            self.clothes_data.money -= item_price
            
            if item_name not in self.clothes_data.inventory_clothes:
                self.clothes_data.inventory_clothes.append(item_name)
            
            # DYNAMIC SNAPSHOT UPDATE
            cat = self.get_category_of(item_name)
            if cat:
                self.original_outfit[cat] = item_name

            self.money_changed.emit(self.clothes_data.money)
            self.refresh_page()
            return True
        else:
            self.show_error()
            return False#prevents change of clothes or button

    # Constructs the main user interface with preview on the left and shop on the right
    def init_ui(self):
        '''Sets up the initial GUI layout for the shop

        Input: None
        Output: None'''
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left Panel: Character Preview and Navigation
        left_container = QFrame()
        left_container.setStyleSheet(self.styles.frame_style())
        left_layout = QVBoxLayout(left_container)

        self.header = store_header(self.styles)
        self.header.home_clicked.connect(self.handle_home_click)
        left_layout.addWidget(self.header)

        # Preview Character Slots
        self.preview_container = QWidget()
        self.preview_vbox = QVBoxLayout(self.preview_container)
        self.preview_vbox.setSpacing(0)
        self.preview_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #make boxes and set their sizes acording to each body part of the character
        self.slots = {}
        dims = {"Head": (200, 154), "Torso": (200, 139), "Legs": (200, 139), "Feet": (200, 45)}
        for part, (w, h) in dims.items():
            lbl = QLabel()
            lbl.setFixedSize(w, h)
            lbl.setScaledContents(True)
            lbl.setStyleSheet("border: none; background: transparent;")
            self.slots[part] = lbl
            self.preview_vbox.addWidget(lbl)

        left_layout.addStretch()
        left_layout.addWidget(self.preview_container)
        left_layout.addStretch()

        self.btn_go_furniture = QPushButton("Browse Furniture")
        self.btn_go_furniture.setStyleSheet(self.styles.action_button_style())
        self.btn_go_furniture.setFixedHeight(60)
        self.btn_go_furniture.clicked.connect(self.handle_furniture_click)
        left_layout.addWidget(self.btn_go_furniture)

        # Right Panel: Scrollable Item Catalog
        right_container = QFrame()
        right_container.setStyleSheet(self.styles.frame_style())
        right_layout = QVBoxLayout(right_container)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(self.styles.scrollbar_style())

        item_container = QWidget()
        item_layout = QVBoxLayout(item_container)
        for name, price in self.clothing_items:
            card = ClothingCard(name, price, self, self.styles)
            item_layout.addWidget(card)
            self.cards[name] = card 

        item_layout.addStretch()
        scroll_area.setWidget(item_container)
        right_layout.addWidget(scroll_area)

        main_layout.addWidget(left_container, 2)
        main_layout.addWidget(right_container, 1)
        self.refresh_page()

    #checkout before switching to Home
    def handle_home_click(self):
        '''Finalizes checkout and emits signal to go home

        Input: None
        Output: None'''
        self.finalize_checkout()
        self.request_home_view.emit()

    #checkout before switching to Furniture
    def handle_furniture_click(self):
        '''Finalizes checkout and emits signal to go to furniture view

        Input: None
        Output: None'''
        self.finalize_checkout()
        self.request_furniture_view.emit()

    # Equips an item in the correct category slot
    def wear_item(self, item_name):
        '''Adds a specific item to the character worn list

        Input: str
        Output: None'''
        cat = self.get_category_of(item_name)
        # Update snapshot if item owned
        if item_name in self.clothes_data.inventory_clothes:
            self.original_outfit[cat] = item_name

        #Removes item of same cat before adding newest item in same cat that was just worn
        self.clothes_data.worn_clothes = [i for i in self.clothes_data.worn_clothes if self.get_category_of(i) != cat]
        self.clothes_data.worn_clothes.append(item_name)
        self.refresh_page()

    # Removes an item from the character preview and pust on the basic none outfit 
    def unwear_item(self, item_name):
        '''Removes a specific item from the character worn list

        Input: str
        Output: None'''
        cat = self.get_category_of(item_name)
        if item_name in self.clothes_data.inventory_clothes:
            self.original_outfit[cat] = None

        if item_name in self.clothes_data.worn_clothes:
            self.clothes_data.worn_clothes.remove(item_name)
        self.refresh_page()

    #function to find which body slot an item belongs to(by going through map and checking for name)
    def get_category_of(self, item_name):
        '''Finds the category slot associated with an item name

        Input: str
        Output: str or None'''
        for category, items in self.category_map.items():
            if item_name in items: return category
        return None

    # Redraws the character preview based on currently worn clothes
    def refresh_page(self): 
        '''Redraws character images and updates money/card states

        Input: None
        Output: None'''
        self.header.update_money(self.clothes_data.money)
        for part, label in self.slots.items():
            active_item = next((i for i in self.clothes_data.worn_clothes if self.get_category_of(i) == part), None)
            img_name = active_item.lower() if active_item else f"base_{part.lower()}"
            pixmap = QPixmap(f"assets/{img_name}.png")
            if not pixmap.isNull():
                label.setPixmap(pixmap)
            else:
                label.clear()
        for card in self.cards.values():
            card.update_card_state()