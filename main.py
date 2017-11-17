"""
Kochka Qt application

Copyright 2017 Pavel Folov
"""

__version__ = '0.1'
__author__ = 'Pavel Frolov'

import sys
import os.path

from PyQt4 import QtGui, QtCore

import design
from kochkalib import Set, Exercise, ExerciseTxtParser, save_exercises_to_file

# todo: i18n
# todo: icon
# todo: threading for load and save data


class KochkaApp(QtGui.QMainWindow, design.Ui_MainWindow):
    """Main Qt application"""

    data_filename = 'data.txt'

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self._buttonsConnects()

        self.exerciseDate.setDate(QtCore.QDate.currentDate())

        self.setModel = SetModel(self.setsTableView)
        self.setsTableView.setModel(self.setModel)
        self.setsTableView.customContextMenuRequested.connect(
            self.slot_setsTable_customContextMenuRequested)
        self.setModel.totalWeightChanged.connect(
            self.totalSetsWeightLcd.display)

        self.exerciseModel = ExerciseModel(self.exercisesTableView)
        self.exercisesTableView.setModel(self.exerciseModel)

        self._initMenu()
        self._appInit()
        self.slot_loadData_clicked()

    def _buttonsConnects(self):
        self.addSetBtn.clicked.connect(self.slot_addSet_clicked)
        self.clearExerciseBtn.clicked.connect(self.slot_clearSet_clicked)
        self.addExerciseBtn.clicked.connect(self.slot_addExercise_clicked)
        self.loadDataBtn.clicked.connect(self.slot_loadData_clicked)
        self.saveDataBtn.clicked.connect(self.slot_saveData_clicked)

    def _initMenu(self):
        self.sets_table_menu = menu = QtGui.QMenu(self)
        delete_action = QtGui.QAction(QtGui.QIcon.fromTheme('edit-delete'),
                                      'Удалить', self)
        delete_action.triggered.connect(self.slot_setsTabel_deleteRow)
        self.sets_table_menu.addAction(delete_action)

    def _appInit(self):
        if not os.path.exists(self.data_filename):
            with open(self.data_filename, 'w'):
                pass

    def slot_setsTable_customContextMenuRequested(self, pos):
        self.sets_table_menu.popup(
            self.setsTableView.viewport().mapToGlobal(pos))

    def slot_setsTabel_deleteRow(self):
        # http://doc.qt.io/qt-5/model-view-programming.html#inserting-and-removing-rows
        # https://evileg.com/en/post/76/
        # import ipdb; ipdb.set_trace()

        rows = self.setsTableView.selectionModel().selectedRows()
        if not rows:
            self._showError("No selected set")
            return
        self.setModel.removeSetByIndex(rows[0].row())

    def slot_loadData_clicked(self):
        self.exerciseModel.clear()

        parser = ExerciseTxtParser(self.data_filename)
        parser.on_error.append(lambda e: self._showError(e))

        for exercise in parser:
            self.exerciseModel.addExercise(exercise)

    def slot_saveData_clicked(self):
        save_exercises_to_file(
            self.data_filename,
            self.exerciseModel.exercises
        )

    def slot_addSet_clicked(self):
        self.setModel.addSet(Set(
            self.weight.text(),
            self.count.text(),
            self.setCount.text()
        ))

    def slot_clearSet_clicked(self):
        self.setModel.clear()

    def _check_exercise(self) -> bool:
        if not self.exerciseName.currentText():
            self._showError('Нет имени упражнения для добавления')
            return False
        if not self.setModel.sets:
            self._showError('Нет сетов для добавления')
            return False
        return True

    def slot_addExercise_clicked(self):
        if not self._check_exercise():
            return
        self.exerciseModel.addExercise(Exercise(
            self.exerciseDate.text(),
            self.exerciseName.currentText(),
            sets=self.setModel.sets
        ))

    def _showError(self, message):
        QtGui.QMessageBox(
            QtGui.QMessageBox.Warning,
            'Error',
            message,
            QtGui.QMessageBox.Ok
        ).exec_()

    def _showMessage(self, message, title='Information'):
        QtGui.QMessageBox(
            QtGui.QMessageBox.Information,
            title,
            message,
            QtGui.QMessageBox.Ok
        ).exec_()


class SetModel(QtCore.QAbstractTableModel):
    """Model for Set TableView"""

    totalWeightChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self)
        self.gui = parent
        self.colLabels = ['вес', 'раз', 'подходов', 'объём']
        self.sets = []

    def addSet(self, set_):
        # todo: implement insertRows
        # http://doc.qt.io/qt-4.8/model-view-programming.html#inserting-and-removing-rows
        self.beginResetModel()
        self.sets.append(set_)
        self.endResetModel()
        self.totalWeightChanged.emit(self.calcTotalWeight())

    def removeSetByIndex(self, index):
        # todo: implement removeRow
        # http://doc.qt.io/qt-4.8/model-view-programming.html#inserting-and-removing-rows
        self.beginResetModel()
        del self.sets[index]
        self.endResetModel()
        self.totalWeightChanged.emit(self.calcTotalWeight())

    def calcTotalWeight(self):
        return sum(s.total_weight for s in self.sets)

    def clear(self):
        self.beginResetModel()
        self.sets = []
        self.endResetModel()
        self.totalWeightChanged.emit(0)

    def rowCount(self, parent=None, **kwargs):
        return len(self.sets)

    def columnCount(self, parent=None, **kwargs):
        return len(self.colLabels)

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return None
        if role == QtCore.Qt.DisplayRole:
            set_ = self.sets[index.row()]
            col = index.column()
            return set_.total_weight if col == 3 \
                else getattr(set_, Set.ATTRS[col])
        return ''

    def headerData(self, section, orientation, role):
        header_cond = (orientation == QtCore.Qt.Horizontal and
                       role == QtCore.Qt.DisplayRole)
        if header_cond:
            return self.colLabels[section]
        return None


class ExerciseModel(QtCore.QAbstractTableModel):
    """Model for Exercise TableView"""
    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self)
        self.gui = parent
        self.colLabels = ['дата', 'название', 'резюме', 'объём']
        self.exercises = []

    def addExercise(self, exercise):
        self.beginResetModel()
        self.exercises.append(exercise)
        self.endResetModel()

    def clear(self):
        self.beginResetModel()
        self.exercises = []
        self.endResetModel()

    def rowCount(self, parent=None, **kwargs):
        return len(self.exercises)

    def columnCount(self, parent=None, **kwargs):
        return len(self.colLabels)

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return None
        if role == QtCore.Qt.DisplayRole:
            exercise = self.exercises[index.row()]
            col = index.column()
            if col == 2:
                return exercise.sets_str
            elif col == 3:
                return exercise.total_weight
            else:
                return getattr(exercise, Exercise.ATTRS[col])
        return ''

    def headerData(self, section, orientation, role):
        header_cond = (orientation == QtCore.Qt.Horizontal and
                       role == QtCore.Qt.DisplayRole)
        if header_cond:
            return self.colLabels[section]
        return None


def main():

    # to remove "QCoreApplication::exec: The event loop is already running"
    # from console when debugging by ipdb
    from PyQt4.QtCore import pyqtRemoveInputHook
    pyqtRemoveInputHook()

    app = QtGui.QApplication(sys.argv)
    form = KochkaApp()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
