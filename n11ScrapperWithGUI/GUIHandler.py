import sys
from time import sleep
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog,QApplication,QMessageBox,QDesktopWidget
from N11Scrapper import scrapper
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal,Qt
from PyQt5.QtGui import QImage,QPixmap
import requests
import os

class EntryScreen(QDialog):
    
    def __init__(self):
        super(EntryScreen,self).__init__()
        handleWidget(400,400)   
        loadUi("entryScreen.ui",self)
        self.startScrappingButton.clicked.connect(self.handleScrapOnPress)
        
    def handleScrapOnPress(self):
        try:
            if int(self.pageCountInputField.text())>50:
                raise Exception
            self.newScrapper=scrapper(self.categoryInputField.text(),int(self.pageCountInputField.text()))
            self.loadLoadingScreen()

        except:
            self.resetPage()
            messageBox=QMessageBox()
            messageBox.setWindowTitle("Error")
            messageBox.setText("There is a problem with your input!.Please try again.")
            messageBox.setIcon(QMessageBox.Critical)
            x=messageBox.exec_()   

    def resetPage(self):
        self.categoryInputField.setText("")
        self.pageCountInputField.setText("")

    def loadLoadingScreen(self):
        self.loadingScreen=LoadingScreen(self.newScrapper)
        widget.addWidget(self.loadingScreen)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
class LoadingScreen(QDialog):
    progressChanged=pyqtSignal(int)

    def __init__(self,scrapperObject):
        super(LoadingScreen,self).__init__()
        handleWidget(200,200)
        loadUi("loadingScreen.ui",self)
        self.progressChanged.connect(self.handleProcessBar)
        self.scrapperObject=scrapperObject
        self.ft=QThreadPool()
        worker=Worker(self.handleScrapping)
        self.ft.start(worker)
        
    def handleScrapping(self):
        self.scrapperObject.getAndWriteData(self)  

    def handleProcessBar(self,value):
        self.progressBar.setValue(value)
        if(value==100):
            sleep(0.5)
            self.loadMainScreen()

    def handleWorker(self):
        self.ft=QThreadPool()
        self.worker=Worker(self.handleScrapping)
        self.ft.start(self.worker)

    def loadMainScreen(self):
        self.mainScreen=MainScreen(self.scrapperObject)
        widget.addWidget(self.mainScreen)
        widget.setCurrentIndex(widget.currentIndex()+1) 

class ErrorPopup(QDialog):

    def __init__(self,parent=None):
        super(ErrorPopup,self).__init__(parent)
        self.messageBox=QMessageBox(parent)
        self.messageBox.setWindowTitle("Error")
        self.messageBox.setText("There is a problem with your input!.Please try again.")
        self.messageBox.setIcon(QMessageBox.Critical)
        
    def showw(self):
        self.messageBox.show()

class MainScreen(QDialog):

    def __init__(self,scrapperObj):
        super(MainScreen,self).__init__()
        self.createFile()
        handleWidget(800,600)  
        self.linkTemplate="<html><head/><body><p><a href='{0}'><span style=' text-decoration: underline; color:#f1c40f;'>Click to see this product in n11!</span></a></p></body></html>" 
        loadUi("mainScreen.ui",self)
        self.showPreviousButton.setFocusPolicy(Qt.NoFocus)
        self.showNextButton.setFocusPolicy(Qt.NoFocus)
        self.saveButton.setFocusPolicy(Qt.NoFocus)
        self.showPreviousButton.clicked.connect(self.showPreviousProduct)
        self.showNextButton.clicked.connect(self.showNextProduct)
        self.saveButton.clicked.connect(self.saveCurrentProduct)
        self.productImageVar=QImage()
        self.currentIndex=0
        self.isFirstDataWritten=False
        self.scrapperObj=scrapperObj
        self.wholedata=scrapperObj.wholedata
        self.parse()
        
    def parse(self):
        self.parsed=self.wholedata[self.currentIndex].split('|')
        self.productBrand.setText(self.parsed[0])
        self.productFullName.setText(self.parsed[1])
        self.productPrice.setText(self.parsed[2])
        self.productRating.setText(self.parsed[3])
        self.productRatingCount.setText(self.parsed[4])
        self.category.setText(self.scrapperObj.getCategory())
        self.storeName.setText(self.parsed[5])
        self.storeRating.setText(self.parsed[6])
        self.totalProduct.setText(str(len(self.wholedata)))
        self.productUrl.setText(self.linkTemplate.format(self.parsed[7]))    
        self.assignImage()

    def showNextProduct(self):
        self.currentIndex+=1
        if self.currentIndex==len(self.wholedata):
            self.currentIndex=0
        self.parse()  

    def showPreviousProduct(self):
        self.currentIndex-=1
        if self.currentIndex==-1:
            self.currentIndex=len(self.wholedata)
        self.parse()

    def assignImage(self):
        self.productImageVar.loadFromData(requests.get(self.parsed[8]).content)
        pixmap = QPixmap(self.productImageVar) 
        self.productImage.setPixmap(pixmap)

    def createFile(self):
        self.dataFile= open("savedProducts.txt", "a", encoding="utf-8")

    def saveCurrentProduct(self):
        separator='|'
        writeMe=""
        try:
            if(not self.isFirstDataWritten):
                if os.path.getsize("savedProducts.txt")!=0:
                    self.dataFile.write("\n")
                writeMe=self.parsed[0] + separator + self.parsed[1] + separator + self.parsed[2] + separator + self.parsed[3] + separator + self.parsed[4] + separator + self.parsed[5] + separator + self.parsed[6]
                self.isFirstDataWritten=True
            else:
                writeMe="\n" + self.parsed[0] + separator + self.parsed[1] + separator + self.parsed[2] + separator + self.parsed[3] + separator + self.parsed[4] + separator + self.parsed[5] + separator + self.parsed[6]
            self.dataFile.write(writeMe)
            self.dataFile.write("\nProduct Url:" + self.parsed[7])
            messageBox=QMessageBox()
            messageBox.setWindowTitle("Product Saved")
            messageBox.setText("Product has been successfully saved!")
            messageBox.setIcon(QMessageBox.Information)
            x=messageBox.exec_()  
        except:
            messageBox=QMessageBox()
            messageBox.setWindowTitle("Error")
            messageBox.setText("There is a problem in file writing!.Please try again.")
            messageBox.setIcon(QMessageBox.Critical)
            x=messageBox.exec_()       

class Worker(QRunnable):

    def __init__(self,function,*args,**kwargs):
        super(Worker, self).__init__()
        self.function=function
        self.args=args
        self.kwargs=kwargs

    def run(self):
        self.function(*self.args,**self.kwargs)    

    
def handleWidget(width,height):
    widget.setFixedSize(width,height)
    qtRectangle = widget.frameGeometry()
    centerPoint = QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    widget.move(qtRectangle.topLeft())

app=QApplication(sys.argv)
widget=QtWidgets.QStackedWidget()
widget.setWindowTitle("n11 Scrapper")
handleWidget(400,400)
welcome=EntryScreen()
widget.addWidget(welcome)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")       