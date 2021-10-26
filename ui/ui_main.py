import sys
import subprocess
import json
import PySide6
from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader
from models import ResearchAssistantModel, Days, ResearchAssistantProgramModel

def load_assistant_data(window):
    assistant_list_prog = subprocess.run(['python', '../cli.py', 'interop', '-p', '../programs/', '-c', '../jsons/courses.json', '-n'], capture_output=True, text=True)
    print(assistant_list_prog.stderr)
    ra_model = ResearchAssistantModel(assistants=assistant_list_prog.stdout.split('\n'))
    window.assistantLV.setModel(ra_model)

def display_selected_program(modelIndex: QtCore.QModelIndex, window):    
    assistant_name = modelIndex.data(role=QtCore.Qt.DisplayRole)

    assistant_prog_proc = subprocess.run(['python', '../cli.py', 'interop', '-p', '../programs/', '-c', '../jsons/courses.json', '-f', '../assigned-programs.json', f'{assistant_name}'], capture_output=True, text=True)
    
    program_obj = json.loads(assistant_prog_proc.stdout)
    
    program = [list() for _ in range(9)]
    for idx in range(len(program)):
        program[idx] = [None] * len(Days)
    
    for assigned_lab in program_obj['assigned_labs']:
        for period in assigned_lab['periods']:
            program[period][Days[assigned_lab['day']].value] = assigned_lab['id']

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
    # load_program_data()

    sys.exit(app.exec())
