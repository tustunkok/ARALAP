from PySide6 import QtCore
from PySide6.QtCore import QAbstractListModel, Qt, QAbstractTableModel
from enum import Enum

Days = Enum('Days', 'mon tue wed thu fri', start=0)

class ResearchAssistantModel(QAbstractListModel):
    def __init__(self, *args, assistants=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.assistants = assistants or []
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.assistants[index.row()]['name']
        
        if role == Qt.DisplayPropertyRole:
            return self.assistants[index.row()]

    def rowCount(self, index):
        return len(self.assistants)


class ResearchAssistantProgramModel(QAbstractTableModel):
    def __init__(self, *args, program=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.program = program or []
    
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.program[index.row()][index.column()]
        
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ['Monday', 'Tuestday', 'Wednesday', 'Thursday', 'Friday'][section]
            elif orientation == Qt.Vertical:
                return [f'{h:02d}.30 - {h + 1:02d}.20' for h in range(9, 18)][section]

    def rowCount(self, index):
        return len(self.program)

    def columnCount(self, index):
        return len(self.program[0])
