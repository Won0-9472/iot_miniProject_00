from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from flask import Flask, request, render_template
import RPi.GPIO as GPIO
import threading
import time
import sys

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED핀 변수선언
RED = 18
GRN = 15
BLU = 14

# Ultrasonic핀 변수선언
ECHO = 2
TRIG = 3

# Buzzer핀 변수선언
BUZZ = 4
btnON = 23
btnOFF = 17
bzFlag = 0

# LED GPIO 셋업
GPIO.setup(RED, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(GRN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BLU, GPIO.OUT, initial=GPIO.LOW)

# Ultrasonic GPIO 셋업
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(BUZZ, GPIO.OUT)

# Ultrasonic GPIO 초기화
GPIO.output(TRIG, False)
GPIO.output(BUZZ, False)

# 음정 변수 셋업
NOTE_C4  = 262; NOTE_CS4 = 277; NOTE_D4  = 294; NOTE_DS4 = 311; NOTE_E4  = 330; NOTE_F4  = 349; NOTE_FS4 = 370;
NOTE_G4  = 392; NOTE_GS4 = 415; NOTE_A4  = 440; NOTE_AS4 = 466; NOTE_B4  = 494; NOTE_C5  = 523

# Buzzer PWM 변수 셋업
bz = GPIO.PWM(BUZZ, 100)
Frq = [ 2000, 2400, ]
DDD = [ NOTE_G4, NOTE_G4, NOTE_A4, NOTE_A4, NOTE_G4, NOTE_G4, NOTE_E4, NOTE_E4, NOTE_G4, NOTE_G4, NOTE_E4, NOTE_E4, NOTE_D4,
			  NOTE_D4, NOTE_D4,	NOTE_G4, NOTE_G4, NOTE_A4, NOTE_A4, NOTE_G4, NOTE_G4, NOTE_E4, NOTE_E4, NOTE_G4, NOTE_E4, NOTE_D4,
			  NOTE_E4, NOTE_C4, NOTE_C4, NOTE_C4 ]
speed = 0.5

# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("PyQtProject_00.ui")[0]

# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.setFixedSize(QSize(1200, 800)) # 창 크기 조절 비활성화

		# 버튼에 LED 관련 기능을 연결하는 코드
		self.btnRed.clicked.connect(self.btnRedFunction)
		self.btnGreen.clicked.connect(self.btnGreenFunction)
		self.btnBlue.clicked.connect(self.btnBlueFunction)
		self.btnRedOnly.clicked.connect(self.btnRedOnlyFunction)
		self.btnGreenOnly.clicked.connect(self.btnGreenOnlyFunction)
		self.btnBlueOnly.clicked.connect(self.btnBlueOnlyFunction)
		self.btnLEDon.clicked.connect(self.btnLEDonFunction)
		self.btnLEDoff.clicked.connect(self.btnLEDoffFunction)

		# 버튼에 Ultrasonic 관련 기능을 연결하는 코드
		self.btnUltraOn.clicked.connect(self.btnUltraOnFunction)
		self.btnUltraOff.clicked.connect(self.btnUltraOffFunction)

		# 버튼에 Buzzer 관련 기능을 연결하는 코드
		self.btnBuzzOn.clicked.connect(self.btnBuzzOnFunction)
		self.btnBuzzSchool.clicked.connect(self.btnBuzzSchoolFunction)
		self.btnBuzzOff.clicked.connect(self.btnBuzzOffFunction)

		# 버튼에 마우스를 갖다대면 기능을 설명하는 setToolTip 메서드 설정
		self.btnRed.setToolTip(       "빨간색 LED를 추가로 켭니다.")
		self.btnGreen.setToolTip(     "초록색 LED를 추가로 켭니다.")
		self.btnBlue.setToolTip(      "파란색 LED를 추가로 켭니다.")
		self.btnRedOnly.setToolTip(   "빨간색 LED만 켜고 나머지는 끕니다.")
		self.btnGreenOnly.setToolTip( "초록색 LED만 켜고 나머지는 끕니다.")
		self.btnBlueOnly.setToolTip(  "파란색 LED만 켜고 나머지는 끕니다.")
		self.btnLEDon.setToolTip(     "모든 LED를 켭니다.")
		self.btnLEDoff.setToolTip(    "모든 LED를 끕니다.")
		self.btnUltraOn.setToolTip(   "거리측정을 위해 초음파 센서를 켭니다.")
		self.btnUltraOff.setToolTip(  "초음파 센서를 끕니다.")
		self.btnBuzzOn.setToolTip(    "피에조 부저를 켭니다.")
		self.btnBuzzSchool.setToolTip("'학교종이 땡땡땡' 노래를 재생합니다.")
		self.btnBuzzOff.setToolTip(   "피에조 부저를 끕니다.")

	# 페페 이미지 불러오기 함수 (같은 폴더 내에 있는 이미지를 불러옴)
		self.initImage()
	def initImage(self):
		self.picPEPE = QLabel(self)
		self.picPEPE.resize(620, 470)
		self.picPEPE.move(360, 340)
		pixmap = QPixmap("PEPE.png")
		self.picPEPE.setPixmap(QPixmap(pixmap))

		self.show()

	# LED 버튼 함수 설정
	def btnRedFunction(self):
		try:
			self.label_Display.setText("RED LED ON")
			GPIO.output(RED, GPIO.HIGH)
		except:
			self.label_Display.setText("ERROR")
			GPIO.cleanup()

	def btnGreenFunction(self):
		try:
			self.label_Display.setText("GREEN LED ON")
			GPIO.output(GRN, GPIO.HIGH)
		except:
			self.label_Display.setText("ERROR")
			GPIO.cleanup()

	def btnBlueFunction(self):
		try:
			self.label_Display.setText("BLUE LED ON")
			GPIO.output(BLU, GPIO.HIGH)
		except:
			self.label_Display.setText("ERROR")
			GPIO.cleanup()

	def btnRedOnlyFunction(self):
		try:
			self.label_Display.setText("RED LED ONLY")
			GPIO.output(RED, GPIO.HIGH)
			GPIO.output(GRN, GPIO.LOW)
			GPIO.output(BLU, GPIO.LOW)
		except:
			self.label_Display.setText("ERROR")
			GPIO.cleanup()

	def btnGreenOnlyFunction(self):
		try:
			self.label_Display.setText("GREEN LED ONLY")
			GPIO.output(RED, GPIO.LOW)
			GPIO.output(GRN, GPIO.HIGH)
			GPIO.output(BLU, GPIO.LOW)
		except:
			self.label_Display.setText("ERROR")
			GPIO.cleanup()

	def btnBlueOnlyFunction(self):
		try:
			self.label_Display.setText("BLUE LED ONLY")
			GPIO.output(RED, GPIO.LOW)
			GPIO.output(GRN, GPIO.LOW)
			GPIO.output(BLU, GPIO.HIGH)
		except:
			self.label.Display.setText("ERROR")
			GPIO.cleanup()

	def btnLEDonFunction(self):
		try:
			self.label_Display.setText("ALL LED ON")
			GPIO.output(RED, GPIO.HIGH)
			GPIO.output(GRN, GPIO.HIGH)
			GPIO.output(BLU, GPIO.HIGH)
		except:
			self.label_Display.setText("ERROR")
			GPIO.cleanup()

	def btnLEDoffFunction(self):
		try:
			self.label_Display.setText("LED OFF")
			GPIO.output(RED, GPIO.LOW)
			GPIO.output(GRN, GPIO.LOW)
			GPIO.output(BLU, GPIO.LOW)
		except:
			self.label_Display.setText("ERROR")
			GPIO.cleanup()

	# Ultrasonic 버튼 함수 설정
	def btnUltraOnFunction(self):
		self.label_Display.setText("ULTRASONIC ON")
		def Ultra_Thread():
			global bzFlag
			bzFlag = 1
			while bzFlag == 1:
				GPIO.output(BUZZ, False)
				GPIO.output(TRIG, True)
				time.sleep(0.00001)
				GPIO.output(TRIG, False)
				bz.ChangeFrequency(1000)
				while GPIO.input(ECHO) == 0:
					start = time.time()
				while GPIO.input(ECHO) == 1:
					stop = time.time()
				check_time = stop - start
				distance = check_time * 34300 / 2
				self.label_Display.setText("Distance : %.1f cm" % distance)

				if distance < 30:
					bz.start(10)
				else:
					bz.stop(10)
				if distance < 5:
					bz.ChangeDutyCycle(99)
					bz.ChangeFrequency(2000)
					GPIO.output(BUZZ, True)
					time.sleep(2)
				elif distance < 10:
					bz.ChangeDutyCycle(10)
					bz.ChangeFrequency(2000)
					GPIO.output(BUZZ, True)
					time.sleep(0.2)
				elif distance < 15:
					bz.ChangeDutyCycle(10)
					bz.ChangeFrequency(700)
					GPIO.output(BUZZ, True)
					time.sleep(0.2)
				elif distance < 20:
					bz.ChangeDutyCycle(10)
					bz.ChangeFrequency(500)
					GPIO.output(BUZZ, True)
					time.sleep(0.2)
				elif distance < 25:
					bz.ChangeDutyCycle(10)
					bz.ChangeFrequency(10)
					GPIO.output(BUZZ, True)
					time.sleep(0.5)
				elif distance < 30:
					bz.ChangeDutyCycle(10)
					bz.ChangeFrequency(10)
					GPIO.output(BUZZ, True)
					time.sleep(1)
				else:
					time.sleep(0.4)
				bz.stop()
		threading.Thread(target=Ultra_Thread).start()

	def btnUltraOffFunction(self):
		self.label_Display.setText("ULTRASONIC OFF")
		global bzFlag
		bzFlag = 0
		GPIO.output(TRIG, False)
		GPIO.output(BUZZ, False)

	# Buzzer 버튼 함수 설정
	def btnBuzzOnFunction(self):
		self.label_Display.setText("BUZZER ON")
		def Buzz_Thread():
			global bzFlag
			global Frq
			bzFlag = 11
			GPIO.output(BUZZ, True)
			while bzFlag == 11:
				bz.start(10)
				for fr in Frq:
					bz.ChangeFrequency(fr)
					time.sleep(speed)
				time.sleep(0.5)
		threading.Thread(target=Buzz_Thread).start()

	def btnBuzzSchoolFunction(self):
		self.label_Display.setText("학교종이 땡땡땡")
		def School_Thread():
			global bzFlag
			global DDD
			bzFlag = 12
			GPIO.output(BUZZ, True)
			while bzFlag == 12:
				bz.start(10)
				for fr in DDD:
					bz.ChangeFrequency(fr)
					time.sleep(speed)
		threading.Thread(target=School_Thread).start()

	def btnBuzzOffFunction(self):
		try:
			self.label_Display.setText("BUZZER OFF")
			global bzFlag
			bzFlag = 0
			GPIO.output(BUZZ, False)
			bz.stop()
		except expression as identifier:
			self.label_Display.setText("ERROR")
			bz.stop()
			GPIO.cleanup()

# 예외처리 : 프로그램이 종료될 때 실행할 clean_up() 함수
def clean_up():
	global bzFlag
	bzFlag = 0
	GPIO.cleanup()

if __name__ == "__main__":
	app = QApplication([])
	myWindow = WindowClass()
	app.aboutToQuit.connect(clean_up)
	myWindow.show()
	sys.exit(app.exec_())
