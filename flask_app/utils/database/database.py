import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id
    
    # Gets the resume data from the database inthe form of a dictionary
    def getResumeData(self):
        resume_data = {}

        # Query institutions and build the base structure
        institutions = self.query("SELECT * FROM institutions")
        for inst in institutions:
            resume_data[inst['inst_id']] = {
                'address': inst['address'],
                'city': inst['city'],
                'state': inst['state'],
                'type': inst['type'],
                'zip': inst['zip'],
                'department': inst['department'],
                'name': inst['name'],
                'positions': {}
            }

        # Query positions
        positions = self.query("SELECT * FROM positions")
        for pos in positions:
            if pos['inst_id'] in resume_data:
                resume_data[pos['inst_id']]['positions'][pos['position_id']] = {
                    'end_date': pos['end_date'],
                    'responsibilities': pos['responsibilities'],
                    'start_date': pos['start_date'],
                    'title': pos['title'],
                    'experiences': {}
                }

        # Query experiences
        experiences = self.query("SELECT * FROM experiences")
        for exp in experiences:
            for inst_id, inst_data in resume_data.items():
                if exp['position_id'] in inst_data['positions']:
                    inst_data['positions'][exp['position_id']]['experiences'][exp['experience_id']] = {
                        'description': exp['description'],
                        'end_date': exp['end_date'],
                        'hyperlink': exp['hyperlink'],
                        'name': exp['name'],
                        'skills': {},
                        'start_date': exp['start_date']
                    }

        # Query skills
        skills = self.query("SELECT * FROM skills")
        for skill in skills:
            for inst_id, inst_data in resume_data.items():
                for pos_id, pos_data in inst_data['positions'].items():
                    for exp_id, exp_data in pos_data['experiences'].items():
                        if skill['experience_id'] == exp_id:
                            exp_data['skills'][skill['skill_id']] = {
                                'name': skill['name'],
                                'skill_level': skill['skill_level']
                            }

        return resume_data

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        # Check if the user already exists
        existing_user = self.query("SELECT * FROM users WHERE email = %s", (email,))
        if existing_user:
            return {'success': 0, 'message': 'User already exists'}
        
        # Encrypt the password
        enc_password = self.onewayEncrypt(password)

        # Insert user into database
        try:
            self.insertRows(table='users', columns=['email', 'password', 'role'], parameters=[[email, enc_password, role]])
            return {'success': 1, 'message': "User created successfully."}

        except Exception as exception:
            return {'success': 0, 'message': f"Error creating user. {exception}"}
        
    def authenticate(self, email='me@email.com', password='password'):
        # Encrypt the password to match the one in the database
        enc_password = self.onewayEncrypt(password)

        # Check if the user exists
        try:
            user = self.query("SELECT * FROM users WHERE email = %s", (email,))  
            if user:
                # Check for matching password
                if user[0]['password'] == enc_password:
                    return {'success': 1, 'message': 'User authentication successful'}
                else:
                    return {'success': 0, 'message': 'Incorrect password'}
            else:
                return {'success': 0, 'message': 'User not found'}
        
        except Exception as exception:
            return {'success': 0, 'message': f"Error authenticating user. {exception}"}
        

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message

