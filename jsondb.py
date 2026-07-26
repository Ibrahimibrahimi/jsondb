import json , os


class Table :
    def __init__(self,name:str,dbPath:str,data) :
        self.name = name
        self.dbPath = dbPath # use as pointer in case you want to override or modify data
        self.data = data
        self.columns = list(self.data[0].keys())
    
    def column_data(self,colname:str):
        return self.data[colname]
    def get_columns(self):
        return self.columns
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
        # update the table data in the db file 
        dbData = None
        with open(self.dbPath,"r") as db :
            dbData = json.load(db)
        
        with open(self.dbPath,"w") as db :
            dbData["data"]["tables"][self.name] = self.data
            db.write(json.dumps(dbData,indent=4))
            print(f"Table '{self.name}' updated successfully")
    def where(self,column:str,value:str,case_sensitive=False):
        # return records of a column that matches the value
        result = []
        # 1. if the column exists
        if column not in self.columns :
            print(f"Error 'where' : Column '{column}' Not found")
        
        # 2. search
        for record in self.data :
            if record[column] == value :
                result.append(record)
        return result

# using json instead of sqlite
class JsonDB :
    def __init__(self,path):
        self.path = self.not_found_exit(path)    
        self.tables = []
        
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
    def not_found_exit(self,path:str):
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
    def __init__(self, path):
        super().__init__(path)

    # add query execution
    def select(self,tablename:str):
        # verify if exist
        self.load()
        self.table_should_exists(tablename,error=f"Cannot select from '{tablename}' : Table Not Found")
        return self.find_table(tablename)


# load the database
db = JsonDbQuery("db.json")

# select a table
users = db.select("users") # select the table users , type=Table()
users.select_columns(["name","password"]) # SELECT name,password from users
print(users.columns)
print(users.data[0]["id"])
users.data[0]["name"] = "ibrahim"
users.override()


print("=" * 10)
print(users.where("name","ibrahim"))