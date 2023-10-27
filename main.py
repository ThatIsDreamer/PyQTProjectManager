from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QRadioButton, QVBoxLayout, QGroupBox, \
    QMessageBox
from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5 import uic, QtWidgets, QtCore
import sys
import os
import shutil
import sqlite3

con = sqlite3.connect("config.sqlite")
con.row_factory = sqlite3.Row
cur = con.cursor()

def DeletProj(id):
    cur.execute(f"""
        DELETE from projects
        where id = {id}
    """)
    con.commit()


def GetProp(where, what):
    result = cur.execute(f"""
        select {what} from {where}
    """).fetchall()
    return [dict(row) for row in result]


def GetTemplate(name):
    result = cur.execute(f"""
        select * from templates
        where name = "{name}"
    """).fetchall()
    return [dict(row) for row in result][0]


def GetAllProjects():
    result = cur.execute(f"""
          select * from projects
    """).fetchall()
    return [dict(row) for row in result]


def GetProject(name):
    result = cur.execute(f"""
          select * from Projects
          where name = "{name}"
    """).fetchall()
    return [dict(row) for row in result]


def GetAllTags():
    result = cur.execute(f"""
          select DISTINCT name from Tags
    """).fetchall()
    return [dict(row)["name"] for row in result]


def GetAllTemplates():
    result = cur.execute(f"""
          select * from Templates
    """).fetchall()
    return [dict(row) for row in result]


def TemplateCreate(template):
    cur.execute(f"""
        INSERT INTO Templates(name, filling) VALUES("{template["name"]}", "{template["filling"]}")
    """)
    con.commit()


def AddTag(tag):
    cur.execute(f"""
        INSERT INTO Tags(name) VALUES("{tag}")
    """)
    con.commit()


def UpdateConfig(prop, val):
    cur.execute(f"""
        UPDATE config
        set {prop} = "{val}"
    """)
    con.commit()


def CreateProject(proj):
    cur.execute(f"""
        INSERT INTO Projects(name, dir, tag) VALUES("{proj["name"]}", "{proj["dir"]}", "{proj["tag"]}")
    """)
    con.commit()


if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

light_theme = """
      QWidget {
          background-color: white;
          color: black;
      }
      QPushButton {
          background-color: lightgray;
      }
      """

dark_theme = """
      QWidget {
          background-color: #2d2d2d;
          color: white;
      }
      QPushButton {
          background-color: #555555;
      }
      """


