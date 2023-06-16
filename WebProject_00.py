from flask import Flask, request, render_template
import RPi.GPIO as GPIO
import threading
import time

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

# 음정 변수 셋업 (출처 : https://www.arduino.cc/en/Tutorial/Tone)
NOTE_C4  = 262; NOTE_CS4 = 277; NOTE_D4  = 294; NOTE_DS4 = 311; NOTE_E4  = 330; NOTE_F4  = 349; NOTE_FS4 = 370;
NOTE_G4  = 392; NOTE_GS4 = 415; NOTE_A4  = 440; NOTE_AS4 = 466; NOTE_B4  = 494; NOTE_C5  = 523

# Buzzer PWM 변수 셋업
bz = GPIO.PWM(BUZZ, 100)
Frq = [ 2000, 2400 ]
DDD = [ NOTE_G4, NOTE_G4, NOTE_A4, NOTE_A4, NOTE_G4, NOTE_G4, NOTE_E4, NOTE_E4, NOTE_G4, NOTE_G4, NOTE_E4, NOTE_E4, NOTE_D4,
			  NOTE_D4, NOTE_D4,	NOTE_G4, NOTE_G4, NOTE_A4, NOTE_A4, NOTE_G4, NOTE_G4, NOTE_E4, NOTE_E4, NOTE_G4, NOTE_E4, NOTE_D4,
			  NOTE_E4, NOTE_C4, NOTE_C4, NOTE_C4 ]
speed = 0.5

# 메인화면 출력
@app.route("/")
def home():
	return render_template("WebProject_00.html")

# 3색 LED route 함수 설정
@app.route("/led/red")
def led_red():
	try:
		GPIO.output(RED, GPIO.HIGH)
		return "ok"
	except expression as identifier:
		return "fail"

@app.route("/led/green")
def led_green():
	try:
		GPIO.output(GRN, GPIO.HIGH)
		return "ok"
	except expression as identifier:
		return "fail"

@app.route("/led/blue")
def led_blue():
	try:
		GPIO.output(BLU, GPIO.HIGH)
		return "ok"
	except expression as identifier:
		return "fail"

@app.route("/led/onlyred")
def led_onlyred():
	try:
		GPIO.output(RED, GPIO.HIGH)
		GPIO.output(GRN, GPIO.LOW)
		GPIO.output(BLU, GPIO.LOW)
		return "ok"
	except expression as identifier:
		return "fail"

@app.route("/led/onlygreen")
def led_onlygreen():
	try:
		GPIO.output(RED, GPIO.LOW)
		GPIO.output(GRN, GPIO.HIGH)
		GPIO.output(BLU, GPIO.LOW)
		return "ok"
	except expression as identifier:
		return "fail"

@app.route("/led/onlyblue")
def led_onlyblue():
	try:
		GPIO.output(RED, GPIO.LOW)
		GPIO.output(GRN, GPIO.LOW)
		GPIO.output(BLU, GPIO.HIGH)
		return "ok"
	except expression as identifier:
		return "fail"

@app.route("/led/all")
def led_all():
	try:
		GPIO.output(RED, GPIO.HIGH)
		GPIO.output(GRN, GPIO.HIGH)
		GPIO.output(BLU, GPIO.HIGH)
		return "ok"
	except expression as identifier:
		return "fail"

@app.route("/led/off")
def led_off():
	try:
		GPIO.output(RED, GPIO.LOW)
		GPIO.output(GRN, GPIO.LOW)
		GPIO.output(BLU, GPIO.LOW)
		return "ok"
	except expression as identifier:
		return "fail"

# ultrasonic 함수 설정
@app.route("/ultra/on")
def ultra_on():
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
			print("Distance : %.1f cm" % distance)
			# 웹페이지 상에 출력 로직 미구현
			if distance < 30:
				bz.start(10)
			else:
				bz.stop()
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
	return "ok"

@app.route("/ultra/off")
def ultra_off():
	global bzFlag
	bzFlag = 0
	GPIO.output(TRIG, False)
	GPIO.output(BUZZ, False)
	return "ok"

# Buzzer 함수 설정
@app.route("/buzz/on")
def buzz_on():
	def Buzz_Thread():
		global bzFlag
		bzFlag = 11
		GPIO.output(BUZZ, True)

		while bzFlag == 11:
			bz.start(10)
			for fr in Frq:
				bz.ChangeFrequency(fr)
				time.sleep(speed)
	threading.Thread(target=Buzz_Thread).start()
	return "ok"

@app.route("/buzz/school")
def buzz_school():
	def School_Thread():
		global bzFlag
		bzFlag = 12
		GPIO.output(BUZZ, True)

		while bzFlag == 12:
			bz.start(10)
			for fr in DDD:
				bz.ChangeFrequency(fr)
				time.sleep(speed)
	threading.Thread(target=School_Thread).start()
	return "sk"

@app.route("/buzz/off")
def buzz_off():
	try:
		global bzFlag
		bzFlag = 0
		GPIO.output(BUZZ, False)
		bz.stop()
		return "ok"
	except expression as identifier:
		return "fail"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="12000")
