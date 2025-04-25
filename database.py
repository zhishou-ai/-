import mysql.connector
from mysql.connector import Error
from typing import List, Dict,Optional,Union
class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    def connect(self):
        #建立数据库连接
        try:
            self.connection = mysql.connector.connect(
                host='192.168.3.159',
                port = 3306,
                user='inventory_user',
                password='zhishou_chat',
                database='inventory_management',
                autocommit=True
            )
            print("数据库连接成功")
        except Error as e:
            print(f"数据库连接失败: {e}")
    def is_connected(self) -> bool:
        #检查数据库连接状态
        return self.connection is not None and self.connection.is_connected()
    def close(self):
        #关闭数据库连接
        if self.is_connected():
            self.connection.close()
            print("数据库连接已关闭")
    def reconnect(self):
        #重新连接数据库
        self.close()
        self.connect()
    def execute_query(self, query: str, params: tuple = None, fetch:bool = False) -> Union[List[Dict], None]:
        '''执行SQL查询
        :param query: SQL查询语句
        :param params: SQL查询参数
        :param fetch: 是否获取查询结果
        :return: 查询结果列表或None
        '''
        if not self.is_connected():
            self.reconnect()
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            return True
        except Error as e:
            print(f"执行查询失败: {e}\n查询: {query}\n参数: {params}")
            if cursor:
                cursor.close()
            return False
    #以下是物品相关操作
    def get_items(self, condition: List[str] = None,params: List = None) -> List[Dict]:
        '''获取物品列表
        :param condition: 条件列表
        :param params: 对应的参数列表
        :return: 物品列表
        '''
        query = "SELECT * FROM items"
        if condition:
            query += " WHERE " + " AND ".join(condition)
        result = self.execute_query(query, tuple(params) if params else None, fetch=True)
        return result if isinstance(result, list) else []
    def get_item_by_id(self, item_id: int) -> Optional[Dict]:
        '''根据ID获取物品
        :param item_id: 物品ID
        :return: 物品字典或None
        '''
        query = "SELECT * FROM items WHERE id = %s"
        result = self.execute_query(query, (item_id,),fetch=True)
        return result[0] if result else None
    def _get_category_id(self, category_name: str):
        if not category_name:
            return None
        result = self.execute_query("SELECT id FROM categories WHERE name = %s", (category_name,), fetch=True)
        if result:
            return result[0]['id']
        else:
            self.execute_query("INSERT INTO categories (name) VALUES (%s)",(category_name,))
            return self.connect.cursor().lastrowid
    def _get_location_id(self, location_name: str):
        if not location_name:
            return None
        result = self.execute_query("SELECT id FROM locations WHERE name = %s", (location_name,), fetch=True)
        if result:
            return result[0]['id']
        else:
            self.execute_query("INSERT INTO locations (name) VALUES (%s)")
            return self.connect.curcor().lastrowid
    def add_item(self, item_data: Dict) -> bool:
        '''添加物品
        :param item: 物品字典
        :return: 是否成功
        '''
        category_id = self._get_category_id(item_data.get("category"))
        location_id = self._get_location_id(item_data.get("location"))

        query = '''
        INSERT INTO items (name, category, location, quantity, description)
        VALUES (%s, %s, %s, %s, %s)
        '''
        params = (
            item_data.get("name"),
            category_id,
            location_id,
            item_data.get("quantity",1),
            item_data.get("description","")
        )
        return bool(self.execute_query(query, params))
    def update_item(self, item_id: int, item_data: Dict) -> bool:
        '''更新物品
        :param item_id: 物品ID
        :param item_data: 物品字典
        :return: 是否成功
        '''
        item_data['id'] = item_id
        query = '''
        UPDATE items SET
        name = %(name)s,
        category = %(category)s,
        location = %(location)s,
        quantity = %(quantity)s,
        description = %(description)s
        WHERE id = %(id)s
        '''
        return bool(self.execute_query(query, item_data))
    def delete_item(self, item_id: int) -> bool:
        '''删除物品
        :param item_id: 物品ID
        :return: 是否成功
        '''
        query = "DELETE FROM items WHERE id = %s"
        return bool(self.execute_query(query, (item_id,)))
    def get_categories(self) -> List[Dict]:
        '''获取物品分类列表
        :return: 分类列表
        '''
        query = "SELECT name FROM categories ORDER BY name" 
        result = self.execute_query(query, fetch=True)
        return [row['name'] for row in result] if result else []
    def get_locations(self) -> List[Dict]:
        '''获取物品位置列表
        :return: 位置列表
        '''
        query = "SELECT name FROM locations ORDER BY name"
        result = self.execute_query(query, fetch=True)
        return [row['name'] for row in result] if result else []
    def get_stats(self) -> Dict[str, int]:
        '''获取物品统计信息
        :return: 统计信息字典
        '''
        stats = {}
        result = self.execute_query("SELECT COUNT(*) AS total FROM items", fetch=True)
        stats['total_items'] = result[0]['total'] if result else 0

        result = self.execute_query("SELECT COUNT(DISTINCT category) AS total FROM items", fetch=True)
        stats['total_categories'] = result[0]['categories'] if result else 0

        result = self.execute_query("SELECT COUNT(DISTINCT location) AS total FROM items", fetch=True)
        stats['total_locations'] = result[0]['locations'] if result else 0
        return stats
    def add_category(self, category_name):
        """添加新分类到数据库"""
        if not category_name:
            return False
        query = "INSERT INTO categories (name) VALUES (%s) ON DUPLICATE KEY UPDATE name=VALUES(name)"
        return bool(self.execute_query(query, (category_name,)))
    
    def add_location(self, location):
        if not location:
            return False
        query = "INSERT INTO locations (name) VALUES (%s) ON DUPLICATE KEY UPDATE name=VALUES(name)"
        return bool(self.execute_query(query, (location,)))
    
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
if __name__ == "__main__":
    db = DatabaseManager()