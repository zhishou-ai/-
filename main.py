import sys
from PyQt6.QtWidgets import QTableWidget,QApplication, QMainWindow, QDialog, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from ui_mainwindow import Ui_MainWindow
from ui_itemdialog import Ui_Dialog
from database import DatabaseManager  
class ItemDialog(QDialog):
    """物品编辑对话框类"""
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        # 设置分类和位置下拉框为可编辑
        self.ui.categoryEdit.setEditable(True)  # 允许直接输入
        self.ui.locationEdit.setEditable(True)
        
        # 初始化分类和位置下拉框
        self._init_comboboxes()
        
        # 初始化数据
        if item_data:
            self._load_data(item_data)
    
    def _init_comboboxes(self):
        """初始化分类和位置下拉框"""
        self.db = DatabaseManager()
        
        # 获取分类选项
        categories = self.db.get_categories()
        self.ui.categoryEdit.clear()
        self.ui.categoryEdit.addItems(categories)
        
        # 获取位置选项
        locations = self.db.get_locations()
        self.ui.locationEdit.clear()
        self.ui.locationEdit.addItems(locations)
    
    
    def get_data(self):
        """获取对话框数据"""
        data = {
            'name': self.ui.nameEdit.text().strip(),
            'category': self.ui.categoryEdit.currentText().strip() or None,
            'location': self.ui.locationEdit.currentText().strip() or None,
            'quantity': self.ui.quantitySpin.value(),
            'description': self.ui.descriptionEdit.toPlainText().strip() or None
        }
        
        # 确保名称不为空
        if not data['name']:
            QMessageBox.warning(self, "错误", "物品名称不能为空")
            return None
        
        return data
    def _check_new_category(self, category):
        """检查并添加新分类到数据库"""
        if category and not self._category_exists(category):
            db = DatabaseManager()
            # 假设有一个方法可以添加新分类到数据库
            db.add_category(category)
    
    def _check_new_location(self, location):
        """检查并添加新位置到数据库"""
        if location and not self._location_exists(location):
            db = DatabaseManager()
            # 假设有一个方法可以添加新位置到数据库
            db.add_location(location)
    
    def _category_exists(self, category):
        """检查分类是否已存在"""
        db = DatabaseManager()
        categories = db.get_categories()
        return category in categories
    
    def _location_exists(self, location):
        """检查位置是否已存在"""
        db = DatabaseManager()
        locations = db.get_locations()
        return location in locations
    def _load_data(self, data):
        """填充对话框数据"""
        self.ui.nameEdit.setText(data['name'])
        self.ui.quantitySpin.setValue(data['quantity'])
        self.ui.descriptionEdit.setPlainText(data.get('description', ''))
        
        # 设置分类和位置
        if 'category' in data and data['category']:
            index = self.ui.categoryEdit.findText(data['category'])
            if index >= 0:
                self.ui.categoryEdit.setCurrentIndex(index)
        
        if 'location' in data and data['location']:
            index = self.ui.locationEdit.findText(data['location'])
            if index >= 0:
                self.ui.locationEdit.setCurrentIndex(index)
    
