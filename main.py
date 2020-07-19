# -*- coding:utf-8 -*-
import spidev as SPI
import ST7789
import RPi.GPIO as GPIO
import time
import os
import sys
import Queue
import sh
import time
import subprocess

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from time import sleep 

import threading
c = threading.Condition()

RST = 27
DC = 25
BL = 24
bus = 0 
device = 0 

KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16


ui = {
	"start_splash": False,
	
	"main_menu": 0,
	"main_menu_show": False,
	"main_menu_options": ["Jailbreak", "Power Off"]
}
disp_update = True
splash = False 		# Show splash on start

# Device variables
dev = {
	"mode": 0,
	"model": "Device",
	"ios": "",
	"udid": "",
	"ecid": "",
}

# Jailbreak variables
jb = {
	"running": False,
	"enable": False,
	"stage": 1,
	"status": ""
}

# Device Identifiers
dev_model = {
	# iPhone
	"iPhone6,1": "iPhone 5s",
	"iPhone6,2": "iPhone 5s",
	"iPhone7,1": "iPhone 6",
	"iPhone7,2": "iPhone 6 Plus",
	"iPhone8,1": "iPhone 6s",
	"iPhone8,2": "iPhone 6s Plus",
	"iPhone8,4": "iPhone SE",
	"iPhone9,1": "iPhone 7",
	"iPhone9,2": "iPhone 7 Plus",
	"iPhone9,3": "iPhone 7",
	"iPhone9,4": "iPhone 7 Plus",
	"iPhone10,1": "iPhone 8",
	"iPhone10,2": "iPhone 8 Plus",
	"iPhone10,3": "iPhone X",
	"iPhone10,4": "iPhone 8",
	"iPhone10,5": "iPhone 8 Plus",
	"iPhone10,6": "iPhone X",
	#iPad
	"iPad4,1": "iPad Air",
	"iPad4,2": "iPad Air",
	"iPad4,3": "iPad Air",
	"iPad4,4": "iPad Mini 2",
	"iPad4,5": "iPad Mini 2",
	"iPad4,6": "iPad Mini 2",
	"iPad4,7": "iPad Mini 3",
	"iPad4,8": "iPad Mini 3",
	"iPad4,9": "iPad Mini 3",
	"iPad5,1": "iPad Mini 4",
	"iPad5,2": "iPad Mini 4",
	"iPad5,3": "iPad Air 2",
	"iPad5,4": "iPad Air 2"	,
	"iPad6,3": "iPad Pro 9.7",
	"iPad6,4": "iPad Pro 9.7",
	"iPad6,7": "iPad Pro 12.9",
	"iPad6,8": "iPad Pro 12.9",
	"iPad6,11": "iPad (2017)",
	"iPad6,12": "iPad (2017)",
	"iPad7,3": "iPad Pro 10.5",
	"iPad7,4": "iPad Pro 10.5",
	#iPod
	"iPod7,1": "iPod Touch 6"
}

# 240x240 display with hardware SPI:
disp = ST7789.ST7789(SPI.SpiDev(bus, device),RST, DC, BL)
disp.Init()
disp.clear()

#init GPIO
GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Input with pull-up
GPIO.setup(BL,GPIO.OUT)
GPIO.output(BL, GPIO.HIGH)

bold18 = ImageFont.truetype('fonts/arialbd.ttf', 18)
bold14 = ImageFont.truetype('fonts/arialbd.ttf', 14)
bold11 = ImageFont.truetype('fonts/arialbd.ttf', 11)
reg14 = ImageFont.truetype('fonts/arial.ttf', 14)
reg12 = ImageFont.truetype('fonts/arial.ttf', 12)
reg10 = ImageFont.truetype('fonts/arial.ttf', 10)
reg9 = ImageFont.truetype('fonts/arial.ttf', 9)


def insert_newlines(string, every=64):
    return '\n'.join(string[i:i+every] for i in range(0, len(string), every))

