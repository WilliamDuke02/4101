import sys
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QGridLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics

class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CustomComboBox, self).__init__(parent)
        self.currentIndexChanged.connect(self.adjustComboBoxSize)

    def adjustComboBoxSize(self):
        # Adjust the size of the combo box to fit the selected item
        text = self.currentText()
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.boundingRect(text).width()
        self.setFixedWidth(text_width + 30)

    def showPopup(self):
        # Adjust the size before showing the popup
        self.adjustComboBoxSize()
        super(CustomComboBox, self).showPopup()

def fetch_column_values(column_name, filter_column=None, filter_value=None):
    with sqlite3.connect('merged_data.db') as conn:
        cursor = conn.cursor()
        if filter_column and filter_value:
            query = f"""SELECT DISTINCT "{column_name}" FROM merged_currentvins_modified 
                        WHERE "{filter_column}" = ?"""
            cursor.execute(query, (filter_value,))
        else:
            query = f'SELECT DISTINCT "{column_name}" FROM merged_currentvins_modified'
            cursor.execute(query)

        return [str(row[0]) for row in cursor.fetchall()]
def minimumSizeHint(self):
        size = super(CustomComboBox, self).minimumSizeHint()
        size.setHeight(20)  # Reduce the default height as needed
        return size
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Custom Query Builder'
        self.comboboxes = {}  # Initialize the comboboxes dictionary
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 1264, 629)  # Adjust the size to match the horizontal layout
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setHorizontalSpacing(10)
        self.grid_layout.setVerticalSpacing(0)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)

        # Define the order of combo boxes and their titles
        ordered_columns = [
            ('Vehicle Manufacturer', 'Vehicle Manufacturer'),
            ('Make', 'Make'),
            ('Model-full', 'Model-full'),
            ('Technology', 'Technology'),
            ('Model Year', 'Model Year'),
            ('Vehicle Category', 'Vehicle Category'),
            ('Vehicle Use Case', 'Vehicle Use Case'),
            ('Vehicle Class', 'Vehicle Class'),
            ('Zip', 'Zip Code')
        ]

        # Initialize combo boxes with the ordered names and add labels
        for i, (name, title) in enumerate(ordered_columns):
            label = QLabel(title)
            self.comboboxes[name] = CustomComboBox()
            self.comboboxes[name].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

            # Place the label in the first row and the combo box in the second row
            # Both label and combo box are in column i
            self.grid_layout.addWidget(label, 0, i)  # Label in column i of the first row
            self.grid_layout.addWidget(self.comboboxes[name], 1, i)  # Combo box in column i of the second row

            self.populateComboBox(self.comboboxes[name], name)

            if name in ['Make', 'Model-full']:
                self.comboboxes[name].setVisible(False)

        # Place the export button below the combo boxes
        self.export_button = QPushButton('Export')
        self.export_button.clicked.connect(self.exportToExcel)
        # Span the export button across all columns, placing it in the third row
        self.grid_layout.addWidget(self.export_button, 2, 0, 1, len(ordered_columns), Qt.AlignCenter) 

        self.setLayout(self.grid_layout)
    def populateComboBox(self, combo_box, column_name, values=None):
        combo_box.clear()
        combo_box.addItem("Any")
        if not values:
            values = fetch_column_values(column_name)
        sorted_values = sorted(values, key=lambda s: s.lower())
        combo_box.addItems(sorted_values)

        if column_name == 'Vehicle Manufacturer':
            combo_box.currentIndexChanged.connect(lambda: self.updateDependentComboBox('Make'))
        elif column_name == 'Make':
            combo_box.currentIndexChanged.connect(lambda: self.updateDependentComboBox('Model-full'))

    def updateDependentComboBox(self, dependent_column):
        if dependent_column == 'Make':
            manufacturer = self.comboboxes['Vehicle Manufacturer'].currentText()
            if manufacturer != "Any":
                self.comboboxes['Make'].setVisible(True)
                makes = fetch_column_values('Make', 'Vehicle Manufacturer', manufacturer)
                self.populateComboBox(self.comboboxes['Make'], 'Make', makes)
            else:
                self.comboboxes['Make'].setVisible(False)
        elif dependent_column == 'Model-full':
            make = self.comboboxes['Make'].currentText()
            if make != "Any":
                self.comboboxes['Model-full'].setVisible(True)
                models = fetch_column_values('Model-full', 'Make', make)
                self.populateComboBox(self.comboboxes['Model-full'], 'Model-full', models)
            else:
                self.comboboxes['Model-full'].setVisible(False)

    def exportToExcel(self):
        try:
            selections = {column_name: combo_box.currentText() for column_name, combo_box in self.comboboxes.items() if combo_box.currentText() != "Any"}
            query_parts = [f'"{column_name}" = ?' for column_name in selections.keys()]
            query = f"SELECT * FROM merged_currentvins_modified WHERE {' AND '.join(query_parts)}" if selections else "SELECT * FROM merged_currentvins_modified"

            with sqlite3.connect('merged_data.db') as conn:
                df = pd.read_sql_query(query, conn, params=list(selections.values()))
                file_name = f'exported_data_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
                df.to_excel(file_name, index=False)
                print(f"Data exported to '{file_name}'.")
        except (sqlite3.Error, Exception) as e:
            print(f"Error during export: {e}")
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    app.exec_()
