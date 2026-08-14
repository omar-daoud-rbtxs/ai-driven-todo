from llama_cpp import Llama
import numpy as np
import re
import sqlite3
from data_manager import DatabaseConnect as DBC

class UserTask():
    def __init__(self, uuid, taskid, name, date_due, time_due, deadline, status, subdivisions, reward, subtasks, grant_status):
        self.uuid = uuid
        self.taskid = taskid
        self.name = name
        self.status = status
        self.subdivisions = subdivisions
        self.deadline = deadline
        self.time_due = time_due
        self.date_due = date_due
        self.reward = reward
        self.grant_status = grant_status
        self.subtasks = subtasks

### Creating AI Engine class to allow interactions with local AI model ###
class AIEngine():
    def __init__(self):
        self.llm = Llama(
            model_path="qwen2.5-0.5b-instruct-q4_k_m.gguf", 
            n_ctx=2048, 
            n_gpu_layers=0, 
            verbose=False
        )

    def get_subtask_list(self, task_name, num_steps):
        '''Prompts AI to generate subtask list for divided task

        Input: str, int
        Output: dict'''
        list_msg = [
            {
                "role": "system", 
                "content": "You are a rigid automated planner. Output ONLY a numbered list. Maximum 4 words per step."
            },

            {
                "role": "user", 
                "content": f"Task: {task_name}\nRequirement: Create exactly {num_steps} steps. Keep each step under 4 words."
            }
        ]

        task_list = self.llm.create_chat_completion(
            messages=list_msg,
            temperature=0.1,
            max_tokens=250
        )

        task_list = task_list['choices'][0]['message']['content']
        sub_tasks_dict = self.split_task_list(task_list)

        return sub_tasks_dict
    
    def get_task_diff(self, task_name):
        '''Prompts AI to generate difficulty scaling for task

        Input: str
        Output: int'''
        diff_msg = [
            {
                "role": "system", 
                "content": "You are a difficulty rater. Output ONLY a single integer number between 0 and 100. Do not write words."
            },

            {
                "role": "user", 
                "content": f"Task: {task_name}\nRequirement: Rate a difficulty out of 100."
            }
        ]
        
        difficulty = self.llm.create_chat_completion(
            messages=diff_msg,
            temperature=0.1,
            max_tokens=250
        )

        difficulty = int(difficulty['choices'][0]['message']['content'])
        difficulty = np.interp(difficulty, [75, 100], [0, 100])

        return difficulty
    
    def split_task_list(self, task_list):
        '''Splits task string user RE to segements

        Input: str
        Output: dict'''
        segments = re.split(r'(\d+)\.', task_list)
        sub_tasks_dict = {}

        for i in range(1, len(segments), 2):
            step_number = int(segments[i])
            step_text = segments[i+1].strip()
            sub_tasks_dict[step_number] = step_text
        
        return sub_tasks_dict
    
ai_engine = AIEngine()

