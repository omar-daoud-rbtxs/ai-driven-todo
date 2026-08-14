from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout, 
    QVBoxLayout, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer, QVariantAnimation, QPoint
from store_utils import store_header, HorizontalScrollArea, default_theme
import os
from PyQt6.QtGui import QPixmap

### UI COMPONENTS ###

class RoomFrame(QFrame):
    """A Frame with stable coordinates to act as the container for placed furniture"""
    def __init__(self, parent=None):
        super().__init__(parent)


class FurnitureCard(QFrame):
    '''The card for a furniture item in the sidebar'''
    def __init__(self, name, price, image_paths, parent_view, styles):
        '''Creates the furniture card UI with an image, name price and buttons for placing and buying
        input: str,int, list of str, object, object'''
        # parent_view here would be the FurnitureView which holds all the data and stuff
        super().__init__()
        self.name = name
        self.price = price
        self.parent_view = parent_view
        self.styles = styles
        self.image_paths = image_paths

        self.setFixedHeight(110)
        self.setFixedWidth(200) 
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        self.setStyleSheet(f"""
                            QFrame {{
                                background-color: {self.styles.col_secondary};
                                border: 1.5px solid {self.styles.col_border};
                                border-radius: 12px;
                            }}
                            QLabel {{ border: none; background: transparent; }}
                            """) 
        
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        self.img_lbl = QLabel()
        self.img_lbl.setFixedSize(80, 80)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Just grab the first image in the list to use as the icon
        if image_paths:
            pixmap = QPixmap(image_paths[0])
            scaled_pixmap = pixmap.scaled(75, 75, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.img_lbl.setPixmap(scaled_pixmap)
    
        layout.addWidget(self.img_lbl)

        right_layout = QWidget()
        right_layout.setStyleSheet("border: none; background: transparent;")
        right_layout_v = QVBoxLayout(right_layout)
        right_layout_v.setContentsMargins(0, 0, 0, 0)
        right_layout_v.setSpacing(2)

        top_layout = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet(f"color: {self.styles.col_text}; font-size: 11px; font-weight: bold;")
        price_lbl = QLabel(f"${price}")
        price_lbl.setStyleSheet(f"color: {self.styles.col_text}; font-size: 11px;")
        top_layout.addWidget(name_lbl)
        top_layout.addStretch()
        top_layout.addWidget(price_lbl)

        self.btn_preview = QPushButton("Place")
        self.btn_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preview.setStyleSheet(f"""
            QPushButton {{
                background: {self.styles.col_secondary};
                border: 1.5px solid {self.styles.col_text};
                border-radius: 6px;
                padding: 3px;
                color: {self.styles.col_text};
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{ background: {self.styles.col_hover};}}
        """)
        
        # We use a lambda here to pass arguments (name, paths) to the function. 
        # Without lambda function would run immediately when the button is created.
        self.btn_preview.clicked.connect(lambda: self.parent_view.place_item(self.name, self.image_paths))

        self.btn_buy = QPushButton("Buy")
        self.btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buy.setStyleSheet(self.styles.button_style() + "font-size: 11px; padding: 3px;")
        self.btn_buy.clicked.connect(self.buy_item)

        right_layout_v.addLayout(top_layout)
        right_layout_v.addWidget(self.btn_preview)
        right_layout_v.addWidget(self.btn_buy)

        layout.addWidget(right_layout, 1)
        self.update_ownership()

    def update_ownership(self):
        '''checks user inventory and update card visually'''
        count = self.parent_view.game_data.inventory_furniture.count(self.name)
        if count > 0:
            self.btn_buy.setText(f"Buy ({count} Owned)")
        else:
            self.btn_buy.setText("Buy")
    
    def buy_item(self):
        '''triggers the purchase logic from parent view'''
        success = self.parent_view.attempt_purchase(self.name, self.price)
        if success: self.update_ownership()

### MAIN INTERFACE ###

class FurnitureView(QWidget):
    request_clothing_view = pyqtSignal()
    request_home_view = pyqtSignal()
    request_save_layout = pyqtSignal(list, list)
    money_changed = pyqtSignal(int)

    def __init__(self, game_data):
        '''Initialize main view, loads in assets and builds the UI
        input: object'''
        super().__init__()
        self.game_data = game_data
        self.styles = default_theme

        self.furniture_items = self.load_item_image()
        self.init_ui()

    def init_ui(self):
        '''Constructs layout: sidebar, bottom bar, room area'''
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10) 
        self.main_layout.setSpacing(10)

        # Container for the top section (Left Room + Right Sidebar)
        self.preview = QFrame()
        self.preview.setStyleSheet(self.styles.frame_style())

        preview_layout = QHBoxLayout(self.preview)
        preview_layout.setContentsMargins(15, 15, 15, 15)

        # Left side (header and room)
        left = QWidget()
        left.setStyleSheet("border: none;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.header = store_header(self.styles)
        self.header.setFixedHeight(50) 
        self.header.home_clicked.connect(self.request_home_view.emit)

        title_row = QWidget()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Furniture Shop")
        title.setStyleSheet(f"color: {self.styles.col_text}; font-size: 18px; font-weight: bold; border: none;")
        
        self.btn_save = QPushButton('Save Changes')
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(self.styles.button_style() + "font-size: 12px; padding: 5px 15px;")
        self.btn_save.clicked.connect(self.save_layout)

        title_row_layout.addWidget(title)
        title_row_layout.addStretch()
        title_row_layout.addWidget(self.btn_save)   

        self.room_container = QWidget()
        self.room_container.setStyleSheet("background: transparent; border: none;")
        
        # The room_area is the floor where items are placed.
        # It's inside room_container but we move it manually
        self.room_area = RoomFrame(self.room_container)
        self.room_area.setFixedSize(1000, 700) 
        self.room_area.setStyleSheet(f'background-color: transparent;')
        
        self.btn_go_clothing = QPushButton("Browse Clothing")
        self.btn_go_clothing.setFixedHeight(45) 
        self.btn_go_clothing.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_go_clothing.setStyleSheet(self.styles.action_button_style())
        self.btn_go_clothing.clicked.connect(self.request_clothing_view.emit)

        left_layout.addWidget(self.header)
        left_layout.addWidget(title_row)
        left_layout.addWidget(self.room_container, 1) 
        left_layout.addWidget(self.btn_go_clothing)
        self.update_room_pos_from_size()

        # right side (sidebar)
        self.side_container = QWidget()
        self.side_container.setStyleSheet("border: none;")
        side_layout = QHBoxLayout(self.side_container)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(10)

        self.btn_open_side = QPushButton()
        self.btn_open_side.setFixedSize(7, 70)
        self.btn_open_side.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_side.setStyleSheet(f"background:{self.styles.col_text}; border-radius:3px; border:none;")
        self.btn_open_side.clicked.connect(self.toggle_sidebar)

        self.sidebar_scroll = HorizontalScrollArea()
        self.sidebar_scroll.setFixedWidth(0) # Start closed (width 0)
        self.sidebar_scroll.setWidgetResizable(True)
        self.sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.sidebar_scroll.setStyleSheet(f"{self.styles.frame_style()} {self.styles.scrollbar_style()}")

        inner = QWidget()
        inner.setStyleSheet("background: transparent; border: none;")
        self.sidebar_layout = QVBoxLayout(inner)
        self.sidebar_layout.setContentsMargins(8, 5, 8, 10)
        self.sidebar_layout.setSpacing(8)

        title_lbl = QLabel("Variants")
        title_lbl.setFixedHeight(25)
        title_lbl.setStyleSheet(f"color: {self.styles.col_text}; font-size: 16px; font-weight: bold; border: none;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(title_lbl)

        self.sidebar_scroll.setWidget(inner)

        side_layout.addWidget(self.btn_open_side)
        side_layout.addWidget(self.sidebar_scroll)

        preview_layout.addWidget(left, 1)
        preview_layout.addWidget(self.side_container)

        # Bottom (category area)
        self.bottom = QWidget()
        self.bottom.setStyleSheet("border: none;")
        bottom_layout = QVBoxLayout(self.bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        frame = QFrame()
        frame.setStyleSheet(self.styles.frame_style())
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 5, 0, 5) 

        grabber = QPushButton()
        grabber.setFixedSize(60, 5) 
        grabber.setCursor(Qt.CursorShape.PointingHandCursor) 
        grabber.setStyleSheet(f"background:{self.styles.col_text}; border-radius:2px; border:none;")
        grabber.clicked.connect(self.toggle_bottom)
        
        self.scroll_container = QWidget()
        self.scroll_container.setMaximumHeight(0) # Start closed (height 0)
        self.scroll_container.setStyleSheet("background: transparent; border: none;")
        scroll_cont_layout = QVBoxLayout(self.scroll_container)
        scroll_cont_layout.setContentsMargins(0,0,0,0)

        self.scroll = HorizontalScrollArea()
        self.scroll.setFixedHeight(115) 
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        cat_widget = QWidget()
        cat_widget.setStyleSheet("background: transparent; border: none;")
        cat_layout = QHBoxLayout(cat_widget)
        cat_layout.setContentsMargins(15, 0, 15, 0)
        cat_layout.setSpacing(10)
        cat_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for category in self.furniture_items:
            btn = QPushButton(category)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumSize(100, 65) 
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet(f"""
                QPushButton {{ 
                    background: {self.styles.col_primary}; 
                    border: 1.5px solid {self.styles.col_border}; 
                    border-radius: 12px; 
                    font-weight: 800; 
                    color: {self.styles.col_text};
                    font-size: 13px;
                }}
                QPushButton:hover {{ background: {self.styles.col_hover}; }}
            """)
            # we use 'cat=category' inside the lambda to capture the CURRENT value of category
            # If we just did lambda:load(category), every button loads the last category in the loop.
            # the _, is throwaway variable bec btns return info we dont use
            btn.clicked.connect(lambda _, cat=category: self.load_category(cat)) 
            cat_layout.addWidget(btn)
        
        self.scroll.setWidget(cat_widget)
        scroll_cont_layout.addWidget(self.scroll)

        frame_layout.addWidget(grabber, 0, Qt.AlignmentFlag.AlignHCenter)
        frame_layout.addWidget(self.scroll_container)

        bottom_layout.addWidget(frame)
        
        self.main_layout.addWidget(self.preview, 1)
        self.main_layout.addWidget(self.bottom)

    def get_default_pos(self):
        '''calc the default position based on window size
        output: tuple (int,int)'''
        if self.width() < 1300:
            return -10, 0
        return 100, 60

    def update_room_pos_from_size(self):
        '''updates room frame position when window starts or initializes'''
        x, y = self.get_default_pos()
        self.room_area.move(x, y)

    def toggle_sidebar(self):
        '''Animates opening closing of the right sidebar and adjusts the rooms position'''
        cur = self.sidebar_scroll.width()
        target = 230 if cur == 0 else 0 
        
        def_left, _ = self.get_default_pos()
        start_pos = self.room_area.pos()
        
        # Calculate where the room should move to when sidebar opens
        if def_left > 0:
            open_x = 20
        else:
            open_x = def_left - 150
            
        target_x = open_x if cur == 0 else def_left
        target_pos = QPoint(target_x, start_pos.y())

        self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Animate Width changes
        self.anim1 = QPropertyAnimation(self.sidebar_scroll, b"minimumWidth")
        self.anim2 = QPropertyAnimation(self.sidebar_scroll, b"maximumWidth")
        
        # Animate Room Position (Sliding it over)
        self.pos_anim = QPropertyAnimation(self.room_area, b"pos")
        self.pos_anim.setDuration(450)
        self.pos_anim.setStartValue(start_pos)
        self.pos_anim.setEndValue(target_pos)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutQuint) 

        for a in (self.anim1, self.anim2):
            a.setDuration(450)
            a.setStartValue(cur)
            a.setEndValue(target)
            a.setEasingCurve(QEasingCurve.Type.OutQuint)
            a.finished.connect(lambda: self.on_side_anim_finished(target))
            a.start()
        
        self.pos_anim.start()

    def toggle_bottom(self):
        '''Aniated the bottom panel and positions the room properly'''
        cur = self.scroll_container.maximumHeight()
        target = 130 if cur == 0 else 0 
        
        _, def_top = self.get_default_pos()
        start_pos = self.room_area.pos()
        
        # Shift room up if bottom panel opens
        target_y = (def_top - 100) if cur == 0 else def_top
        target_pos = QPoint(start_pos.x(), target_y)

        self.anim_bot = QPropertyAnimation(self.scroll_container, b"maximumHeight")
        self.anim_bot.setDuration(500)
        self.anim_bot.setStartValue(cur)
        self.anim_bot.setEndValue(target)
        self.anim_bot.setEasingCurve(QEasingCurve.Type.OutQuint)
        
        self.pos_bot_anim = QPropertyAnimation(self.room_area, b"pos")
        self.pos_bot_anim.setDuration(500)
        self.pos_bot_anim.setStartValue(start_pos)
        self.pos_bot_anim.setEndValue(target_pos)
        self.pos_bot_anim.setEasingCurve(QEasingCurve.Type.OutQuint)

        self.anim_bot.start()
        self.pos_bot_anim.start()
    
    def on_side_anim_finished(self, target):
        '''makes scrollbars work after animiation finishes'''
        if target > 0: self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def resizeEvent(self, event):
        '''makes sure the room is centered even when the window is resized'''
        # Only center if panels are closed, otherwise it ruin anim
        if self.sidebar_scroll.width() == 0 and self.scroll_container.maximumHeight() == 0:
            self.update_room_pos_from_size()
        super().resizeEvent(event)

    def load_category(self, category):
        ''' puts the furniture cards inside sidepanel, for each category
        input: str'''
        if self.sidebar_scroll.width() == 0: self.toggle_sidebar() 
        
        # Clean up old items: Loop backwards or check count to remove widgets
        # We skip index 0 because thats the  title label
        while self.sidebar_layout.count() > 1: 
            item = self.sidebar_layout.takeAt(1).widget()
            if item: item.deleteLater()
            
        for item_data in self.furniture_items.get(category):
            name = item_data[0]
            price = item_data[1]
            path = item_data[2]
            card = FurnitureCard(name, price, path, self, self.styles) 
            self.sidebar_layout.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter) 

    def update_game_data(self, data):
        '''updates reference to gamedata
        input: object'''
        self.game_data = data      

    def refresh_page(self, data):
        '''refreshes displays based on new data'''
        self.header.update_money(self.game_data.money)
        self.update_game_data(data)
        # Update every card in the sidebar to show correct "Owned" count
        for i in range(1, self.sidebar_layout.count()):
            widget = self.sidebar_layout.itemAt(i).widget()
            if isinstance(widget, FurnitureCard):
                widget.update_ownership()
        
    def show_error_message(self, text, slot=0):
        '''displays temp error msg label
        input: str, int'''
        existing_same_msg = [c for c in self.room_area.findChildren(QLabel) if c.text() == text and c.isVisible()]
        if existing_same_msg: return

        lbl = QLabel(text, self.room_area)
        lbl.setStyleSheet(f"color: red; font-size: 20px; font-weight: bold; border: none; background: transparent;")
        lbl.adjustSize()
        
        base_x = (self.room_area.width() - lbl.width()) // 2
        base_y = (self.room_area.height() - lbl.height()) // 2
        
        offset = slot * 35
        lbl.move(base_x, base_y - offset)
        lbl.show()
        # Kill the label after 2 seconds
        QTimer.singleShot(2000, lbl.deleteLater)

    def attempt_purchase(self, item_name, item_price):
        '''makes sure user has enough money and processes the purchase
        input: str,int
        output: bool'''
        if self.game_data.money >= item_price:
            self.game_data.money -= item_price
            self.game_data.inventory_furniture.append(item_name)
            self.refresh_page(self.game_data) 
            self.money_changed.emit(self.game_data.money)
            return True
        else:
            self.show_error_message('Insufficient Funds', slot=0)
            return False
        
    def place_item(self, item_name, image_paths):
        '''Makes an item a Draggable furniture if the user has it in their inventor
        input: str, list of str'''
        placed_list = self.game_data.placed_furniture
        owned_qty = self.game_data.inventory_furniture.count(item_name)
        # Count how many of the item are already on the floor
        placed_qty = sum(1 for item in placed_list if item['name'] == item_name)
        
        if owned_qty == 0:
            self.show_error_message('Item not owned', slot=1)
            return
        
        if placed_qty < owned_qty:
            # Calculate Z index so new item appears on top (max z + 1)
            current_max_z = max((item.get('z', 0) for item in self.game_data.placed_furniture), default=0)
            new_item_data = {'name': item_name, 'angle_index': 0, 'x': 0, 'y': 0, 'z': current_max_z + 1}
            self.game_data.placed_furniture.append(new_item_data)
            
            # Create the draggable object
            item_lbl = DraggableFurniture(self.room_area, image_paths, new_item_data, self)
            item_lbl.setStyleSheet("border: none; background: transparent;")
            item_lbl.show()
            self.refresh_z_order()

            center_x = (self.room_area.width() - item_lbl.width()) // 2 
            center_y = (self.room_area.height() - item_lbl.height()) // 2 
            item_lbl.move(center_x, center_y)

            new_item_data['x'] = center_x
            new_item_data['y'] = center_y
            self.refresh_page(self.game_data) 
        else:
            self.show_error_message(f'All {item_name}s placed', slot=1)
    
    def load_item_image(self):
        '''get info from the assets in the asset library and builds the store categories
        output: dict with list of tuples'''
        assets_folder = "assets"
        data = {}
        grouped_items = {} 

        if not os.path.exists(assets_folder):
            return {} 
        
        valid_file_types = ('.png')
        for filename in os.listdir(assets_folder):
            if filename.lower().endswith(valid_file_types):
                name_no_extension = os.path.splitext(filename)[0] 
                parts = name_no_extension.split('_')

                # Logic to extract price andname based on filename structure
                if len(parts) >= 4 and parts[-1].isdigit() and len(parts[-1]) == 1 and parts[-2].isdigit():
                    category = parts[0]
                    try: price = int(parts[-2])
                    except ValueError: price = 0
                    name = ' '.join(parts[1:-2])
                elif len(parts) >= 3:
                    category = parts[0]
                    try: price = int(parts[-1])
                    except ValueError: price = 0
                    name = ' '.join(parts[1:-1])
                else: continue

                if 'Floor' in name or 'Wall' in name: continue

                key = (category, name, price)
                full_path = os.path.join(assets_folder, filename) 
                if key not in grouped_items: grouped_items[key] = []
                grouped_items[key].append(full_path)

        for (cat, name, price), paths in grouped_items.items():
            paths.sort() 
            if cat not in data: data[cat] = []
            data[cat].append((name, price, paths))
        return data   
      
    def save_layout(self):
        '''ouptuts a signal withh the current inventory and what items are placed'''
        self.request_save_layout.emit(self.game_data.inventory_furniture, self.game_data.placed_furniture)    

    def load_layout(self, data=None):
        '''gets the placed items from saved items and sorts by Z index
        input: list of dict'''
        placed_data = data
        if not placed_data: return
        placed_data.sort(key=lambda x: x.get('z', 0))

        for item_data in placed_data:
            image_paths = []
            # Find the images for this item name
            for category, items in self.furniture_items.items():
                for name, price, paths in items:
                    if name == item_data['name']:
                        image_paths = paths
                        break
                if image_paths: break
            if not image_paths:
                image_paths = self.get_specific_item_images(item_data['name'])

            if image_paths:
                item_lbl = DraggableFurniture(self.room_area, image_paths, item_data, self)
                item_lbl.show()
    
    def refresh_z_order(self):
        '''Stack widgets in the right order based on z axis'''
        widgets = self.room_area.findChildren(DraggableFurniture)
        # Stack widgets in the right order based on z axis using .raise_()
        sorted_widgets = sorted(widgets, key=lambda w: w.item_data.get('z', 0))
        for w in sorted_widgets: w.raise_()

    def get_specific_item_images(self, item_name):
        '''gets images if items are locked 
        input: str
        output: list of str'''
        assets_folder = 'assets'
        paths = []
        if not os.path.exists(assets_folder): return []
        for filename in os.listdir(assets_folder):
            if item_name in filename and filename.endswith('.png'):
                paths.append(os.path.join(assets_folder, filename))
        paths.sort()
        return paths

    def clear_room_area(self):
        '''removes draggable items from room'''
        widgets = self.room_area.findChildren(DraggableFurniture)
        for w in widgets: w.deleteLater()               
    
