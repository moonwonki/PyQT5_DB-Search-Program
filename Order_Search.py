import sys
import threading
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import *
import pymysql
import datetime

import csv
import json
from decimal import *
import xml.etree.ElementTree as ET


class MainWindow (QWidget):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.query = DB_Queries()

        self.setupUI()


    def setupUI(self):
        # 윈도우 설정
        self.setWindowTitle("주문 검색 윈도우")
        self.setGeometry(0, 0, 1104, 800)

        # 콤보 박스 설정
        self.customerComboBox = QComboBox()
        self.customerComboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.countryComboBox = QComboBox()
        self.countryComboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.cityComboBox = QComboBox()
        self.cityComboBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # DB 관련 콤보박스 설정
        self.comboBox_init()

        # 그룹 박스 설정
        searchControlGroupBox = QGroupBox("주문 검색")
        searchControlGroupBox.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)


        #라벨 설정
        searchCustomerLabel = QLabel("고객:")
        searchCustomerLabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        searchCountryLabel = QLabel("국가:")
        searchCountryLabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        searchCityLabel = QLabel("지역:")
        searchCityLabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.searchResultNumLabel = QLabel("검색된 주문의 개수: ")
        self.searchResultNumLabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)




        # 버튼 설정
        searchButton = QPushButton("검색")
        searchButton.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        searchButton.clicked.connect(self.searchButton_Clicked)
        resetButton = QPushButton("초기화")
        resetButton.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        resetButton.clicked.connect(self.resetButton_clicked)

        #테이블 설정
        self.tableWidget = QTableWidget() #추후 수정.

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.setRowCount(1000)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setHorizontalHeaderLabels(
            ["orderNo", "orderDate", "requiredDate", "shippedDate", "status", "customer",
             "comments"])
        self.tableWidget.cellClicked.connect(self.table_cellClicked)
        self.table_set("init")



        # layout 설정
        topLayout = QHBoxLayout()
        ControlLayout = QVBoxLayout()
        ControlComboLayout = QHBoxLayout()
        ButtonLayout = QVBoxLayout()

        worldLayout = QVBoxLayout()

        ControlComboLayout.addWidget(searchCustomerLabel)
        ControlComboLayout.addWidget(self.customerComboBox)
        ControlComboLayout.addWidget(searchCountryLabel)
        ControlComboLayout.addWidget(self.countryComboBox)
        ControlComboLayout.addWidget(searchCityLabel)
        ControlComboLayout.addWidget(self.cityComboBox)

        ControlLayout.addLayout(ControlComboLayout)
        ControlLayout.addWidget(self.searchResultNumLabel)
        searchControlGroupBox.setLayout(ControlLayout)

        ButtonLayout.addWidget(searchButton)
        ButtonLayout.addWidget(resetButton)

        topLayout.addWidget(searchControlGroupBox,3)
        topLayout.addLayout(ButtonLayout,1)

        worldLayout.addLayout(topLayout,1)
        worldLayout.addWidget(self.tableWidget,4)
        self.setLayout(worldLayout)

    def comboBox_init(self):
        try: self.countryComboBox.disconnect()
        except Exception: pass
        self.countryComboBox.clear()
        self.customerComboBox.clear()
        self.cityComboBox.clear()

        customerList = list()
        customerList.append("ALL")
        countryList = list()
        countryList.append("ALL")
        cityList = list()
        cityList.append("ALL")
        tmp = self.query.selectCustomerName()
        for customers in tmp:
            for k, v in customers.items():
                customerList.append(v)
        customerList.sort()

        tmp = self.query.selectCountryName()
        for country in tmp:
            for k, v in country.items():
                countryList.append(v)
        countryList.sort()

        tmp = self.query.selectCityName()
        for city in tmp:
            for k, v in city.items():
                cityList.append(v)
        cityList.sort()

        for item in customerList:
            self.customerComboBox.addItem(item)
        for item in countryList:
            self.countryComboBox.addItem(item)
        for item in cityList:
            self.cityComboBox.addItem(item)
        # self.customerComboBox.currentIndexChanged.connect()
        self.countryComboBox.currentIndexChanged.connect(self.countryComboBox_selected)
        # self.cityComboBox.currentIndexChanged.connect()

    def table_set(self, command):
        self.lock.acquire()
        if (command == "search"):
            orderList = self.query.selectOrders(self.customerComboBox.currentText(),self.countryComboBox.currentText(),self.cityComboBox.currentText())
        else:
            orderList = self.query.selectAllOrders()

        self.tableWidget.clearContents()

        if (len(orderList) == 0):
            self.searchResultNumLabel.setText("검색된 주문의 개수: " + str(0))
            self.lock.release()
            return

        sorted(orderList, key=lambda x: x['orderNo'])
        for rowIDX, orders in enumerate(orderList):
            for columnIDX, (k, v) in enumerate(orders.items()):
                if (type(v) == datetime.date):
                    v = v.strftime("%Y-%m-%d")
                if (type(v) == int):
                    v = str(v)
                item = QTableWidgetItem(v)
                self.tableWidget.setItem(rowIDX, columnIDX, item)

        self.searchResultNumLabel.setText("검색된 주문의 개수: " + str(len(orderList)))
        self.lock.release()

    def searchButton_Clicked(self):
        self.table_set("search")

    def countryComboBox_selected(self):
        if (self.countryComboBox.currentText() == "ALL"):
            self.comboBox_init()
            return
        cityList = ["ALL"]
        tmp = self.query.selectCityNameInCountry(self.countryComboBox.currentText())
        for city in tmp:
            for k, v in city.items():
                cityList.append(v)
        cityList.sort()

        self.cityComboBox.clear()
        for item in cityList:
            self.cityComboBox.addItem(item)

    def resetButton_clicked(self):
        self.table_set("init")
        print("init")
        self.comboBox_init()

    def table_cellClicked(self, rowIDX, columnIDX):
        print("tableClicked")
        orderNum = self.tableWidget.item(rowIDX,0)
        self.orderWindow = orderWindow(orderNum.text())
        self.orderWindow.show()



