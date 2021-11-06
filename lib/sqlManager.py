import sqlite3

class FieldType(object):
    text = "text"
    integer = "integer"
    real = "real"
    null = "null"
    blob = "blob"

class SqlManager(object):

    def __init__(self, path) -> None:
        super().__init__()
        self.conn = sqlite3.connect(path)
        tableList = self.getTable()
        if len(tableList) == 0:
            self.currentTable = None
        else:
            self.currentTable = tableList[0]

    def createTable(self, *, name, field, id=False):
        self.currentTable = name
        cmd = []
        if id:
            cmd.append("create table if not exists {0} (id integer primary key autoincrement".format(name))
        else:
            cmd.append("create table if not exists {0} (".format(name))
        fields = ["{0} {1}".format(fname, ftype) for fname, ftype in field.items()]
        cmd.append(",".join(fields))
        cmd.append(")")
        self.conn.execute(self.executeCmd("".join(cmd)))
        self.conn.commit()

    def insert(self, *, table=None, field=None, value):
        if table == None:
            table = self.currentTable
        else:
            self.currentTable = table
        if field == None:
            field = self.getField(table=table)
        cmd = [] 
        cmd.append("insert into {0} (".format(table))
        cmd.append(",".join(field))
        values = []
        for i in range(len(value)):
            if isinstance(value[i],str):
                values.append("\"{0}\"".format(value[i]))
            else:
                values.append(str(value[i]))
        cmd.append(") values (" + ",".join(values) + ")")
        self.conn.execute(self.executeCmd("".join(cmd)))
        self.conn.commit()

    def getTable(self):
        cursor = self.conn.cursor()
        cursor.execute(self.executeCmd("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
        result = cursor.fetchall()
        #result.pop()
        r = []
        for x in result:
            r.append(*x)
        cursor.close()
        return r

    def getField(self, *, table=None):
        if table == None:
            table = self.currentTable
        else:
            self.currentTable = table
        cursor = self.conn.cursor()
        cursor.execute(self.executeCmd("PRAGMA table_info({0})".format(table)))
        result = [x[1] for x in cursor.fetchall()]
        cursor.close()
        return result
        
    def clear(self, *, table=None):
        if table == None:
            table = self.currentTable
        else:
            self.currentTable = table
        self.conn.execute(self.executeCmd("delete from {0}".format(table)))
        self.conn.commit()

    def deleteField(self, *, table=None, field):
        if table == None:
            table = self.currentTable
        else:
            self.currentTable = table
        fields = self.getField(table=table)
        fields.remove(field)
        self.conn.execute(self.executeCmd("create table temp as select " + ",".join(fields) + " from {0} where 1 = 1".format(table)))
        self.conn.execute(self.executeCmd("drop table {0}").format(table))
        self.conn.execute(self.executeCmd("alter table temp rename to {0}".format(table)))
        self.conn.commit()

    def deleteRecord(self, *, table=None, condition):
        if table == None:
            table = self.currentTable
        else:
            self.currentTable = table
        conditions = []
        for x,y in condition.items():
            x = str(x)
            if isinstance(y, str):
                y = "'{0}'".format(y)
            else:
                y = str(y)
            conditions.append(x+" = "+y)
        self.conn.execute(self.executeCmd("delete from {0} where {1}".format(table, " and ".join(conditions))))
        self.conn.commit()

    def select(self, *, table=None, field=("*"), condition=None):
        if table == None:
            table = self.currentTable
        else:
            self.currentTable = table
        cursor = self.conn.cursor()
        if condition == None:
            cursor.execute(self.executeCmd("select {1} from {0}".format(table,", ".join(field))))
        else:
            conditions = []
            for x,y in condition.items():
                x = str(x)
                if isinstance(y, str):
                    y = "'{0}'".format(y)
                else:
                    y = str(y)
                conditions.append(x+" = "+y)
            cursor.execute(self.executeCmd("select {1} from {0} where {2}".format(table,", ".join(field)," and ".join(conditions))))
        result = [[*x] for x in cursor.fetchall()]
        cursor.close()
        return result

    def executeCmd(self, str):
        print(str)
        return str
    
    def close(self):
        self.conn.close()

def test():
    db = SqlManager("C:/Users/asus/Desktop/learn python/problem/my_test.db")
    db.createTable(name="bookshelf",field={"path":FieldType.text,"page":FieldType.integer})
    print(db.getTable())
    db.insert(field=["path","page"],value=["myworld\'\'2",2])
    print(db.select())
    print(db.select(field=("path",),condition={"page":2}))
    db.deleteRecord(condition={"page":2})
    print(db.select())
    db.clear()
    db.close()

#test()

        