### INTERACTIV OBJECTS ###

class DraggableFurniture(QLabel):
    '''The actual item in the room handles the dragging, rotating and deleting'''
    def __init__(self, parent, image_paths, item_data, main_view):
        '''initializes the draggable item, sets the cursors look, loads the right image
        input: QWidget, List of str, dict, object'''
        super().__init__(parent)
        self.image_paths = image_paths 
        self.item_data = item_data
        self.angle_index = self.item_data.get('angle_index', 0)
        self.drag_start_position = None
        self.parent_view = main_view 
        self.scale_factor = 0.8
        # Items with "Floor" or "Wall" in name cannot be moved by user
        self.is_locked = "Floor" in self.item_data['name'] or "Wall" in self.item_data['name']
        
        if 'z' not in self.item_data: self.item_data['z'] = 0
        if not self.is_locked: self.setCursor(Qt.CursorShape.OpenHandCursor)
        else: self.setCursor(Qt.CursorShape.ArrowCursor)

        self.setStyleSheet("border: none; background: transparent;")
        self.update_image()
        # If we have saved coordinates, restore them
        if 'x' in self.item_data and 'y' in self.item_data:
            self.move(self.item_data['x'], self.item_data['y'])

    def update_image(self):
        '''updates the image displayed based on the current rotated version'''
        if not self.image_paths: return 
        current_image_path = self.image_paths[self.angle_index]
        if os.path.exists(current_image_path):
            pix = QPixmap(current_image_path)
            new_w = int(pix.width() * self.scale_factor)
            new_h = int(pix.height() * self.scale_factor)
            self.setFixedSize(new_w, new_h)
            self.setPixmap(pix.scaled(new_w, new_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def rotate(self):
        ''' goes thru the available images to make it look like its rotating'''
        if len(self.image_paths) > 1:
            # Use modulo (%) so if index is 3 and len is 4, 4%4 becomes 0 (loops back to start)
            self.angle_index = (self.angle_index + 1) % len(self.image_paths) 
            self.item_data['angle_index'] = self.angle_index
            self.update_image()

    def mousePressEvent(self, event):
        '''handles the logic when u click with mouse, this is overriding the og function inherited from QWidget which is inherted by Qlabel
         input: object, built into PyQt6 instance from QMouseEvent '''
        if self.is_locked: return
        self.setFocus()
        if event.button() == Qt.MouseButton.LeftButton: # this is Enum, Qt is the library, MouseButton is the Enum class, LeftButton is enum member
            self.drag_start_position = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rotate()
    
    def mouseMoveEvent(self, event):
        '''Calc the new pos during dragging, but makes sure it stays within boundaries'''
        if self.is_locked: return
        # Ensure left button is held AND we have a start position
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_start_position: 
            delta = event.pos() - self.drag_start_position
            target_pos = self.pos() + delta
            
            # Boundary calcs
            parent_rect = self.parentWidget()
            max_x = parent_rect.width() - self.width()
            max_y = parent_rect.height() - self.height()
            
            # Clamp the values so item doesn't fly off screen
            safex = max(0, min(target_pos.x(), max_x))
            safey = max(0, min(target_pos.y(), max_y))
            
            self.move(safex, safey)
            self.item_data['x'] = safex
            self.item_data['y'] = safey

    def mouseReleaseEvent(self, event):
        '''Resets the cursor and drag state when mouse is realease'''
        if self.is_locked: return
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.drag_start_position = None

    def mouseDoubleClickEvent(self, event):
        '''Brings item to front by incrementing the z value'''
        if self.is_locked: return
        if event.button() == Qt.MouseButton.LeftButton:
            siblings = self.parentWidget().findChildren(DraggableFurniture)
            current_max_z = 0
            # Find the highest Z currently in the room
            for sib in siblings:
                z = sib.item_data.get('z', 0)
                if z > current_max_z: current_max_z = z
            
            # Set this item to max + 1 so it on top
            self.item_data['z'] = current_max_z + 1
            self.raise_()

    def delete_item(self):
        '''remove item from placed furniture'''
        if self.item_data in self.parent_view.game_data.placed_furniture:
            self.parent_view.game_data.placed_furniture.remove(self.item_data)
            self.deleteLater()

    def keyPressEvent(self, event):
        '''waits for the delete or backspace to trigger dletion'''
        if self.is_locked: return
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.delete_item()