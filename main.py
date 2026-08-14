from PyQt6.QtWidgets import (QApplication, QMainWindow, QStackedWidget)
import sys

# Import your modules
from home_page import RoomScene
from login_page import LoginPage
from data_manager import *
from store_utils import GameData, default_theme
from clothing_store import ClothingView
from furniture_store import FurnitureView
from task_page import TaskEntryWidget
from task_handler import TaskDataHandler

# Initialize user id global variable as well as database manager, user manager and task handler objects
uuid = None
db = DatabaseManager()
user_man = UserManager(db)
task_handler = TaskDataHandler()

def main():
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            self.setWindowTitle('Tikkit - Login')
            self.resize(300, 310)
            self.setMinimumSize(300, 310)            

            self.game_data = GameData()
                      
            # Create pages
            self.login_page = LoginPage()
            self.home_page = RoomScene(self.game_data)
            self.clothing_view = ClothingView(self.game_data)
            self.furniture_view = FurnitureView(self.game_data)
            self.task_entry = TaskEntryWidget(default_theme)
            
            # Stack with all pages
            self.pages = QStackedWidget()
            self.pages.addWidget(self.login_page)      # Index 0
            self.pages.addWidget(self.home_page)       # Index 1
            self.pages.addWidget(self.furniture_view)  # Index 2
            self.pages.addWidget(self.clothing_view)   # Index 3
            self.pages.addWidget(self.task_entry)      # Index 4
            
            # Connect login/logout signals
            self.login_page.login_success.connect(self.login)
            self.home_page.logout_signal.connect(self.logout)
            
            # Connect from home to store
            self.home_page.request_clothing_store.connect(self.switch_to_clothing)
            self.home_page.request_furniture_store.connect(self.switch_to_furniture)

            # Connect from home to task entry
            self.home_page.request_task_entry.connect(self.switch_to_task_entry)
            
            # Connect from clothing to home and furniture
            self.clothing_view.request_home_view.connect(self.switch_to_home)
            self.clothing_view.request_furniture_view.connect(self.switch_to_furniture)
            self.clothing_view.money_changed.connect(self.sync_views)
            
            # Connect from furniture to home and clothing
            self.furniture_view.request_home_view.connect(self.switch_to_home)
            self.furniture_view.request_clothing_view.connect(self.switch_to_clothing)
            self.furniture_view.money_changed.connect(self.sync_views)

            # Connect from task entry to home
            self.task_entry.request_main_page.connect(self.switch_to_home)
            
            # Link task manager and task entry page
            self.task_entry.task_ready_signal.connect(task_handler.task_insertion)

            # Signal requesting change to tasks
            self.home_page.request_task_status_update.connect(self.update_task_status)
            self.home_page.request_subtask_status_update.connect(self.update_divtask_status)
            self.home_page.request_task_removal.connect(self.remove_and_update_tasks)

            # Save data signals
            self.furniture_view.request_save_layout.connect(self.save_furniture_data)
            self.clothing_view.checkout_completed.connect(self.save_clothe_data)
            
            self.setCentralWidget(self.pages)
            
        
        def init_game_data(self, current_uuid):
            '''Initializes game data based of given user ID

            Input: int
            Output: None'''
            inv_furn_list, eqp_furn_list = user_man.retrieve_user_furniture_data(current_uuid)
            self.game_data.inventory_furniture = inv_furn_list
            self.game_data.placed_furniture = eqp_furn_list
            self.game_data.money = user_man.retrive_user_money(current_uuid)
            self.furniture_view.load_layout(eqp_furn_list)
    
            inv_clothes_list, eqp_clothes_dict = user_man.retrieve_user_clothe_data(current_uuid)
            self.game_data.inventory_clothes = inv_clothes_list
            self.game_data.equipped_clothes = eqp_clothes_dict
            self.clothing_view.update_clothes_data(self.game_data)
            self.clothing_view.refresh_page()

            self.sync_views()
            pass

        def save_furniture_data(self, inventory_furniture, placed_furniture):
            '''Saves user furniture data to their uuid

            Input: list, list
            Output: None'''
            global uuid
            user_man.save_user_furniture_data(uuid, inventory_furniture, placed_furniture)

        def save_clothe_data(self, inventory_clothes, equipped_clothes):
            '''Saves user clothe data to their uuid

            Input: list, dict
            Output: None'''
            global uuid
            user_man.save_user_clothe_data(uuid, inventory_clothes, equipped_clothes)
        
        def login(self, current_uuid):
            '''Login sequence initializing app using user data from database

            Input: int
            Output: None'''
            global uuid
            uuid = current_uuid
            self.update_tasks()
            self.setWindowTitle('Tikkit')
            self.init_game_data(current_uuid)
            self.sync_views()
            self.setMinimumSize(1280, 720)
            self.resize(1280, 720)
            self.showMaximized()
            self.pages.setCurrentIndex(1)
        
        def switch_to_home(self):
            '''Switch to home page

            Input: None
            Output: None'''
            self.update_tasks()
            self.setWindowTitle('Tikkit')
            self.sync_views()
            self.pages.setCurrentIndex(1)
        
        def switch_to_clothing(self):
            '''Switch to clothing store page

            Input: None
            Output: None'''            
            self.setWindowTitle('Tikkit - Clothing Store')
            self.sync_views()
            self.pages.setCurrentIndex(3)
        
        def switch_to_furniture(self):
            '''Switch to furniture store page

            Input: None
            Output: None'''
            self.setWindowTitle('Tikkit - Furniture Store')
            self.sync_views()
            self.pages.setCurrentIndex(2)
        
        def switch_to_task_entry(self):
            '''Switch to task entry page

            Input: None
            Output: None'''
            global uuid
            self.task_entry.update_uuid(uuid)
            self.setWindowTitle('Tikkit - Add Task')
            self.pages.setCurrentIndex(4)
        
        def sync_views(self):
            '''Refresh pages to enure updated visuals relative to data

            Input: None
            Output: None'''
            self.clothing_view.refresh_page() 
            self.furniture_view.refresh_page(self.game_data)
            self.home_page.refresh_view(self.game_data)

        def remove_and_update_tasks(self, taskid):
            '''Removes task

            Input: int
            Output: None'''
            task_handler.task_deletion(taskid)
            self.update_tasks()

        def update_tasks(self):
            '''Refreshes task panel

            Input: None
            Output: None'''
            global uuid
            user_task_list = task_handler.query_user_tasks(uuid)
            self.home_page.update_task_panel(user_task_list)

        def update_divtask_status(self, card, status, subtask_id, taskid):
            '''Updates divided task's status and attempts reward grant

            Input: object, int, int, int
            Output: None'''
            task_handler.subtask_update_status(status, subtask_id)
            try:
                divtask_status, grant_status, reward = task_handler.query_divtask_status(taskid)
                self.garnt_user_reward(grant_status, reward, taskid)
            except:
                divtask_status = task_handler.query_divtask_status(taskid)
            finally:
                self.home_page.update_divtask_label(card, divtask_status)

        def update_task_status(self, status, taskid):
            '''Updates task's status and attempts reward grant

            Input: int, int
            Output: None'''
            try:
                grant_status, reward = task_handler.task_update_status(status, taskid)
                self.garnt_user_reward(grant_status, reward, taskid)
            finally:
                return

        def garnt_user_reward(self, grant_status, reward, taskid):
            '''Grants user task reward if first completion

            Input: int, int, int
            Output: None'''
            if grant_status == 0:
                task_handler.update_task_grant_status(taskid)
                self.game_data.money += reward
            self.sync_views()
        
        def logout(self):
            '''Logout sequence initializing app for next user

            Input: None
            Output: None'''
            self.setWindowTitle('Tikkit - Login')
            global uuid
            user_man.logout(uuid)
            user_man.save_user_money(uuid, self.game_data.money)
            self.furniture_view.clear_room_area()
            self.home_page.refresh_view(GameData())
            self.setMinimumSize(350, 310) 
            self.resize(350, 310)
            self.pages.setCurrentIndex(0)
            uuid = None
        
        def closeEvent(self, event):
            '''Logout sequence upon closing the app

            Input: object
            Output: None'''
            global uuid
            if uuid:
                user_man.logout(uuid)
                user_man.save_user_money(uuid, self.game_data.money)
            return super().closeEvent(event)
        
    ### Intialize App and Window ###
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()