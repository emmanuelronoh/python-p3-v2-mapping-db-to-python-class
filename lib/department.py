import sqlite3
from __init__ import CONN, CURSOR

class Department:
    all = {}  # In-memory storage for instances

    def __init__(self, name, location, id=None):
        self.name = name
        self.location = location
        self.id = id

    @classmethod
    def create_table(cls):
        '''Creates the departments table if it does not exist.'''
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        '''Drops the departments table if it exists.'''
        sql = "DROP TABLE IF EXISTS departments"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        '''Saves the instance to the database.'''
        if self.id is None:
            # Insert new department
            sql = """
                INSERT INTO departments (name, location)
                VALUES (?, ?)
            """
            CURSOR.execute(sql, (self.name, self.location))
            self.id = CURSOR.lastrowid
            Department.all[self.id] = self
            CONN.commit()
        else:
            # Update existing department
            self.update()

    @classmethod
    def create(cls, name, location):
        '''Creates a new department instance and saves it to the database.'''
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        '''Updates the instance's corresponding database row.'''
        if self.id is not None:
            sql = """
                UPDATE departments
                SET name = ?, location = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.name, self.location, self.id))
            CONN.commit()
            Department.all[self.id] = self

    def delete(self):
        '''Deletes the instance's corresponding database row.'''
        if self.id is not None:
            sql = "DELETE FROM departments WHERE id = ?"
            CURSOR.execute(sql, (self.id,))
            CONN.commit()
            Department.all.pop(self.id, None)
            self.id = None

    @classmethod
    def instance_from_db(cls, row):
        '''Takes a table row and returns a Department instance.'''
        return cls(row[1], row[2], row[0])

    @classmethod
    def get_all(cls):
        '''Returns a list of Department instances for every row in the db.'''
        sql = "SELECT * FROM departments"
        rows = CURSOR.execute(sql).fetchall()
        departments = [cls.instance_from_db(row) for row in rows]
        cls.all = {dept.id: dept for dept in departments}
        return departments

    @classmethod
    def find_by_id(cls, department_id):
        '''Returns a Department instance corresponding to the db row retrieved by id.'''
        department = cls.all.get(department_id)
        if department is None:
            sql = "SELECT * FROM departments WHERE id = ?"
            row = CURSOR.execute(sql, (department_id,)).fetchone()
            if row:
                department = cls.instance_from_db(row)
                cls.all[department_id] = department
        return department

    @classmethod
    def find_by_name(cls, name):
        '''Returns a Department instance corresponding to the db row retrieved by name.'''
        for department in cls.all.values():
            if department.name == name:
                return department
        sql = "SELECT * FROM departments WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        if row:
            department = cls.instance_from_db(row)
            cls.all[department.id] = department
            return department
        return None
