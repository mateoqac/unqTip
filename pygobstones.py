#!/usr/bin/python
import subprocess
import sys
import os
import platform
from commons.utils import root_path

cmd = 'python commons/get-pip.py'
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
out, err = p.communicate() 
result = out.split('\n')
for lin in result:
    if not lin.startswith('#'):
        print(lin)


from PyQt4 import QtGui, QtCore
from gui.mainWindow import *
from time import time, sleep
from PyQt4.QtGui import QApplication, QSplashScreen, QPixmap
from PyQt4.QtCore import QSize
from PyQt4.QtSvg import QSvgWidget
import pip


def main():
    
        #instalo pip si la version de python es 2.7
    if sys.version[:3]=='2.7':
        variables= {}
        execfile('commons/get-pip.py',variables)
        print 'Installed pip'
    #Instalo la libreria para poder utilizar Google Drive    
    pip.main(['install', 'PyDrive'])
    print 'Installed PyDrive'
    app = QtGui.QApplication(sys.argv)

    #Get the locale settings
    locale = unicode(QtCore.QLocale.system().name())

    # This is to make Qt use locale configuration; i.e. Standard Buttons
    # in your system's language.
    qtTranslator=QtCore.QTranslator()
    qtTranslator.load("qt_" + locale,
                        QtCore.QLibraryInfo.location(
                        QtCore.QLibraryInfo.TranslationsPath)
                        )
    app.installTranslator(qtTranslator)

    path = os.path.join(root_path(), 'commons')
    

    #Install pip if python version is 2.7
      
    pip.main(['install', 'PyDrive'])
    print 'Installed PyDrive'
   

    f = QtGui.QFontDatabase.addApplicationFont(os.path.join(path, 'ubuntu.ttf'))
    font = QtGui.QFont('Ubuntu Titling')
    font.setBold(True)
    font.setPixelSize(16)
    app.setFont(font)

    start = time()
    
    if 'huayra' in platform.uname():
        img = QPixmap(os.path.join(path, 'gobstones_huayra.png'))
    else:
        img = QPixmap(os.path.join(path, 'gobstones.png'))

    splash = QSplashScreen(img)
    splash.show()

    while time() - start < 1:
        app.processEvents()
    
    w = MainWindow()
    icon = QtGui.QIcon(os.path.join(path, 'logo.png'))
    w.setWindowIcon(icon)
    splash.finish(w)
    w.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