def menu_button(y, text, sel):
	if sel == 1:
		d.rectangle((0,y,240,y + 40), outline=0, fill=(240,240,240,100)) #center filled
		d.text((40,y + 5), text, font=fnt1, fill=(0,0,0,255))
	else:
		d.rectangle((0,y,240,y + 40), outline=0, fill=(20,20,20,100)) #center filled
		d.text((40,y + 5), text, font=fnt1, fill=(240,240,240,255))

def get_jailbreak_running():
	return jb["running"]

def set_disp_update():
		disp_update = True

## Return Mode of Device
## 0 = No Device 1 = DFU 2 = Recovery 3 = Normal
def dev_mode():
	lsusb = subprocess.check_output("lsusb")
	if (lsusb.find("05ac:12") < 1):
		return 0
	for line in lsusb.split("\n"):
		if "DFU" in line:
			return 1
		if "Recovery" in line:
			return 2
	return 3

## Get Device Info and store in dev
def dev_update():
	if (dev["mode"] == 3):
		try:
			ideviceinfo = subprocess.check_output("ideviceinfo")
			for line in ideviceinfo.split("\n"):
				if "ProductVersion" in line:
					split = line.split(":")
					dev["ios"] = split[1].strip()
				if "ProductType" in line:
					split = line.split(":")
					if dev_model[split[1].strip()]:
						dev["model"] = dev_model[split[1].strip()]
					else:
						dev["model"] = "Unsupported"
				if "UniqueDeviceID" in line:
					split = line.split(":")
					dev["udid"] = split[1].strip()
				if "UniqueChipID" in line:
					split = line.split(":")
					dev["ecid"] = split[1].strip()
		except:
			return


def get_ui_image(file):
	return os.getcwd() + '/ui/' + file
	
def ui_draw_bar(display, stage):
	bar = Image.open(get_ui_image('bar_' + str(stage) + '.jpg')).convert('RGBA') # Load background
	display.paste(bar, (17,120))

def ui_dev_connect(draw):
	draw.text((20,36), "Welcome to checkra1n!", font=bold18, fill=(224,224,224,255))
	
	## Device Info Display
	if (dev["mode"] == 0):
		txt = insert_newlines("Connect your iPhone, iPod Touch or iPad to begin.", 40)
		draw.text((10,66), txt, font=bold11, fill=(224,224,224,255))
	
	if (dev["mode"] == 1):
		txt = dev["model"] + " connected."
		txt = insert_newlines(txt, 40)
		txt = txt + "\nMode: DFU"
		
	if (dev["mode"] == 2):
		txt = dev["model"] + " connected."
		txt = insert_newlines(txt, 40)
		txt = txt + "\nMode: Recovery"	
		
	if (dev["mode"] == 3):
		txt = dev["model"] + " (iOS " + dev["ios"] + ") connected."
		txt = insert_newlines(txt, 40)
		txt = txt + "\nMode: Normal"
		txt = txt + "\nECID: 0x" + dev["ecid"]

	#draw.text((10,200), "Verbose boot", font=bold11, fill=(224,224,224,255))
	
	draw.text((10,66), txt, font=bold11, fill=(224,224,224,255))

def ui_jailbreak(draw, display):	
	txt = insert_newlines(jb["status"], 40)
	draw.text((10,66), txt, font=bold11, fill=(224,224,224,255))
	ui_draw_bar(display, jb["stage"])

	