class FirstSetup(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        global light_theme
        global dark_theme
        global GetProp
        global UpdateConfig

        if GetProp("config", "*")[0]["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)

        uic.loadUi("config.ui", self)
        self.pushButton.clicked.connect(self.openFileDialog)

    def openFileDialog(self):
        prfl = str(QFileDialog.getExistingDirectory(self, "Выбери папку для проектов"))
        UpdateConfig("projectFolder", prfl)

        if prfl != "":
            self.close()
            self.open_mainscreen()

    def open_mainscreen(self):
        self.second_form = MainScreen()
        self.second_form.show()


class MainScreen(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        global light_theme
        global dark_theme
        global GetProp
        global UpdateConfig
        global GetAllProjects
        global DeletProj

        uic.loadUi("main.ui", self)
        self.createProjectBtn.clicked.connect(self.openProjectCreateScreen)
        self.settingButton.clicked.connect(self.openSettings)

        if GetProp("config", "*")[0]["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)

        self.renderPorojects()

    def checkIfProjectExsist(self):
        prjts = GetAllProjects()
        for el in prjts:
            if not os.path.isdir(f'{GetProp("config", "ProjectFolder")[0]["projectFolder"]}/{el["dir"]}'):
                DeletProj(el["id"])
                print("DELETING!!!!", el["id"])

    def renderPorojects(self):
        self.checkIfProjectExsist()
        prjts = GetAllProjects()
        for el in prjts:

            group_box = QGroupBox(el["name"])
            group_box_layout = QVBoxLayout()
            font = QFont()
            font.setPointSize(14)
            group_box.setFont(font)
            if el["tag"] is None:
                el["tag"] = "Нет"

            button = QPushButton(f'Открыть в vscode: {el["name"]}')
            button.clicked.connect(self.openInCode)
            deleteButton = QPushButton(f'Удалить: {el["name"]}')
            deleteButton.setStyleSheet("""QPushButton {color: red; font-size: 14px}""")
            deleteButton.clicked.connect(self.delete)
            label = QLabel(f'Тэг: {el["tag"]}')
            group_box_layout.addWidget(label)
            group_box_layout.addWidget(button)
            group_box_layout.addWidget(deleteButton)

            group_box.setLayout(group_box_layout)
            self.verticalLayout.addWidget(group_box)

    def delete(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Удалить проект?")
        dlg.setText("Удалить проект?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()

        if button == QMessageBox.Yes:
            projectname = self.sender().text().split(":")[1].strip()
            project = GetProject(projectname)[0]

            shutil.rmtree(f'{GetProp("config", "projectFolder")[0]["projectFolder"]}/{project["dir"]}')

            DeletProj(project["id"])

            for i in reversed(range(self.verticalLayout.count())):
                self.verticalLayout.itemAt(i).widget().setParent(None)
            self.renderPorojects()

    def changeTheme(self):
        if GetProp("config", "*")[0]["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)

    def openSettings(self):
        self.second_form = Settings()
        self.second_form.show()

    def openInCode(self):
        projectname = self.sender().text().split(":")[1].strip()
        project = GetProject(projectname)[0]
        print(project)
        os.system(f'cmd /c "code {GetProp("config", "projectFolder")[0]["projectFolder"]}/{project["dir"]}"')

    def openProjectCreateScreen(self):
        self.second_form = ProjectCreate()
        self.second_form.show()


class Settings(QMainWindow):
    def __init__(self):
        super().__init__()
        global light_theme
        global dark_theme
        global UpdateConfig
        global TemplateCreate

        if GetProp("config", "*")[0]["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)
        uic.loadUi("settings.ui", self)

        self.projectDirChangeBtn.clicked.connect(self.changeDir)
        self.templateCreateBtn.clicked.connect(self.createTemplate)
        self.changeThemeBtn.clicked.connect(self.changeTheme)

    def changeTheme(self):

        if GetProp("config", "*")[0]["theme"] == "dark":
            UpdateConfig("theme", "light")
        else:
            UpdateConfig("theme", "dark")

        if GetProp("config", "*")[0]["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)

    def createTemplate(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Выбери файлы для шаблона', '/',
                                                "All Files (*);;Text Files (*.txt)")
        if len(files) == 0:
            return

        template = {"filling": []}
        for file in files:
            filetemp = {"fileName": file.split("/")[-1]}
            with open(file, 'r') as f:
                filetemp["content"] = f.read()
            template["filling"].append(filetemp)

        name, done = QtWidgets.QInputDialog.getText(
            self, 'Новый шаблон', 'Введи название шаблона')
        if done and name:
            template["name"] = name

            print(template)

            TemplateCreate(template)

    def changeDir(self):
        src_folder = GetProp("config", "projectFolder")[0]["projectFolder"]
        dest_folder = str(QFileDialog.getExistingDirectory(self, "Выбери новую папку для проектов"))

        items = os.listdir(src_folder)
        for item in items:
            src_path = os.path.join(src_folder, item)
            dest_path = os.path.join(dest_folder, item)
            shutil.move(src_path, dest_path)

        UpdateConfig("projectFolder", dest_folder)


class ProjectCreate(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        global GetProp
        global GetAllTags
        global AddTag
        global CreateProject
        self.changeTheme()
        uic.loadUi("projectCreate.ui", self)

        # переменые в которых хранятся тэг и шаблон
        self.template = None
        self.tag = None

        self.addTagButton.clicked.connect(self.addTag)

        self.templateRadioBtns = []
        # проходим по каждому шаблону в файле конфигурации
        for el in GetProp("Templates", "*"):
            # добовляем radio button в список со всеми raio button
            self.templateRadioBtns.append(QRadioButton(el["name"]))
            self.templateRadioBtns[-1].clicked.connect(self.setTemplate)
            self.templateLayout.addWidget(self.templateRadioBtns[-1])

        self.tagRadioBtns = []
        for el in GetAllTags():
            self.tagRadioBtns.append(QRadioButton(el))
            self.tagRadioBtns[-1].clicked.connect(self.setTag)
            self.tagLayout.addWidget(self.tagRadioBtns[-1])

        self.ProjectCreateBtn.clicked.connect(self.createProject)

    def changeTheme(self):
        if GetProp("config", "*")[0]["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)

    def addTag(self):
        name, done = QtWidgets.QInputDialog.getText(
            self, 'Новый тэг', 'Введи название тэга')
        if (done):
            AddTag(name)
            self.tagRadioBtns.append(QRadioButton(name))
            self.tagRadioBtns[-1].clicked.connect(self.setTag)
            self.tagLayout.addWidget(self.tagRadioBtns[-1])

    def setTag(self):
        self.tag = self.sender().text()

    # Задает шаблон который используется
    def setTemplate(self):
        self.template = self.sender().text()

    def createProject(self):
        print(self.projectName.text())
        formatedpname = self.projectName.text().lower().replace(' ', '_')
        currfolder = f'{GetProp("config", "projectFolder")[0]["projectFolder"]}/{formatedpname}'
        newproject = {
            "name": self.projectName.text(),
            "dir": formatedpname,
            "tag": self.tag
        }

        CreateProject(newproject)
        os.mkdir(currfolder)

        if (self.template):
            template = GetTemplate(self.template)
            template["filling"] = eval(template["filling"])
            for el in template["filling"]:
                with open(f'{currfolder}/{el["fileName"]}', 'x') as f:
                    f.write(el["content"])
        os.system(f'cmd /c "code {currfolder}')

        sys.exit(app.exec())


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook

    print(GetProp("config", "projectFolder")[0]["projectFolder"])
    if (GetProp("config", "projectFolder")[0]["projectFolder"] != ''):
        ex = MainScreen()
    else:
        ex = FirstSetup()
    ex.show()
    sys.exit(app.exec())