class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # 初始化数据库
        self.db = DatabaseManager()  
        
        # 初始化UI
        self._setup_ui()
        self._connect_signals()
        
        # 加载初始数据
        self.load_items()
    
    def _setup_ui(self):
        """初始化界面设置"""
        # 设置表格属性
        self.ui.tableWidget.setColumnCount(6)  # ID,名称,分类,位置,数量,描述
        self.ui.tableWidget.setHorizontalHeaderLabels(
            ['ID', '名称', '分类', '位置', '数量', '描述'])
        self.ui.tableWidget.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.ui.tableWidget.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        
        # 初始化筛选下拉框
        self._init_filters()
    
    def _init_filters(self):
        """初始化筛选下拉框"""
        self.ui.comboBox.addItem("所有分类")  # 第一个是默认选项
        self.ui.comboBox_2.addItem("所有位置")
        
        # 从数据库获取分类和位置选项
        categories = self.db.get_categories()  
        locations = self.db.get_locations()    
        
        self.ui.comboBox.addItems(categories)
        self.ui.comboBox_2.addItems(locations)
    
    def _connect_signals(self):
        """连接信号与槽"""
        self.ui.btnAdd.clicked.connect(self.add_item)
        self.ui.btnEdit.clicked.connect(self.edit_item)
        self.ui.btnDelete.clicked.connect(self.delete_item)
        self.ui.btnRefresh.clicked.connect(self.load_items)
        self.ui.searchEdit.textChanged.connect(self.load_items)
        self.ui.comboBox.currentTextChanged.connect(self.load_items)
        self.ui.comboBox_2.currentTextChanged.connect(self.load_items)
    def load_items(self):
        """加载物品列表"""
        # 获取筛选条件
        search_text = self.ui.searchEdit.text().strip()
        category = self.ui.comboBox.currentText()
        location = self.ui.comboBox_2.currentText()
        
        # 构建查询条件
        conditions = []
        params = []
        
        if search_text:
            conditions.append("name LIKE %s")
            params.append(f"%{search_text}%")
        if category != "所有分类":
            conditions.append("category = %s")
            params.append(category)
        if location != "所有位置":
            conditions.append("location = %s")
            params.append(location)
        
        # 执行查询
        items = self.db.get_items(conditions, params)  
        
        # 清空并填充表格
        self.ui.tableWidget.setRowCount(0)
        for row, item in enumerate(items):
            self.ui.tableWidget.insertRow(row)
            self._fill_table_row(row, item)
    
    def _fill_table_row(self, row, item):
        """填充表格行"""
        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(item['id'])))
        self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(item['name']))
        self.ui.tableWidget.setItem(row, 2, 
            QTableWidgetItem(item.get('category', '')))
        self.ui.tableWidget.setItem(row, 3, 
            QTableWidgetItem(item.get('location', '')))
        self.ui.tableWidget.setItem(row, 4, 
            QTableWidgetItem(str(item['quantity'])))
        self.ui.tableWidget.setItem(row, 5, 
            QTableWidgetItem(item.get('description', '')))
    def add_item(self):
        """添加物品"""
        dialog = ItemDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item_data = dialog.get_data()
            if item_data is None:  # 验证失败
                return
                
            if self.db.add_item(item_data):
                self.load_items()  # 刷新列表
            else:
                self._show_error("添加物品失败")
    
    def edit_item(self):
        """编辑物品"""
        selected = self._get_selected_item()
        if not selected:
            self._show_warning("请先选择要编辑的物品")
            return
        
        dialog = ItemDialog(self, selected)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if self.db.update_item(selected['id'], dialog.get_data()):
                self.load_items()
            else:
                self._show_error("更新物品失败")
    
    def delete_item(self):
        """删除物品"""
        selected = self._get_selected_item()
        if not selected:
            self._show_warning("请先选择要删除的物品")
            return
        
        if self._confirm_delete(selected['name']):
            if self.db.delete_item(selected['id']):
                self.load_items()
            else:
                self._show_error("删除物品失败")
    
    def _get_selected_item(self):
        """获取当前选中物品"""
        selected = self.ui.tableWidget.selectedItems()
        if not selected:
            return None
            
        return {
            'id': int(self.ui.tableWidget.item(selected[0].row(), 0).text()),
            'name': self.ui.tableWidget.item(selected[0].row(), 1).text(),
            'category': self.ui.tableWidget.item(selected[0].row(), 2).text(),
            'location': self.ui.tableWidget.item(selected[0].row(), 3).text(),
            'quantity': int(self.ui.tableWidget.item(selected[0].row(), 4).text()),
            'description': self.ui.tableWidget.item(selected[0].row(), 5).text()
        }
    
    def _show_warning(self, message):
        """显示警告"""
        QMessageBox.warning(self, "警告", message)
    
    def _show_error(self, message):
        """显示错误"""
        QMessageBox.critical(self, "错误", message)
    
    def _confirm_delete(self, name):
        """确认删除"""
        return QMessageBox.question(
            self, "确认删除",
            f"确定要删除物品 '{name}' 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes
if __name__ == "__main__":
    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 进入主事件循环
    sys.exit(app.exec())