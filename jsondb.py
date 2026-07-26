import json
import os
import re



class Tools :
    
    # compare if two strings are equals , match_case option
    @staticmethod
    def equals(s1:str,s2:str,match_case=True):
        return str(s1.lower() if match_case else s1) == str(s2.lower() if match_case else s2)


class Table :
    def __init__(self,name:str,dbPath:str,data) :
        self.name = name
        self.dbPath = dbPath # use as pointer in case you want to override or modify data
        self.data = data
        self.columns = list(self.data[0].keys())
        self.deleted = False
    
    def column_data(self,colname:str):
        return self.data[colname]
    def get_columns(self):
        return self.columns
    def column_should_exist(self,colname):
        if colname not in self.columns :
            print(f"Error 'where' : Column '{colname}' Not found")
            exit()
    def select_columns(self,cols:list[str]) :
        # select specific columns
        return [self._filter_by_column(record,cols) for record in self.data]
    def _filter_by_column(self,record:dict,cols: list[str]):
        # take a record (single json) and return the same but with specific columns
        d = {}
        for col,val in record.items() :
            if col in cols :
                d[col] = val
        return d
    def override(self):
        print("Override()  from Table class is deprecated, please use it from the JsonDbQuery class ! ")
        return
        

    def where(self,column:str,value:str,case_sensitive=False):
        # return records of a column that matches the value
        result = []
        # 1. if the column exists
        if column not in self.columns :
            print(f"Error 'where' : Column '{column}' Not found")
        
        # 2. search
        for record in self.data :
            if Tools.equals(record[column],value,case_sensitive):
                result.append(record)
        return result
    def where_regex(self,column:str,regex:str):
        # return records of a column that matches the value
        result = []
        # 1. if the column exists
        self.column_should_exist(column)
        
        # 2. compile the regex
        compiled_regex = re.compile(regex)
        # 3. search
        for record in self.data :
            if re.match(compiled_regex,record[column]) :
                result.append(record)
        return result
    def delete_table(self,rc=True) : # remove cotent
        self.deleted = True
        print(f"Table '{self.name}' deleted successfully !")

        if rc :
            self.name += "[DELETED]"
            self.data = []

    def __json__(self):
        # converts this class and data into json form
        # data + name
        return { self.name:self.data }


# using json instead of sqlite
class JsonDB :
    def __init__(self,path,not_found_create=True,name="My database"):
        if not_found_create and not os.path.exists(path) :
            # create an empty db if not found
            # ===================
            self.path = path
            template = { "name":name, "data":{"tables":{ } } }

            with open(path,"w") as file :
                file.write(json.dumps(template,indent=4))


        self.path = self.db_should_exist(path)
        self.tables = []
        self.name = name
        
        self.load()
    def load(self) :
        with open(self.path,"r") as db :
            self.tables = self.load_tables(
                json.load(db)
            )
            
            print(f"Loaded {len(self.tables)} tables : {[table.name for table in self.tables]}")
    def load_tables(self,data):
        # return list of tables instance from the json data
        return [ 
                Table(name,self.path,tabledata) 
                for name,tabledata
                in data["data"]["tables"].items()]  
    """ Verificators  """
    def db_should_exist(self,path:str):
        if os.path.exists(path):
            return path
        else :
            print(f"Path {path} Not found !")
            print(os.listdir())
            exit()
    def table_should_exists(self,table:str,error:str):
        if table in [table.name for table in self.tables]:
            return True
        else :
            print(error)
            exit()
    def find_table(self,tablename:str):
        for table in self.tables :
            if tablename == table.name :
                return table
        return None


# to execute queries
class JsonDbQuery(JsonDB) :
    def __init__(self, path,not_found_create=True,name="NewDb"):
        super().__init__(path,not_found_create,name)
    # select a specific table + return
    def select_table(self,tablename:str):
        # verify if exist
        self.load()
        self.table_should_exists(tablename,error=f"Cannot select from '{tablename}' : Table Not Found")
        return self.find_table(tablename)
    def override(self):
        # keep only tables where the attribute 'deleted' is False
        self.tables = [table for table in self.tables if not table.deleted]

        with open(self.path,"w") as file :
            
            output = {
                    "name": self.name,
                    "data" : {
                        # TODO create the function get_tables_as_dict
                            "tables": self.get_tables_as_dict()
                        }
                    }
            file.write(json.dumps(output,indent=4))
    def get_tables_as_dict(self):
        tables = {}
        # TODO loop over non-deleted tables only
        for table in  [t for t in self.tables if not t.deleted ]:
            tables[table.name] = table.data
        return tables

if __name__ == "__main__" :
    # load the database
    db = JsonDbQuery("db.json")

    # select a table
    users = db.select_table("users") # select the table users , type=Table()
    users.select_columns(["name","password"]) # SELECT name,password from users
    print(users.columns)
    print(users.data[0]["id"]) # SELECT id from users LIMIT 1
    users.data[0]["name"] = "ibrahim"
    users.override() # COMMIT


    print("=" * 10)
    print(users.where("name","Ibrahim",case_sensitive=True )) # SELECT * from users ==> WHERE name=ibrahim

    print("=" * 10)
    print(users.where_regex("name","[A-z]")) # Use  regex

    # delete a table
    users.delete_table()
    db.override()
    




    # Test if the database not found
    
    # not_found_db = JsonDbQuery("notfound.json")
    