class orderWindow (QWidget):
    def __init__(self,orderNum):
        super().__init__()
        print(orderNum)
        self.orderNumber = orderNum
        self.query = DB_Queries()
        self.setupUI()
        self.show()

    def setupUI(self):
        # 윈도우 설정
        self.setWindowTitle("주문 상세 내역")
        self.setGeometry(0, 0, 1200,700)

        # 상단 그룹박스와 라벨
        self.topGroupBox = QGroupBox("주문 상세 내역")
        self.orderNoLabel = QLabel("주문번호 : ")
        self.productNumLabel = QLabel("상품개수 : ")
        self.priceLabel = QLabel("주문액: ")

        # 테이블위젯
        self.tableWidget = QTableWidget()
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.setRowCount(100)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setHorizontalHeaderLabels(
            ["orderLineNo", "productCode", "productName", "quantity", "priceEach", "상품주문액"])

        # 하단 그룹박스
        self.bottomGroupBox = QGroupBox("파일출력")
        self.csvRadioBtn = QRadioButton("CSV")
        self.csvRadioBtn.setChecked(True)
        self.jsonRadioBtn = QRadioButton("JSON")
        self.xmlRadioBtn = QRadioButton("XML")
        self.saveBtn = QPushButton("저장")
        self.saveBtn.clicked.connect(self.saveBtn_clicked)

        # DB 정보 채우기
        self.data_set()

        # 레이아웃
        self.wholeLayout = QVBoxLayout()
        self.topGroupBoxLayout = QHBoxLayout()
        self.bottomGroupBoxLayout = QHBoxLayout()

        self.topGroupBoxLayout.addWidget(self.orderNoLabel)
        self.topGroupBoxLayout.addWidget(self.productNumLabel)
        self.topGroupBoxLayout.addWidget(self.priceLabel)
        self.topGroupBox.setLayout(self.topGroupBoxLayout)

        self.bottomGroupBoxLayout.addWidget(self.csvRadioBtn)
        self.bottomGroupBoxLayout.addWidget(self.jsonRadioBtn)
        self.bottomGroupBoxLayout.addWidget(self.xmlRadioBtn)
        self.bottomGroupBoxLayout.addWidget(self.saveBtn)
        self.bottomGroupBox.setLayout(self.bottomGroupBoxLayout)

        self.wholeLayout.addWidget(self.topGroupBox,1)
        self.wholeLayout.addWidget(self.tableWidget,2)
        self.wholeLayout.addWidget(self.bottomGroupBox,1)

        self.setLayout(self.wholeLayout)

    def data_set(self):
        orderList = self.query.selectSpecificOrder(self.orderNumber)
        self.orderList = list()
        quantitySum = 0
        priceSum = 0
        for rowIDX, orders in enumerate(orderList):
            tmp = dict()
            for columnIDX, (k, v) in enumerate(orders.items()):
                key = k
                value = v
                if (columnIDX == 0):
                    key = "orderLineNo"
                elif (columnIDX == 1):
                    key = "productCode"
                elif (columnIDX == 2):
                    key = "productName"
                elif (columnIDX == 3):
                    key = "quantity"
                    quantitySum += 1
                elif (columnIDX == 4):
                    key = "priceEach"
                    value = str(v)
                else:
                    priceSum += v
                    value = str(v)
                    key = "상품주문액"
                tmp[key] = value
                v = str(v)
                item = QTableWidgetItem(v)
                self.tableWidget.setItem(rowIDX, columnIDX, item)
            self.orderList.append(tmp)
        self.orderNoLabel.setText("주문번호 : " + str(self.orderNumber))
        self.productNumLabel.setText("상품개수 : " + str(quantitySum))
        self.priceLabel.setText("주문액 : " + str(priceSum))
        print(self.orderList)

    def saveBtn_clicked(self):
        if (self.csvRadioBtn.isChecked()):
            self.saveCSV()
        elif (self.xmlRadioBtn.isChecked()):
            self.saveXML()
        elif (self.jsonRadioBtn.isChecked()):
            self.saveJSON()
        else:
            return

    def saveCSV(self):
        with open(str(self.orderNumber)+'.csv', 'w', encoding='utf-8', newline='') as f:
            wr = csv.writer(f)

            # 테이블 헤더를 출력
            columnNames = list(self.orderList[0].keys())
            wr.writerow(columnNames)

            # 테이블 내용을 출력
            for row in self.orderList:  # 딕셔너리를 꺼내고
                orderInfo = list(row.values()) # 그 안에 value로 리스트를 만들어서
                wr.writerow(orderInfo) # 출력하는 구조

    def saveJSON(self):
        name = str(self.orderNumber)
        newDict = dict()
        newDict[name] = self.orderList

        with open(str(self.orderNumber)+'.json', 'w', encoding='utf-8') as f:
            json.dump(newDict, f, indent=4, ensure_ascii=False)

    def saveXML(self):
        name = str(self.orderNumber)
        newDict = dict()
        newDict[name] = self.orderList

        tableName = list(newDict.keys())[0]
        tableRows = list(newDict.values())[0]

        rootElement = ET.Element('Table')
        rootElement.attrib['name'] = tableName

        for row in tableRows:
            rowElement = ET.Element('Row')
            rootElement.append(rowElement)
            for columnName in list(row.keys()):
                if (row[columnName] == None):
                    rowElement.attrib[columnName] = ''
                elif (type(row[columnName]) == int):
                    rowElement.attrib[columnName] = str(row[columnName])
                elif (type(row[columnName]) == Decimal):
                    rowElement.attrib[columnName] = str(row[columnName])
                else:
                    rowElement.attrib[columnName] = row[columnName]
        # XDM 트리를 콘솔에 출력
        try:ET.ElementTree(rootElement).write(str(self.orderNumber)+'.xml', encoding='utf-8', xml_declaration=True)
        except Exception as e : print(e)

