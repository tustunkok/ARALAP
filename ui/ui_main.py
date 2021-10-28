import sys
import subprocess
import json
import PySide6
from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader
from .models import ResearchAssistantModel, Days, ResearchAssistantProgramModel

PROGRAMS_DIR = None
COURSES_FILE = None
MAIN_WINDOW = None
EXISTING_PROGRAM = None

def load_assistant_data():
    assistant_list_prog = subprocess.run(['python', 'cli.py', 'interop', '-p', f'{PROGRAMS_DIR}', '-c', f'{COURSES_FILE}', '-n'], capture_output=True, text=True)
    ra_model = ResearchAssistantModel(assistants=assistant_list_prog.stdout.split('\n')[:-1])
    MAIN_WINDOW.assistantLV.setModel(ra_model)


def display_selected_program(modelIndex: QtCore.QModelIndex):    
    assistant_name = modelIndex.data(role=QtCore.Qt.DisplayRole)

    assistant_prog_proc = subprocess.run(['python', 'cli.py', 'interop', '-p', f'{PROGRAMS_DIR}', '-c', f'{COURSES_FILE}', '-f', 'assigned-programs.json', f'{assistant_name}'], capture_output=True, text=True)
    
    program_obj = json.loads(assistant_prog_proc.stdout)
    
    program = [list() for _ in range(9)]
    for idx in range(len(program)):
        program[idx] = [None] * len(Days)
    
    for assigned_lab in program_obj['assigned_labs']:
        for period in assigned_lab['periods']:
            program[period][Days[assigned_lab['day']].value] = assigned_lab['id']

    program_model = ResearchAssistantProgramModel(program=program)
    MAIN_WINDOW.programTV.setModel(program_model)


def programs_dir_select():
    global PROGRAMS_DIR
    dlg = QtWidgets.QFileDialog()
    dlg.setFileMode(QtWidgets.QFileDialog.Directory)
    dlg.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
    dlg.exec()
    PROGRAMS_DIR = dlg.selectedFiles()[0]
    load_assistant_data()


def courses_dir_select():
    global COURSES_FILE
    dlg = QtWidgets.QFileDialog()
    dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
    dlg.setNameFilter("Json files (*.json)")
    dlg.exec()
    COURSES_FILE = dlg.selectedFiles()[0]


def create_new_program():
    if EXISTING_PROGRAM is None:
        subprocess.run(['python', 'cli.py', 'schedule', '-p', f'{PROGRAMS_DIR}', '-c', f'{COURSES_FILE}'])
    else:
        subprocess.run(['python', 'cli.py', 'schedule', '-p', f'{PROGRAMS_DIR}', '-c', f'{COURSES_FILE}', '-e', f'{EXISTING_PROGRAM}'])


def choose_existing_program():
    global EXISTING_PROGRAM
    dlg = QtWidgets.QFileDialog()
    dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
    dlg.setNameFilter("Json files (*.json)")
    dlg.exec()
    EXISTING_PROGRAM = dlg.selectedFiles()[0]


def main():
    global MAIN_WINDOW
    print("PySide6", PySide6.__version__)
    print("Qt", QtCore.__version__)

    app = QtWidgets.QApplication(sys.argv)

    ui_file = QtCore.QFile("./ui/uis/mainwindow.ui")
    ui_file.open(QtCore.QFile.ReadOnly)
    loader = QUiLoader()

    MAIN_WINDOW = loader.load(ui_file)
    MAIN_WINDOW.assistantLV.clicked.connect(display_selected_program)
    MAIN_WINDOW.programsDirBtn.clicked.connect(programs_dir_select)
    MAIN_WINDOW.coursesDirBtn.clicked.connect(courses_dir_select)
    MAIN_WINDOW.createNewProgramBtn.clicked.connect(create_new_program)
    MAIN_WINDOW.chooseExistingProgBtn.clicked.connect(choose_existing_program)
    MAIN_WINDOW.show()

    sys.exit(app.exec())