class Thread_Button(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name

	def run(self):
		global disp_update, newprocess
		disp_bl = True
		while True:
		
			if not GPIO.input(KEY_LEFT_PIN): # button is released
				if ui["main_menu"] < 3 and ui["main_menu"] > 0:
					ui["main_menu"] -= 1
					disp_update = True
				sleep(0.5)
				
			if not GPIO.input(KEY_RIGHT_PIN): # button is released
				if ui["main_menu"] < 2 and ui["main_menu"] > -1:
					ui["main_menu"] += 1
					disp_update = True
				sleep(0.5)
				
			if not GPIO.input(KEY1_PIN): # button is released
				if ui["main_menu"] == 0:
					if (jb["running"] == True):
						os.system('killall -9 checkra1n')
						os.system('usbmuxd')
						jb["running"] = False
						ui["main_menu_options"][0] = "Jailbreak"
						disp_update = True
					else:
						jb["enable"] = True
							
				if ui["main_menu"] == 2:
					os.popen("sudo halt").read()
				sleep(0.5) #Stops spamming of the button
				
			if not GPIO.input(KEY2_PIN): # button is released
				ui["main_menu_show"] = not ui["main_menu_show"]
				disp_update = True
				sleep(0.5)
				
			if not GPIO.input(KEY3_PIN): # button is released
				if (disp_bl == True):
					GPIO.output(BL, GPIO.LOW)
					disp_bl = False
				else:
					GPIO.output(BL, GPIO.HIGH)
					disp_bl = True
				sleep(1)
				
			sleep(0.05)

class Thread_Display(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name

	def run(self):
		global disp_update, splash
		while True:
			if splash:
				image = Image.open(get_ui_image('ra1nman.jpg')) # Show splash screen
				disp.ShowImage(image,0,0)
				sleep(1)
				splash = False
				continue
				
			if disp_update:
				display = Image.open(get_ui_image('window.jpg')).convert('RGBA') 	# Load window into display image
				d = ImageDraw.Draw(display, 'RGBA')

				if jb["running"]:
					ui_jailbreak(d, display)
				else:
					ui_dev_connect(d)
				
				if ui["main_menu_show"]:
					## Options
					opt = "" + ui["main_menu_options"][ui["main_menu"]] + ""
					w, h = d.textsize(opt, font=bold18)
					wpos = (240-w)/2
					d.multiline_text( (wpos, 204), opt, font = bold18, fill = (224,224,224,255))
				
				disp.ShowImage(display,0,0)
				disp_update = False
				
class Thread_Device(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		
	def run(self):
		global disp_update
		while True:
			if not jb["running"]:
				mode = dev_mode()
				if (dev["mode"] != mode):
					dev["mode"] = mode
					dev_update()
					disp_update = True
			sleep(0.5)	
		
class Thread_Jailbreak(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		
	def test(self):
		if self.newprocess:
			jb["running"] = False
			self.newprocess.kill()
		return True
		
	def run(self):
		global disp_update
		sleep(1)	
		while True:
			if (jb["enable"] == True) and (jb["running"] == False):
				jb["running"] = True
				jb["enable"] = False
				jb["status"] = "Please wait..."
				ui["main_menu_options"][0] = "Stop"
				os.system('killall -9 usbmuxd')
				jb["stage"] = 0
				disp_update = True
				
				def process_output(line, stdin, newprocess):
					global disp_update
					#pattern = [" [*]"," [!]"]
					pattern = [" [*]"]
					res = [ele for ele in pattern if(ele in line)]
					show_output = bool(res)
					
					if show_output == True:
						line = line.strip(' - [*]: ')
						line = line.rstrip()
						
						jb["status"] = line
						
						if "DFU" in line:
							jb["stage"] = 1
						if "Checking" in line:
							jb["stage"] = 2
						if "Setting" in line:
							jb["stage"] = 3
						if "download" in line:
							jb["stage"] = 4			
						if "All Done" in line:
							jb["stage"] = 5
							newprocess.kill()
							os.system('usbmuxd')
							jb["running"] = False
							
						disp_update = True
				
				def done(cmd, success, exit_code):
					newprocess.kill()
					os.system('usbmuxd')
					jb["running"] = False
					ui["main_menu_options"][0] = "Jailbreak"
					os.system('usbmuxd')
					
				try:
					process = sh.Command('checkra1n')
					self.newprocess = process("-c", "-V", _out=process_output, _err=process_output, _done=done)
				except:
					sleep(1)
			sleep(1)
		

tb = Thread_Button("Thread_Button")
td = Thread_Display("Thread_Display")
ti = Thread_Device("Thread_Device")
tj = Thread_Jailbreak("Thread_Jailbreak")

td.start()
ti.start()
tb.start()
tj.start()

tb.join()
ti.join()
td.join()
tj.join()
