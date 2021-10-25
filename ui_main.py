import sys
import subprocess
import json
import PySide6
from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader
from models import ResearchAssistantModel, Days, ResearchAssistantProgramModel

ALL_PROGRAMS = None

def load_assistant_data(window):
    assistant_list_prog = subprocess.run(['python', 'main.py', 'list', 'programs'], capture_output=True, text=True)
    assistant_data = json.loads(assistant_list_prog.stdout)
    ra_model = ResearchAssistantModel(assistants=assistant_data)
    window.assistantLV.setModel(ra_model)

def load_program_data():
    global ALL_PROGRAMS
    assistant_prog_proc = subprocess.run(['python', 'main.py', 'create', '-e', 'ui-test-assigned-programs.json', 'courses.json', 'programs'], capture_output=True, text=True)
    program_data = json.loads(assistant_prog_proc.stdout)
    all_programs = dict()
    for idx, assistant in enumerate(program_data):
        program = [list() for _ in range(9)]
        for idx in range(len(program)):
            program[idx] = [None] * len(Days)
        
        for assigned_lab in assistant['assigned_labs']:
            for period in assigned_lab['periods']:
                program[period][Days[assigned_lab['day']].value] = assigned_lab['id']
        all_programs[assistant['name']] = program
    
    ALL_PROGRAMS = all_programs

def display_selected_program(modelIndex: QtCore.QModelIndex, window):
    global ALL_PROGRAMS
    
    model_index = modelIndex.data(role=QtCore.Qt.DisplayPropertyRole)
    program = ALL_PROGRAMS.get(model_index['name'])
    program_model = ResearchAssistantProgramModel(program=program)
    window.programTV.setModel(program_model)

if __name__ == '__main__':
    print("PySide6", PySide6.__version__)
    print("Qt", QtCore.__version__)

    app = QtWidgets.QApplication(sys.argv)

    ui_file = QtCore.QFile("uis/mainwindow.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    loader = QUiLoader()

    window = loader.load(ui_file)
    window.assistantLV.clicked.connect(lambda x: display_selected_program(x, window))
    window.show()

    load_assistant_data(window)
    load_program_data()

    sys.exit(app.exec())
