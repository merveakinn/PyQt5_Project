from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from time import sleep
import sys
import os
from configparser import ConfigParser
import subprocess

class ProcessThread(QThread):
    isRunning = False
    send_error = pyqtSignal([str])
    
    def __init__(self, app):
        super(ProcessThread, self).__init__()
        self.app = app

    def run(self):
        while 1:
            if self.isRunning:
                save = ConfigParser()
                if os.path.exists(f"C:\\Users\\{os.getlogin()}\\Desktop\\PyQt5_Project\\save.ini"): save.read(f"C:\\Users\\{os.getlogin()}\\Desktop\\PyQt5_Project\\save.ini")

                machine = self.app.machineCombo.currentText().lower()

                xChecked = self.app.XcheckBox.isChecked()
                yChecked = self.app.YcheckBox.isChecked()
                zChecked = self.app.ZcheckBox.isChecked()
                bltchChecked = self.app.BLTOUCHcheckBox.isChecked() 
                runoutsensorChecked = self.app.RUNOUT_SENSORcheckBox.isChecked()
                encoderChecked = self.app.ENCODERcheckBox.isChecked()
                X_HOMEChecked = self.app.X_HOMEcheckBox.isChecked()
                Y_HOMEChecked = self.app.Y_HOMEcheckBox.isChecked()
                Z_HOMEChecked = self.app.Z_HOMEcheckBox.isChecked()

                h = "Configuration.h"
                file = f"C:\\Users\\{os.getlogin()}\\Desktop\\PyQt5_Project\\{h}"

                try:
                    with open(file, "r") as f: old = f.read()
                    new = old.replace(f"#define BLTOUCH" , f"//#define BLTOUCH")
                    new = old.replace(f"#define FILAMENT_RUNOUT_SENSOR" , f"//#define FILAMENT_RUNOUT_SENSOR")
                    new = old.replace(f"#define REVERSE_ENCODER_DIRECTION" , f"//#define REVERSE_ENCODER_DIRECTION")

                    new = old.replace(f"INVERT_X_DIR {str(not xChecked).lower()}", f"INVERT_X_DIR {str(xChecked).lower()}")
                    new = new.replace(f"INVERT_Y_DIR {str(not yChecked).lower()}", f"INVERT_Y_DIR {str(yChecked).lower()}")
                    new = new.replace(f"INVERT_Z_DIR {str(not zChecked).lower()}", f"INVERT_Z_DIR {str(zChecked).lower()}")

                    new = new.replace("//#define BLTOUCH", "#define BLTOUCH").replace("#define BLTOUCH", f"{'' if bltchChecked else '//'}#define BLTOUCH")
                    new = new.replace("//#define FILAMENT_RUNOUT_SENSOR", "#define FILAMENT_RUNOUT_SENSOR").replace("#define FILAMENT_RUNOUT_SENSOR", f"{'' if runoutsensorChecked else '//'}#define FILAMENT_RUNOUT_SENSOR")
                    new = new.replace("//#define REVERSE_ENCODER_DIRECTION", "#define REVERSE_ENCODER_DIRECTION").replace("#define REVERSE_ENCODER_DIRECTION", f"{'' if encoderChecked else '//'}#define REVERSE_ENCODER_DIRECTION")                    

                    new = new.replace("#define X_HOME_DIR 1", "#define X_HOME_DIR -1").replace("#define X_HOME_DIR -1", f"{'#define X_HOME_DIR 1' if X_HOMEChecked else '#define X_HOME_DIR -1'}")
                    new = new.replace("#define Y_HOME_DIR 1", "#define Y_HOME_DIR -1").replace("#define Y_HOME_DIR -1", f"{'#define Y_HOME_DIR 1' if Y_HOMEChecked else '#define Y_HOME_DIR -1'}")
                    new = new.replace("#define Z_HOME_DIR 1", "#define Z_HOME_DIR -1").replace("#define Z_HOME_DIR -1", f"{'#define Z_HOME_DIR 1' if Z_HOMEChecked else '#define Z_HOME_DIR -1'}")

                    with open(file, "w") as f: f.write(new)
                except Exception as e: 
                    self.send_error.emit(str(e))

                save[machine] = {
                    "invertxdir": xChecked,
                    "invertydir": yChecked,
                    "invertzdir": zChecked,
                    "disablebltouch": bltchChecked,
                    "runoutsensor": runoutsensorChecked,
                    "encoder": encoderChecked,
                    "xhome": X_HOMEChecked,
                    "yhome": Y_HOMEChecked,
                    "zhome": Z_HOMEChecked
                }
                try:
                    with open("save.ini", "w") as f: save.write(f)
                except UnicodeEncodeError:
                    self.send_error.emit("Machine Name contains unicode characters.")

                self.app.runBtn.setText("Run")
                self.app.XcheckBox.setEnabled(True)
                self.app.YcheckBox.setEnabled(True)
                self.app.ZcheckBox.setEnabled(True)
                self.app.runBtn.setEnabled(True)
                self.app.BLTOUCHcheckBox.setEnabled(True)
                self.app.RUNOUT_SENSORcheckBox.setEnabled(True)
                self.app.ENCODERcheckBox.setEnabled(True)
                self.app.X_HOMEcheckBox.setEnabled(True)
                self.app.Y_HOMEcheckBox.setEnabled(True)
                self.app.Z_HOMEcheckBox.setEnabled(True)

                self.isRunning = False
            sleep(0.5)
        
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.title = "DENEME"
        self.setWindowTitle(self.title)
        self.setFixedSize(350, 250)

        with open(f"C:\\Users\\{os.getlogin()}\\Desktop\\PyQt5_Project\\machines.txt", "r") as f:
            self.machines = f.read().replace("\n","").replace(" ","").split(",")
            for i in self.machines: 
                if len(i) < 1: self.machines.remove(i)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        mainGrid = QGridLayout(self)

        self.machineBox = QGroupBox("Machine")
        self.machineBox.layout = QGridLayout()
        self.machineBox.setLayout(self.machineBox.layout)
        self.machineCombo = QComboBox()
        self.machineCombo.addItems(self.machines)
        self.machineCombo.currentTextChanged.connect(lambda: self.get_save(self.machineCombo.currentText()))
        self.machineBox.layout.addWidget(self.machineCombo, 0, 0)
        mainGrid.addWidget(self.machineBox, 0, 0)

        self.settingsBox = QGroupBox("Settings")
        self.settingsBox.layout = QGridLayout()
        self.settingsBox.setLayout(self.settingsBox.layout)
        self.XcheckBox = QCheckBox("X DIR")
        self.XcheckBox.setLayoutDirection(Qt.RightToLeft)
        self.settingsBox.layout.addWidget(self.XcheckBox, 0, 0, Qt.AlignRight)
        self.YcheckBox = QCheckBox("Y DIR")
        self.YcheckBox.setLayoutDirection(Qt.RightToLeft)
        self.settingsBox.layout.addWidget(self.YcheckBox, 0, 1, Qt.AlignRight)
        self.ZcheckBox = QCheckBox("Z DIR")
        self.ZcheckBox.setLayoutDirection(Qt.RightToLeft)
        self.settingsBox.layout.addWidget(self.ZcheckBox, 0, 2, Qt.AlignRight)

        self.BLTOUCHcheckBox = QCheckBox("BLTOUCH") 
        self.BLTOUCHcheckBox.setLayoutDirection(Qt.RightToLeft) 
        self.settingsBox.layout.addWidget(self.BLTOUCHcheckBox, 1, 0, Qt.AlignRight)

        self.RUNOUT_SENSORcheckBox = QCheckBox("RUNOUT")
        self.RUNOUT_SENSORcheckBox.setLayoutDirection(Qt.RightToLeft)
        self.settingsBox.layout.addWidget(self.RUNOUT_SENSORcheckBox, 1, 1, Qt.AlignRight)

        self.ENCODERcheckBox = QCheckBox("ENCODER")
        self.ENCODERcheckBox.setLayoutDirection(Qt.RightToLeft)
        self.settingsBox.layout.addWidget(self.ENCODERcheckBox, 1, 2, Qt.AlignRight)

        self.X_HOMEcheckBox = QCheckBox("X HOME (max)")
        self.X_HOMEcheckBox.setLayoutDirection(Qt.RightToLeft)
        self.X_HOMEcheckBox.stateChanged.connect(self.xhomeChange)
        self.settingsBox.layout.addWidget(self.X_HOMEcheckBox, 2, 0, Qt.AlignRight)
        self.Y_HOMEcheckBox = QCheckBox("Y HOME (max)")
        self.Y_HOMEcheckBox.setLayoutDirection(Qt.RightToLeft)
        self.Y_HOMEcheckBox.stateChanged.connect(self.yhomeChange)
        self.settingsBox.layout.addWidget(self.Y_HOMEcheckBox, 2, 1, Qt.AlignRight)
        self.Z_HOMEcheckBox = QCheckBox("Z HOME (max)")
        self.Z_HOMEcheckBox.setLayoutDirection(Qt.RightToLeft)
        self.Z_HOMEcheckBox.stateChanged.connect(self.zhomeChange)
        self.settingsBox.layout.addWidget(self.Z_HOMEcheckBox, 2, 2, Qt.AlignRight)
        
        mainGrid.addWidget(self.settingsBox, 1, 0)

        self.processBox = QGroupBox("Process")
        self.processBox.layout = QGridLayout()
        self.processBox.setLayout(self.processBox.layout)
        self.runBtn = QPushButton(text="Run")
        self.runBtn.clicked.connect(self.toggle)
        
        self.processBox.layout.addWidget(self.runBtn, 1, 0)
        mainGrid.addWidget(self.processBox, 2, 0)

        self.procThread = ProcessThread(self)
        self.procThread.send_error.connect(self.on_error)
        self.procThread.start()
        self.get_save(self.machines[0])

    def xhomeChange(self):
        if "max" in self.X_HOMEcheckBox.text(): self.X_HOMEcheckBox.setText(self.X_HOMEcheckBox.text().replace("max", "min"))
        else: self.X_HOMEcheckBox.setText(self.X_HOMEcheckBox.text().replace("min", "max"))

    def yhomeChange(self):
        if "max" in self.Y_HOMEcheckBox.text(): self.Y_HOMEcheckBox.setText(self.Y_HOMEcheckBox.text().replace("max", "min"))
        else: self.Y_HOMEcheckBox.setText(self.Y_HOMEcheckBox.text().replace("min", "max"))

    def zhomeChange(self):
        if "max" in self.Z_HOMEcheckBox.text(): self.Z_HOMEcheckBox.setText(self.Z_HOMEcheckBox.text().replace("max", "min"))
        else: self.Z_HOMEcheckBox.setText(self.Z_HOMEcheckBox.text().replace("min", "max"))

    def get_save(self, name):
        with open(f"C:\\Users\\{os.getlogin()}\\Desktop\\PyQt5_Project\\current_machine.txt", "w") as f: f.write(name.lower())
        if os.path.exists(f"C:\\Users\\{os.getlogin()}\\Desktop\\PyQt5_Project\\save.ini"):
            save = ConfigParser()
            save.read(f"C:\\Users\\{os.getlogin()}\\Desktop\\PyQt5_Project\\save.ini")
            name = name.lower()

            try: 
                save[name]
                there = True
            except: there = False

            if there:
                self.XcheckBox.setChecked("true" in save[name]["invertxdir"].lower())
                self.YcheckBox.setChecked("true" in save[name]["invertydir"].lower())
                self.ZcheckBox.setChecked("true" in save[name]["invertzdir"].lower())
                self.BLTOUCHcheckBox.setChecked("true" in save[name]["disablebltouch"].lower())
                self.RUNOUT_SENSORcheckBox.setChecked("true" in save[name]["runoutsensor"].lower())
                self.ENCODERcheckBox.setChecked("true" in save[name]["encoder"].lower())
                self.X_HOMEcheckBox.setChecked("true" in save[name]["xhome"].lower())
                self.Y_HOMEcheckBox.setChecked("true" in save[name]["yhome"].lower())
                self.Z_HOMEcheckBox.setChecked("true" in save[name]["zhome"].lower())
            else:
                self.XcheckBox.setChecked(False)
                self.YcheckBox.setChecked(False)
                self.ZcheckBox.setChecked(False)
                self.BLTOUCHcheckBox.setChecked(False)
                self.RUNOUT_SENSORcheckBox.setChecked(False)
                self.ENCODERcheckBox.setChecked(False)
                self.X_HOMEcheckBox.setChecked(False)
                self.Y_HOMEcheckBox.setChecked(False)
                self.Z_HOMEcheckBox.setChecked(False)

            
            if name == "c1_sn221":
                self.setMachineUUID("c1_sn221")
            elif name == "c1_sn222":
                self.setMachineUUID("c1_sn222")
            elif name == "c1_sn223":
                self.setMachineUUID("c1_sn223")
            elif name == "c1_sn224":
                self.setMachineUUID("c1_sn224")
            elif name == "c1_sn225":
                self.setMachineUUID("c1_sn225")
            elif name == "c1_sn226":
                self.setMachineUUID("c1_sn226")
            elif name == "c1_sn227":
                self.setMachineUUID("c1_sn227")
            elif name == "c1_sn228":
                self.setMachineUUID("c1_sn228")
        
    def on_error(self, message="Test Message"): 
        QMessageBox.about(self, f"{self.title} Error", message)

    def toggle(self):
        if self.procThread.isRunning:
            self.runBtn.setText("Run")
            self.XcheckBox.setEnabled(True)
            self.YcheckBox.setEnabled(True)
            self.ZcheckBox.setEnabled(True)
            self.runBtn.setEnabled(True)
            self.BLTOUCHcheckBox.setEnabled(True)
            self.RUNOUT_SENSORcheckBox.setEnabled(True)
            self.ENCODERcheckBox.setEnabled(True)
            self.X_HOMEcheckBox.setEnabled(True)
            self.Y_HOMEcheckBox.setEnabled(True)
            self.Z_HOMEcheckBox.setEnabled(True)
        else: 
            self.runBtn.setText("Stop")
            self.XcheckBox.setEnabled(False)
            self.YcheckBox.setEnabled(False)
            self.ZcheckBox.setEnabled(False)
            self.runBtn.setEnabled(False)
            self.BLTOUCHcheckBox.setEnabled(False)
            self.RUNOUT_SENSORcheckBox.setEnabled(False)
            self.ENCODERcheckBox.setEnabled(False)
            self.X_HOMEcheckBox.setEnabled(False)
            self.Y_HOMEcheckBox.setEnabled(False)
            self.Z_HOMEcheckBox.setEnabled(False)

        bat = "executer.bat"
        try: subprocess.Popen([f"C:\\Users\\{os.getlogin()}\\Desktop\\PyQt5_Project\\{bat}"])
        except: self.on_error(f"Unable to find '{bat}' file.")

        self.procThread.isRunning = not self.procThread.isRunning

    def setMachineUUID(self, text):
        h = "Configuration.h"
        file = f"C:\\Users\\{os.getlogin()}\\Desktop\\PyQt5_Project\\{h}"
        with open(file, "r") as f: old = f.read()
        oldVal = old.split("#define MACHINE_UUID")[1].split('"')[1]
        new = old.replace(oldVal, text)
        with open(file, "w") as f: f.write(new)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(app.exec_())
