import sqlite3

class DatabaseConnect():
    def __init__(self, db_path='appdata/app_data'):
        self.db_path = db_path

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

class DatabaseManager(DatabaseConnect):
    def __init__(self):
        super().__init__()

    def user_exists(self, username):
        '''Checks if username is present in database

        Input: str
        Output: bool'''
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
            return cursor.fetchone() is not None

    def insert_user(self, username, password):
        '''Attempts to insert user into database

        Input: str, str
        Output: bool'''
        try:
            with self._get_conn() as conn:
                conn.cursor().execute(
                    'INSERT INTO users (username, password, logged_status) VALUES (?, ?, 0)',
                    (username, password)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_password_by_username(self, username):
        '''Collects password from username

        Input: str
        Output: str or None'''
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_uuid(self, username):
        '''Collects user id from username

        Input: str
        Output: int or None'''
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT uuid FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            return result[0] if result else None

    def update_status(self, uuid, status_code):
        '''Updates specific user id's logged status

        Input: int, int
        Output: None'''
        with self._get_conn() as conn:
            conn.cursor().execute(
                'UPDATE users SET logged_status = ? WHERE uuid = ?', 
                (status_code, uuid)
            )
            conn.commit()

    def update_user_money(self, uuid, money):
        '''Updates specific user id's money value

        Input: int, int
        Output: None'''
        with self._get_conn() as conn:
            conn.cursor().execute('UPDATE users SET money = ? WHERE uuid = ?', (money, uuid))
            conn.commit()

    def query_user_money(self, uuid):
        '''Collects specific user id's money value from database

        Input: int
        Output: int'''
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT money FROM users WHERE uuid = ?', (uuid,))
            result = cursor.fetchone()

        return result[0]
    
    def add_user_inv_furniture(self, uuid, inv_dict):
        '''Adds specific user id's furniture inventory to database after clearing old items

        Input: int, dict
        Output: None'''
        with self._get_conn() as conn:
            conn.cursor().execute('DELETE FROM inventory WHERE uuid = ? AND item_type = ?', (uuid, 'furn'))
            conn.commit()

        for item, quantity in inv_dict.items():
            with self._get_conn() as conn:
                conn.cursor().execute(
                    'INSERT INTO inventory (uuid, item_name, item_type, quantity) VALUES (?, ?, ?, ?)',
                    (uuid, item, 'furn',quantity)
                )
                conn.commit()
    
    def add_user_eqp_furniture(self, uuid, placed_furniture):
        '''Adds specific user id's placed furniture to database after clearing old items

        Input: int, list
        Output: None'''
        with self._get_conn() as conn:
            conn.cursor().execute('DELETE FROM placed_furniture WHERE uuid = ?', (uuid,))
            conn.commit()

        for item in placed_furniture:
            with self._get_conn() as conn:
                conn.cursor().execute(
                    'INSERT INTO placed_furniture (uuid, name, angle_index, x, y, z) VALUES (?, ?, ?, ?, ? , ?)',
                    (uuid, item['name'], item['angle_index'], item['x'], item['y'], item['z'])
                    )
                conn.commit()
        
        return

    def query_user_inv_furniture(self, uuid):
        '''Collects specific user id's inventory furniture from database

        Input: int
        Output: list'''
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT item_name, quantity FROM inventory WHERE uuid = ? AND item_type = ?', (uuid, 'furn'))
            result = cursor.fetchall()
        
        inv_furn_list = []
        for item in result:
            item_name, quantity = item
            for _ in range(quantity):
                inv_furn_list.append(item_name)
        
        return inv_furn_list


    def query_user_eqp_furniture(self, uuid):
        '''Collects specific user id's placed furniture from database

        Input: int
        Output: list'''
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute(f"SELECT name, angle_index, x, y, z FROM placed_furniture WHERE uuid = (?)", (uuid,))
            rows = cursor.fetchall()
            
        row_list = []
        for row in rows:
            row_data = dict(row)
            row_list.append(row_data)
        
        return row_list
    
    def add_user_eqp_clothes(self, uuid):
        '''Adds specific user id's empty equipped clothes template to database

        Input: int
        Output: None'''
        with self._get_conn() as conn:
            conn.cursor().execute(
                'INSERT INTO equipped_clothes (uuid, Head, Torso, Legs, Feet) VALUES (?, ?, ?, ?, ?)',
                (uuid, None, None, None, None)
                )
            conn.commit()

    def update_user_eqp_clothes(self, uuid, equipped_clothes):
        '''Updates specific user id's equipped clothes to database

        Input: int, dict
        Output: None'''
        with self._get_conn() as conn:
            conn.cursor().execute(
                'UPDATE equipped_clothes SET Head = ?, Torso = ?, Legs = ?, Feet = ? WHERE uuid = ?', 
                (equipped_clothes['Head'], equipped_clothes['Torso'], equipped_clothes['Legs'], equipped_clothes['Feet'], uuid)
            )
            conn.commit()

    def add_user_inv_clothes(self, uuid, item_list):
        '''Adds specific user id's clothing inventory to database after clearing old items

        Input: int, dict
        Output: None'''
        with self._get_conn() as conn:
            conn.cursor().execute('DELETE FROM inventory WHERE uuid = ? AND item_type = ?', (uuid, 'clothe'))
            conn.commit()

        for item in item_list:
            with self._get_conn() as conn:
                conn.cursor().execute(
                    'INSERT INTO inventory (uuid, item_name, item_type) VALUES (?, ?, ?)',
                    (uuid, item, 'clothe')
                    )
                conn.commit()
        
        return
    
    def query_user_eqp_clothes(self, uuid):
        '''Collects specific user id's equipped clothes from database

        Input: int
        Output: dict'''
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute(f"SELECT Head, Torso, Legs, Feet FROM equipped_clothes WHERE uuid = (?)", (uuid,))
            row = cursor.fetchone()
        
        if not row:
            return {}
        else:
            return dict(row)
    
    def query_user_inv_clothes(self, uuid):
        '''Collects specific user id's inevntory clothes from database

        Input: int
        Output: list'''
        inv = []

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT item_name FROM inventory WHERE uuid = ? AND item_type = ?', (uuid, 'clothe'))
            result = cursor.fetchall()

        for i in range(len(result)):
            inv.append(result[i][0])
        
        if not inv:
            return []
        else:
            return inv

class UserManager():
    def __init__(self, db_manager):
        self.db = db_manager
        self.current_uuid = None

    def validate_and_register(self, username, password, confirm_password):
        '''Ensures specific conditons met before registering user

        Input: str, str, str
        Output: bool, str'''

        if not username or not password:
            return False, 'All fields are required!'
        
        if password != confirm_password:
            return False, 'Passwords do not match!'

        if len(password) < 6:
            return False, 'Password must be at least 6 characters long!'

        if self.db.user_exists(username):
            return False, 'Username is already taken!'

        if self.db.insert_user(username, password):
            self.current_uuid = self.db.get_uuid(username)
            default_space = [   {'name': 'Floor Blank', 'angle_index': 0, 'x': 555, 'y': 172, 'z': 0}, 
                                {'name': 'Wall1', 'angle_index': 0, 'x': 640, 'y': 64, 'z': 0},
                                {'name': 'Wall1', 'angle_index': 1, 'x': 558, 'y': 67, 'z': 0}, 
                                {'name': 'Floor Blank', 'angle_index': 0, 'x': 477, 'y': 230, 'z': 3},
                                {'name': 'Wall2', 'angle_index': 0, 'x': 717, 'y': 119, 'z': 1}, 
                                {'name': 'Floor Blank', 'angle_index': 3, 'x': 633, 'y': 228, 'z': 2}, 
                                {'name': 'Floor Blank', 'angle_index': 1, 'x': 554, 'y': 285, 'z': 4}, 
                                {'name': 'Wall1', 'angle_index': 1, 'x': 477, 'y': 124, 'z': 5},
                            ]
            self.db.add_user_eqp_furniture(self.current_uuid, default_space)

            self.db.add_user_eqp_clothes(self.current_uuid)
            
            return True, 'Account created successfully!'
        else:
            return False, 'Database error during insertion.'

    def validate_and_login(self, username, password):
        '''Ensure specific conditions met before login

        Input: str, str
        Output: bool, str'''
        if not username or not password:
            return False, 'All fields are required!'

        stored_password = self.db.get_password_by_username(username)

        if stored_password is None:
            return False, 'Username not found!'

        if password == stored_password:
            self.current_uuid = self.db.get_uuid(username)
            self.db.update_status(self.current_uuid, 1)
            return True, 'Login successful!'
        else:
            return False, 'Incorrect password!'

    def logout(self, user_uuid):
        '''Updates specific user id's logged status to 0

        Input: int
        Output: None'''
        if user_uuid:
            self.db.update_status(user_uuid, 0)

    def save_user_money(self, uuid, money):
        '''Updates specific user id's currency value through data manager

        Input: int, int
        Output: None'''
        self.db.update_user_money(uuid, money)

    def retrive_user_money(self, uuid):
        '''Updates specific user id's currency value through data manager

        Input: int
        Output: int'''
        return self.db.query_user_money(uuid)
    
    def save_user_furniture_data(self, uuid, inventory_furniture, placed_furniture):
        '''Updates specific user id's complete furniture data through data manager

        Input: int, list, list
        Output: int'''
        inv_set = set(inventory_furniture)
        inv_dict = {}

        for item in inv_set:
            inv_dict[item] = inventory_furniture.count(item)

        self.db.add_user_inv_furniture(uuid, inv_dict)
        self.db.add_user_eqp_furniture(uuid, placed_furniture)

    def retrieve_user_furniture_data(self, uuid):
        '''Collect specific user id's complete furniture data through data manager

        Input: int
        Output: list, list'''
        inv_furn_list = self.db.query_user_inv_furniture(uuid)
        place_items_list = self.db.query_user_eqp_furniture(uuid)

        return inv_furn_list, place_items_list
    
    def save_user_clothe_data(self, uuid, invenory_clothes, equipped_clothes):
        '''Updates specific user id's complete clothing data through data manager

        Input: int, list, dict
        Output: None'''
        self.db.update_user_eqp_clothes(uuid, equipped_clothes)
        self.db.add_user_inv_clothes(uuid, invenory_clothes)

    def retrieve_user_clothe_data(self, uuid):
        '''Collect specific user id's complete clothing data through data manager

        Input: int
        Output: list, dict'''
        equipped_clothes = self.db.query_user_eqp_clothes(uuid)
        inventory_clothes = self.db.query_user_inv_clothes(uuid)

        return inventory_clothes, equipped_clothes