# json dump 메소드에서 발생하는 'object of type decimal is not json serializable' 에러를 해결하기 위한 encoder 클래스
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # 만약 decimal 형태의 객체를 받았다면 스트링으로 변환하여 리턴
        if isinstance(obj, Decimal):
            return str(obj)
        # 아니라면 그냥 똑같이 수행.
        return json.JSONEncoder.default(self, obj)


class DB_Utils:
    # SQL 질의문(sql과 params)을 전달받아 실행하는 메소드
    def queryExecutor(self, db, sql, params):
        conn = pymysql.connect(host='localhost', user='guest', password='bemyguest', db='classicmodels', charset='utf8')
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:     # dictionary based cursor
                cursor.execute(sql, params)                             # dynamic SQL
                rows = cursor.fetchall()
                return rows
        except Exception as e:
            print(e)
            print(type(e))
        finally:
            cursor.close()
            conn.close()

class DB_Queries:
    # 검색문을 각각 하나의 메소드로 정의

    # 콤보박스 리스트를 위한 메소드 4개
    def selectCustomerName(self):
        sql = "SELECT DISTINCT name FROM customers"

        util = DB_Utils()
        rows = util.queryExecutor(db="classicmodels", sql=sql,params=None)
        return rows


    def selectCountryName(self):
        sql = "SELECT DISTINCT country FROM customers"

        util = DB_Utils()
        rows = util.queryExecutor(db="classicmodels", sql=sql, params=None)
        return rows

    def selectCityName(self):
        sql = "SELECT DISTINCT city FROM customers"

        util = DB_Utils()
        rows = util.queryExecutor(db="classicmodels",sql=sql,params=None)
        return rows

    def selectCityNameInCountry(self,country):
        sql = "SELECT DISTINCT city FROM customers where country = %s"

        util = DB_Utils()
        rows = util.queryExecutor(db="classicmodels",sql=sql,params=country)
        return rows

    # DB 모든 주문 검색문
    def selectAllOrders(self):
        sql = "SELECT orders.orderNo, orders.orderDate, orders.requiredDate, orders.shippedDate, orders.status, customers.name, orders.comments FROM customers NATURAL JOIN orders"

        util = DB_Utils()
        rows = util.queryExecutor(db="classicmodels", sql=sql, params=None)
        return rows

    # DB 모든 콤보박스를 고려하는 주문
    def selectOrders(self, customer, country, city):
        sql = "SELECT orders.orderNo, orders.orderDate, orders.requiredDate, orders.shippedDate, orders.status, customers.name, orders.comments FROM customers NATURAL JOIN orders"
        count = 0
        whereSQL = ""
        whereSQLParams = list()
        if (customer != "ALL"):
            whereSQL += " customers.name = %s"
            whereSQLParams.append(customer)
            count += 1
        if (country != "ALL"):
            if (count >= 1):
                whereSQL += " AND"
            whereSQL += " customers.country = %s"
            whereSQLParams.append(country)
            count += 1
        if (city != "ALL"):
            if (count >= 1):
                whereSQL += " AND"
            whereSQL += " customers.city = %s"
            whereSQLParams.append(city)
            count += 1

        if (count > 0):
            sql += " WHERE"
            sql += whereSQL
            params = tuple(whereSQLParams)
        else:
            params = None

        util = DB_Utils()
        rows = util.queryExecutor(db="classicmodels", sql=sql, params=params)
        return rows







    # 주문 상세 내역 검색문
    def selectSpecificOrder(self, orderNum):
        sql = "SELECT orderDetails.orderLineNo, products.productCode, products.name, orderDetails.quantity, " \
              "orderDetails.priceEach, orderDetails.quantity * orderDetails.priceEach FROM orderDetails NATURAL JOIN " \
              "orders NATURAL JOIN products WHERE orderDetails.orderNo = %s ORDER BY orderDetails.orderLineNo"
        params = (orderNum)

        util = DB_Utils()
        rows = util.queryExecutor(db="classicmodels", sql=sql, params=params)
        return rows


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()