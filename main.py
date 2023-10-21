from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QRadioButton, QVBoxLayout, QGroupBox, \
    QMessageBox
from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5 import uic, QtWidgets, QtCore
import sys
import json
import os
import shutil



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
        global config
        global light_theme
        global dark_theme
        if config["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)

        uic.loadUi("config.ui", self)
        self.pushButton.clicked.connect(self.openFileDialog)

    def openFileDialog(self):
        config["projectsFolder"] = str(QFileDialog.getExistingDirectory(self, "Выбери папку для проектов"))

        with open("config.json", "w") as jsonFile:
            json.dump(config, jsonFile)
        if config["projectsFolder"] != "":
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
        global config
        global light_theme
        global dark_theme

        uic.loadUi("main.ui", self)
        self.createProjectBtn.clicked.connect(self.openProjectCreateScreen)
        self.settingButton.clicked.connect(self.openSettings)
        if config["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)

        self.renderPorojects()



    def checkIfProjectExsist(self):
        for el in config["projects"]:
            if not os.path.isdir(f'{config["projectsFolder"]}/{el["dir"]}'):
                config["projects"].remove(el)
        with open("config.json", "w") as jsonFile:
            json.dump(config, jsonFile)

    def renderPorojects(self):
        self.checkIfProjectExsist()
        for el in config["projects"]:
            
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
            projectobjindex = [el["name"] for el in config["projects"]].index(projectname)

            shutil.rmtree(f'{config["projectsFolder"]}/{config["projects"][projectobjindex]["dir"]}')
            del config["projects"][projectobjindex]

            for i in reversed(range(self.verticalLayout.count())):
                self.verticalLayout.itemAt(i).widget().setParent(None)
            self.renderPorojects()

            with open("config.json", "w") as jsonFile:
                json.dump(config, jsonFile)



    def changeTheme(self):
        if config["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)

    def openSettings(self):
        self.second_form = Settings()
        self.second_form.show()

    def openInCode(self):
        projectname = self.sender().text().split(":")[1].strip()
        projectobjindex = [el["name"] for el in config["projects"]].index(projectname)
        print(f'')
        os.system(f'cmd /c "code {config["projectsFolder"]}/{config["projects"][projectobjindex]["dir"]}"')

    def openProjectCreateScreen(self):
        self.second_form = ProjectCreate()
        self.second_form.show()


class Settings(QMainWindow):
    def __init__(self):
        super().__init__()
        global config
        global light_theme
        global dark_theme

        if config["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)
        uic.loadUi("settings.ui", self)

        self.projectDirChangeBtn.clicked.connect(self.changeDir)
        self.templateCreateBtn.clicked.connect(self.createTemplate)
        self.changeThemeBtn.clicked.connect(self.changeTheme)

    def changeTheme(self):
        if config["theme"] == "light":
            config["theme"] = "dark"
        else:
            config["theme"] = "light"
        if config["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)
        with open("config.json", "w") as jsonFile:
            json.dump(config, jsonFile)

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

            config["userTemplates"].append(template)
            print(template)
            with open("config.json", "w") as jsonFile:
                json.dump(config, jsonFile)

    def changeDir(self):
        src_folder = config["projectsFolder"]
        dest_folder = str(QFileDialog.getExistingDirectory(self, "Выбери новую папку для проектов"))

        items = os.listdir(src_folder)
        for item in items:
            src_path = os.path.join(src_folder, item)
            dest_path = os.path.join(dest_folder, item)
            shutil.move(src_path, dest_path)

        config["projectsFolder"] = dest_folder

        with open("config.json", "w") as jsonFile:
            json.dump(config, jsonFile)


class ProjectCreate(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        global config
        self.changeTheme()
        uic.loadUi("projectCreate.ui", self)

        # переменые в которых хранятся тэг и шаблон
        self.template = None
        self.tag = None

        self.addTagButton.clicked.connect(self.addTag)

        self.templateRadioBtns = []
        # проходим по каждому шаблону в файле конфигурации
        for el in config["userTemplates"]:
            # добовляем radio button в список со всеми raio button
            self.templateRadioBtns.append(QRadioButton(el["name"]))
            self.templateRadioBtns[-1].clicked.connect(self.setTemplate)
            self.templateLayout.addWidget(self.templateRadioBtns[-1])

        self.tagRadioBtns = []
        for el in config["tags"]:
            self.tagRadioBtns.append(QRadioButton(el))
            self.tagRadioBtns[-1].clicked.connect(self.setTag)
            self.tagLayout.addWidget(self.tagRadioBtns[-1])

        self.ProjectCreateBtn.clicked.connect(self.createProject)

    def changeTheme(self):
        if config["theme"] == "dark":
            self.setStyleSheet(dark_theme)
        else:
            self.setStyleSheet(light_theme)

    def addTag(self):
        name, done = QtWidgets.QInputDialog.getText(
            self, 'Новый тэг', 'Введи название тэга')
        if (done):
            config["tags"].append(name)
            with open("config.json", "w") as jsonFile:
                json.dump(config, jsonFile)
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
        currfolder = f'{config["projectsFolder"]}/{formatedpname}'
        newproject = {
            "name": self.projectName.text(),
            "dir": formatedpname,
            "tag": self.tag
        }
        config["projects"].append(newproject)

        os.mkdir(currfolder)
        if (self.template):
            templateindex = [el["name"] for el in config["userTemplates"]].index(self.template)
            if self.template:
                for el in config["userTemplates"][templateindex]["filling"]:
                    with open(f'{currfolder}/{el["fileName"]}', 'x') as f:
                        f.write(el["content"])
        os.system(f'cmd /c "code {currfolder}')
        with open("config.json", "w") as jsonFile:
            json.dump(config, jsonFile)
        sys.exit(app.exec())


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    config = json.load(open("config.json"))
    if (config["projectsFolder"] != ''):
        ex = MainScreen()
    else:
        ex = FirstSetup()
    ex.show()
    sys.exit(app.exec())