### Creating Task Handler to interact with database for task relvant queries ###
class TaskDataHandler(DBC):
    def __init__(self):
        super().__init__()
    
    def task_insertion(self, task_specs):
        '''Insert task and subtasks if the task is divided

        Input: object
        Output: int'''
        try:
            with self._get_conn() as conn:
                curr = conn.cursor()
                curr.execute(
                    'INSERT INTO tasks (uuid, name, subdivisions, deadline, date_due, time_due, reward) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                    (task_specs.uuid, task_specs.name, task_specs.subdivisions, task_specs.deadline, task_specs.date_due, task_specs.time_due, task_specs.reward)
                )
                current_task_id = curr.lastrowid
                conn.commit()
        except sqlite3.IntegrityError:
            return 0
        
        if task_specs.subdivisions != 0:
            for i in range(task_specs.subdivisions):
                try:
                    with self._get_conn() as conn:
                        conn.cursor().execute(
                            'INSERT INTO subtasks (parent_id, subtask_order, name) VALUES (?, ?, ?)', 
                            (current_task_id, i, task_specs.subtasks[i+1])
                        )
                        conn.commit()
                except sqlite3.IntegrityError as e:
                    print(e)
                    return 0
                
    def query_user_tasks(self, uuid):
        '''Collect user tasks from database

        Input: int
        Output: list'''
        taskid_list = []

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT taskid FROM tasks WHERE uuid = ?', (uuid,))
            result = cursor.fetchall()

        for i in range(len(result)):
            taskid_list.append(result[i][0])
        
        if not taskid_list:
            return []

        taskid_string = ',' .join(['?'] * len(taskid_list))
        
        user_task_list = []
        
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM tasks WHERE taskid IN ({taskid_string})", taskid_list)
            rows = cursor.fetchall()
            
        for row in rows:
            row_data = dict(row) 
            row_data['subtasks'] = None

            if row_data['subdivisions'] != 0:
                subtask_list = []
                with self._get_conn() as conn:
                    conn.row_factory = sqlite3.Row 
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM subtasks WHERE parent_id = ?", (row_data['taskid'],))
                    rows = cursor.fetchall()
                        
                for row in rows:
                    subtask = dict(row) 
                    subtask_list.append(subtask)
                row_data['subtasks'] = subtask_list
                subtask_list = []

            user_task = UserTask(**row_data)
            user_task_list.append(user_task)
        
        subtask_list = []

        return user_task_list
    
    def update_task_grant_status(self, taskid):
        '''Updates grant status in database

        Input: int
        Output: None'''
        with self._get_conn() as conn:
            conn.cursor().execute('UPDATE tasks SET grant_status = ? WHERE taskid = ?', (1, taskid))
            conn.commit()
    
    def query_task_grant_status(self, taskid):
        '''Collects grant status data from database

        Input: int
        Output: tuple'''
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT grant_status, reward FROM tasks WHERE taskid = ?', (taskid,))
            result = cursor.fetchone()
        
        return result
    
    def task_update_status(self, status, taskid):
        '''Updates task status and if applicable, returns grant status and reward

        Input: int
        Output: int, int'''
        with self._get_conn() as conn:
            conn.cursor().execute('UPDATE tasks SET status = ? WHERE taskid = ?', (status, taskid))
            conn.commit()
        
        if status == 1:
            grant_status, reward = self.query_task_grant_status(taskid)

            return grant_status, reward


    def subtask_update_status(self, status, subtask_id):
        '''Updates individual subtask status

        Input: int, int
        Output: None'''
        with self._get_conn() as conn:
            conn.cursor().execute('UPDATE subtasks SET status = ? WHERE subtask_id = ?', (status, subtask_id))
            conn.commit()

    def query_divtask_status(self, taskid):
        '''Updates divided tasks' subtask status and updates its own status accordingly, if applicable, returns grant status and reward

        Input: int
        Output: int, int int'''
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT MIN(status) FROM subtasks WHERE parent_id = ?', (taskid,))
            result = cursor.fetchone()
        
        grant_status, reward = self.query_task_grant_status(taskid)

        if result[0] != 0:
            self.task_update_status(1, taskid)
            status = 1
        else:
            self.task_update_status(0, taskid)
            status = 0

        if status == 1:
            return result[0], grant_status, reward
        else:
            return result[0]
        

    def task_deletion(self, taskid):
        '''Deletes task and its subtasks if task is divided

        Input: int
        Output: None'''
        tempid = taskid
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT subdivisions FROM tasks WHERE taskid = ?', (tempid,))
            result = cursor.fetchone()
            conn.cursor().execute('DELETE FROM tasks WHERE taskid = ?', (tempid,))
            conn.commit()
        
        if result[0] != 0:
            with self._get_conn() as conn:
                conn.cursor().execute('DELETE FROM subtasks WHERE parent_id = ?', (tempid,))
                conn.commit()