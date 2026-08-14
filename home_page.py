from PyQt6.QtWidgets import (QWidget, 
                             QPushButton, QLabel, QGraphicsScene, 
                             QGraphicsView, QGraphicsPixmapItem, 
                             QVBoxLayout, QFrame, QHBoxLayout, 
                             QSizePolicy, QDialog, QGridLayout, 
                             QCheckBox, QScrollArea,QLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRectF
from PyQt6.QtGui import QPixmap
from store_utils import default_theme
import os


### MAIN SCENE ###
class RoomScene(QWidget):
    '''main container for viewing game, has camera and side and bottom panels'''

    #signals for navigation
    logout_signal = pyqtSignal()
    request_clothing_store = pyqtSignal()
    request_furniture_store = pyqtSignal()
    request_task_entry = pyqtSignal()
    request_task_status_update = pyqtSignal(int, int) 
    request_subtask_status_update = pyqtSignal(object, int, int, int)
    request_task_removal = pyqtSignal(int)

    def __init__(self, game_data):
        '''builds cameraview and panels
        input: object'''
        super().__init__()
        self.game_data = game_data
        self.setMinimumSize(1280, 720)
        self.styles = default_theme

        #main layout (center area and side panel)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        #center container(camera bottom panel)
        self.center_container = QWidget()
        self.center_layout = QVBoxLayout(self.center_container)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(0)

        #where items r placed
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(100, -40, 1080, 520)

        self.camera = Camera(self.scene, self.styles)
        self.camera.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.camera.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)   
        
        #buttons that toggle side and bottom panel
        self.camera.bottom_btn.clicked.connect(self.toggle_bottom)
        self.camera.side_btn.clicked.connect(self.toggle_side)

        self.setup_bottom_panel()
        # Widgets to center layout
        self.center_layout.addWidget(self.camera)
        self.center_layout.addWidget(self.bottom_panel)
        self.setup_side_panel()
        #main section to horizontal lauot
        self.main_layout.addWidget(self.center_container)
        self.main_layout.addWidget(self.side_panel)

        self.camera.req_settings.connect(self.setup_settings)
        self.refresh_view(self.game_data)

    def update_game_data(self, data):
        ''' connects game data
        input: object'''
        self.game_data = data

    def setup_side_panel(self):
        '''makes expandable size panel that has the task list'''
        self.side_panel = QFrame()
        self.side_panel.setFixedWidth(350)
        self.side_panel.setStyleSheet(self.styles.panel_style())
        
        layout = QVBoxLayout(self.side_panel)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 15, 10, 15)

        lbl = QLabel('TASKS')
        lbl.setStyleSheet(f"font-weight: 900; font-size: 18px; color: {self.styles.col_text}; border: none;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl) 

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(self.styles.scrollbar_style())
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.card_container = QWidget()
        self.card_container.setStyleSheet("background: transparent;")
        
        self.card_container_layout = QVBoxLayout(self.card_container)
        self.card_container_layout.setSpacing(10)
        self.card_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        task_entry_nav = QPushButton('Add Task')
        task_entry_nav.setCursor(Qt.CursorShape.PointingHandCursor)
        task_entry_nav.setFixedSize(280, 40)
        task_entry_nav.setStyleSheet(self.styles.action_button_style())
        task_entry_nav.clicked.connect(self.request_task_entry.emit)

        self.scroll_area.setWidget(self.card_container)
        layout.addWidget(self.scroll_area)

        layout.addWidget(task_entry_nav, 0, Qt.AlignmentFlag.AlignHCenter)        
    
    def setup_bottom_panel(self):
        '''makes bottom panel with the nav buttons'''
        self.bottom_panel = QFrame()
        self.bottom_panel.setMaximumHeight(70)
        self.bottom_panel.setStyleSheet(self.styles.panel_style())

        layout = QHBoxLayout(self.bottom_panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 10, 20, 10)

        btn1 = QPushButton('Clothing Store')
        btn1.setCursor(Qt.CursorShape.PointingHandCursor)
        btn1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn1.setStyleSheet(self.styles.button_style())
        btn1.clicked.connect(self.request_clothing_store.emit)

        btn2 = QPushButton('Furniture Store')
        btn2.setCursor(Qt.CursorShape.PointingHandCursor)
        btn2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn2.setStyleSheet(self.styles.button_style())
        btn2.clicked.connect(self.request_furniture_store.emit)

        layout.addWidget(btn1)
        layout.addWidget(btn2)
    
    def setup_settings(self):
        '''opens the settings panel QDialog with logout button'''
        settings = QDialog(self)
        settings.setWindowTitle('System Settings')
        settings.setFixedSize(300, 200)
        settings.setStyleSheet(f"background: {self.styles.col_secondary}; border: 2px solid {self.styles.col_border};")
        
        layout = QVBoxLayout(settings)
        layout.setSpacing(5)
        layout.setContentsMargins(20, 20, 20, 20)
        
        logout_btn = QPushButton('Logout ➜')
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        logout_btn.setFixedHeight(50)
        logout_btn.setStyleSheet(self.styles.action_button_style())
        logout_btn.clicked.connect(settings.accept)

        layout.addStretch()
        layout.addWidget(logout_btn)

        if settings.exec():
            self.logout()
    
    def toggle_bottom(self):
        '''Animate bottom panel'''
        cur = self.bottom_panel.maximumHeight()
        target = 70 if cur == 0 else 0
        
        self.anim_bot = QPropertyAnimation(self.bottom_panel, b"maximumHeight")
        self.anim_bot.setDuration(500)
        self.anim_bot.setStartValue(cur)
        self.anim_bot.setEndValue(target)
        self.anim_bot.setEasingCurve(QEasingCurve.Type.OutQuint)
        self.anim_bot.start()
    
    def toggle_side(self):
        '''animate sdie panel and adjusts the camera center'''
        cur = self.side_panel.width()
        target = 350 if cur == 0 else 0
        
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.anim1 = QPropertyAnimation(self.side_panel, b"minimumWidth")
        self.anim2 = QPropertyAnimation(self.side_panel, b"maximumWidth")
        
        for a in (self.anim1, self.anim2):
            a.setDuration(450)
            a.setStartValue(cur)
            a.setEndValue(target)
            a.setEasingCurve(QEasingCurve.Type.OutQuint)
            a.finished.connect(lambda: self.on_side_anim_finished(target))
            a.start()
        
        # link anim to camera 
        # prevents it from jumping to final positon by recalc centerpoint per frame
        self.anim1.valueChanged.connect(lambda: self.recenter_camera()) 

    def on_side_anim_finished(self, target):
        '''enable scrollbar when anim finsihes'''
        if target > 0:
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.recenter_camera()

    def resizeEvent(self, event):
        '''Handles the positioning when window is resized'''
        super().resizeEvent(event)
        self.update_button_positions()
        self.recenter_camera()

    def recenter_camera(self):
        '''calc offset to center room based on the sidepanel width'''
        if not self.scene.items():
            return
            
        items_rect = self.scene.itemsBoundingRect()
        center_point = items_rect.center()

        current_width = self.side_panel.width()
        if current_width > 0:
            ratio = current_width / 350.0
            offset = 5 * ratio 
            
            center_point.setX(center_point.x() + offset)

        self.camera.centerOn(center_point)

    def update_task_panel(self, user_task_list):
        '''calears and remakes the side panel
        input:list of object'''
        while self.card_container_layout.count():
            item = self.card_container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        card_list = []
        for i in range(len(user_task_list)):
            if user_task_list[i].subdivisions != 0:
                #create a card with the subtasks
                card = UserDivTaskCard(user_task_list[i])
                card.update_task_status_database.connect(self.request_task_status_update.emit)
                #cards emit signal to room scen which roomscene emits to main to do logic
                card.update_subtask_status_database.connect(
                    lambda status, subtask_id, taskid, c=card: 
                    self.request_subtask_status_update.emit(c, status, subtask_id, taskid)
                )
                card.delete_request.connect(self.request_task_removal.emit)
                card_list.append(card)
            else:
                #create a card without subtask
                card = UserTaskCard(user_task_list[i])
                card.update_task_status_database.connect(self.request_task_status_update.emit)
                card.delete_request.connect(self.request_task_removal.emit)
                card_list.append(card)

        for card in card_list:
            self.card_container_layout.addWidget(card)

    def update_divtask_label(self, card, status):
        '''update the strike through on the task headers'''
        card.update_center_label(status)
    
    def update_button_positions(self):
        '''position overlay butons on camera view'''
        y_bot = self.camera.height() - self.camera.bottom_btn.height()
        x_bot = (self.camera.width() - self.camera.bottom_btn.width()) // 2
        self.camera.bottom_btn.move(x_bot, y_bot - 5) 
        x_side = self.camera.width() - self.camera.side_btn.width()
        y_center = (self.camera.height() - self.camera.side_btn.height()) // 2
        self.camera.side_btn.move(x_side, y_center)
        margin = 10
        self.camera.settings_btn.move(margin, margin)
        
        money_x = self.camera.width() - self.camera.money_indicator.width() - margin
        self.camera.money_indicator.move(money_x, margin)

    def logout(self):
        '''emits logout sginal'''
        self.logout_signal.emit()

    def refresh_view(self, data):
        '''Refereshes money, data and reloads the furniture
        input: object'''
        self.camera.update_money(self.game_data.money)
        self.update_game_data(data)
        self.scene.clear()
        self.load_furniture()
        self.recenter_camera()

    def get_image_path(self, item_name):
        '''Find all images assets based on name
        input: str
        output: list of str'''
        assets_folder = 'assets'
        paths = []
        if not os.path.exists(assets_folder): return []
        
        for filename in os.listdir(assets_folder):
           if item_name.lower() in filename.lower() and filename.endswith('.png'):
                paths.append(os.path.join(assets_folder, filename))
        paths.sort()
        return paths
    
    def load_furniture(self):
        '''add furniture images to scene based on pllaced furniture data'''
        scale_factor = 0.8

        for item in self.game_data.placed_furniture:
            paths = self.get_image_path(item['name'])
            if not paths: continue

            angle_idx = item.get('angle_index', 0)
            if angle_idx >= len(paths): angle_idx = 0
            path = paths[angle_idx]
            
            if path and os.path.exists(path):
                
                pix = QPixmap(path)

                new_w = int(pix.width() * scale_factor)
                new_h = int(pix.height() * scale_factor)
                scaled_pix = pix.scaled(
                    new_w, new_h, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )

                pix_item = QGraphicsPixmapItem(scaled_pix)
                pix_item.setPos(item['x'], item['y'])
                pix_item.setZValue(item.get('z', 0))
                self.scene.addItem(pix_item)

class Camera(QGraphicsView):
    '''A custom QgraphicsView that acts as camera for scene'''
    req_settings = pyqtSignal()
    def __init__(self, scene, styles):
        '''init view and overla buttons
        input:QGraphicsene, object'''
        super().__init__(scene)
        self.styles = styles
        self.margin = 10

        self.bottom_btn = QPushButton('─', self)
        self.bottom_btn.setFixedSize(60, 20) 
        self.bottom_btn.setStyleSheet(self.styles.bottom_button_style())
        self.bottom_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.side_btn = QPushButton('〡', self)
        self.side_btn.setFixedSize(20, 60)
        self.side_btn.setStyleSheet(self.styles.side_button_style())
        self.side_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.settings_btn = QPushButton('⏣', self)
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setStyleSheet(self.styles.settings_button_style())
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self.req_settings.emit)

        self.money_indicator = QLabel('$0', self)
        self.money_indicator.setStyleSheet(self.styles.money_label_style())

        self.update_button_positions()
        self.settings_btn.move(self.margin, self.margin)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        self.money_indicator.move(self.settings_btn.width()+self.margin, self.margin)

    def update_money(self, amount):
        '''Update the visual money disp
        input: int'''
        self.money_indicator.setText(f'${amount}')
        self.money_indicator.adjustSize()
        self.update_button_positions()

    def resizeEvent(self, event):
        '''Update overlay button position when resize'''
        super().resizeEvent(event)
        self.update_button_positions()

    def update_button_positions(self):
       '''recalc new coords for buttons absed on window size'''
       margin = 10
       y_bot = self.height() - self.bottom_btn.height()
       self.bottom_btn.move((self.width() - self.bottom_btn.width()) // 2, y_bot)
       x_side = self.width() - self.side_btn.width()
       self.side_btn.move(x_side, (self.height() - self.side_btn.height()) // 2)
       self.settings_btn.move(margin, margin)
       money_x = self.width() - self.money_indicator.width() - margin
       self.money_indicator.move(money_x, margin) 
    
    def mousePressEvent(self, event):
        '''override mousepress to keep curso consisten'''
        super().mousePressEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        '''override mousepress to keep curso consisten'''
        super().mouseReleaseEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

### TASK CARDS ###

class UserTaskCard(QFrame):
    ''' taks card widget for side bar'''
    update_task_status_database = pyqtSignal(int, int)
    delete_request = pyqtSignal(int)

    def __init__(self, user_task):
        '''constructs task card UI
        input:object'''
        super().__init__()
        self.setObjectName("Card") 
        self.setFixedSize(305, 65) 
        self.styles = default_theme
        
        self.taskid = user_task.taskid

        self.setStyleSheet(self.styles.task_style())

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 2, 5, 2)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1) 
        layout.setRowStretch(2, 0)

        self.reward_label = QLabel(f"${user_task.reward}")
        self.reward_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.reward_label, 0, 2, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        self.checkbox = QCheckBox(f'{user_task.name}')
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setChecked(True if user_task.status == 1 else False)
        font = self.checkbox.font()
        font.setStrikeOut(self.checkbox.isChecked())
        self.checkbox.setFont(font)
        layout.addWidget(self.checkbox, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.checkbox.toggled.connect(self.task_status_updated)

        self.time_due_label = QLabel(f"{user_task.time_due}" if user_task.deadline != 0 else "")
        self.time_due_label.setStyleSheet("padding-left: 2px;") 
        layout.addWidget(self.time_due_label, 2, 0, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        self.date_due_label = QLabel(f"{user_task.date_due}" if user_task.deadline != 0 else "")
        layout.addWidget(self.date_due_label, 2, 2, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        self.delete_btn = QPushButton("✕")
        self.delete_btn.setFixedSize(25, 25)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.delete_btn.setStyleSheet('background-color: transparent; color: #ff6666; font-size: 18px; border: none; font-weight: 900;')
        layout.addWidget(self.delete_btn, 1, 2,  alignment=Qt.AlignmentFlag.AlignCenter)

        self.delete_btn.clicked.connect(lambda: self.delete_request.emit(self.taskid))

        layout.setColumnStretch(0, 1) 
        layout.setColumnStretch(1, 0) 
        layout.setColumnStretch(2, 0)

    def task_status_updated(self, checked):
        '''emit signal to ubdate dtabase and strike out text
        input: bool'''
        self.update_task_status_database.emit(int(checked), self.taskid)
        font = self.checkbox.font()
        font.setStrikeOut(checked)
        self.checkbox.setFont(font)

class UserDivTaskCard(QFrame):
    '''task card widget with subtasks'''
    update_task_status_database = pyqtSignal(int, int)
    update_subtask_status_database = pyqtSignal(int, int, int)
    delete_request = pyqtSignal(int)

    def __init__(self, user_task):
        '''make task card UI
        input: object'''
        super().__init__()
        self.setObjectName("Card") 
        self.setFixedWidth(305)
        self.styles = default_theme
        
        self.taskid = user_task.taskid
        self.full_task_status = user_task.status

        self.setStyleSheet(self.styles.task_style())

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        #fix layout to fit around children to make it shrink back down ithout space in scroll area
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        main_card_container = QWidget()
        main_card_container.setFixedSize(305, 65)
        main_card_layout = QGridLayout(main_card_container)
        main_card_layout.setSpacing(0)
        main_card_layout.setContentsMargins(5, 2, 5, 2)

        main_card_layout.setRowStretch(0, 0)
        main_card_layout.setRowStretch(1, 1) 
        main_card_layout.setRowStretch(2, 0)

        self.reward_label = QLabel(f"${user_task.reward}")
        self.reward_label.setStyleSheet("padding-right: 5px; font-weight: bold;")
        main_card_layout.addWidget(self.reward_label, 0, 2, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        self.center_container = QWidget()
        self.center_container_layout = QHBoxLayout(self.center_container)
        self.center_container_layout.setSpacing(5)
        self.center_container_layout.setContentsMargins(5, 0, 0, 0)
        
        self.menu_btn = QPushButton("►")
        self.menu_btn.setFixedSize(18, 18)
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.clicked.connect(self.toggle_subtask_container)

        self.center_label = QLabel(f'{user_task.name}')
        self.center_label.setStyleSheet('spacing: 8px; font-size: 14px; background: transparent; border: none; font-weight: bold;')
        font = self.center_label.font()
        font.setStrikeOut(bool(user_task.status))
        self.center_label.setFont(font)

        self.center_container_layout.addWidget(self.menu_btn)
        self.center_container_layout.addWidget(self.center_label)
        main_card_layout.addWidget(self.center_container, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.time_due_label = QLabel(f"{user_task.time_due}" if user_task.deadline != 0 else "")
        self.time_due_label.setStyleSheet("padding-left: 2px;") 
        main_card_layout.addWidget(self.time_due_label, 2, 0, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        self.date_due_label = QLabel(f"{user_task.date_due}" if user_task.deadline != 0 else "")
        self.date_due_label.setStyleSheet("padding-right: 5px;")
        main_card_layout.addWidget(self.date_due_label, 2, 2, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        self.delete_btn = QPushButton("✕")
        self.delete_btn.setFixedWidth(25)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.delete_btn.setStyleSheet('background-color: transparent; color: #ff6666; font-size: 18px; border: none; font-weight: 900;')
        main_card_layout.addWidget(self.delete_btn, 1, 2,  alignment=Qt.AlignmentFlag.AlignCenter)

        self.delete_btn.clicked.connect(lambda: self.delete_request.emit(self.taskid))

        main_card_layout.setColumnStretch(0, 1) 
        main_card_layout.setColumnStretch(1, 0) 
        main_card_layout.setColumnStretch(2, 0)

        self.subtasks_container = QWidget()
        self.subtasks_container.setStyleSheet(f"background: transparent; border: none {self.styles.col_border};")
        self.subtasks_container_layout = QVBoxLayout(self.subtasks_container)
        self.subtasks_container_layout.setSpacing(5)
        self.subtasks_container_layout.setContentsMargins(20, 0, 5, 10)
        self.add_checkbox_list(user_task.subtasks)

        self.subtasks_container_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        layout.addWidget(main_card_container)
        layout.addWidget(self.subtasks_container)
        self.subtasks_container.hide()
        layout.addStretch()

    def add_checkbox_list(self, subtask_list):
        '''Iterates thru subtask list and makes checkboxes
        input: list of dict'''
        for subtask in subtask_list:
            checkbox = QCheckBox(f"{subtask['name']}")
            checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
            checkbox.setChecked(True if subtask['status'] == 1 else False)
            font = checkbox.font()
            font.setStrikeOut(checkbox.isChecked())
            checkbox.setFont(font)
            #we have ti do subtask id = subtask otherwise it will take the value when the button is clicked
            checkbox.toggled.connect(
                lambda checked, subtask_id=subtask['subtask_id'], chk = checkbox: 
                self.subtask_status_updated(checked, subtask_id, chk)
                )
            self.subtasks_container_layout.addWidget(checkbox)
        self.subtasks_container_layout.addStretch()

    def subtask_status_updated(self, checked, subtask_id, checkbox):
        '''emit signal for subtask to strike through the text'''
        self.update_subtask_status_database.emit(int(checked), subtask_id, self.taskid)
        font = checkbox.font()
        font.setStrikeOut(checked)
        checkbox.setFont(font)

    def update_center_label(self, status):
        '''Update main subtask if all task are complete'''
        font = self.center_label.font()
        font.setStrikeOut(bool(status))
        self.center_label.setFont(font)

    def toggle_subtask_container(self):
        '''expand, collapse subtask list view'''
        if self.subtasks_container.isVisible():
            self.menu_btn.setText('►')
            self.subtasks_container.hide()
        else:
            self.menu_btn.setText('▼')
            self.subtasks_container.show()