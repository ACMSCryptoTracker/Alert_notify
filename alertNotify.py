import select
import psycopg2
import json
import psycopg2.extensions
import smtplib
import string
import configparser
from collections import defaultdict
#Read Config File 

Config = configparser.ConfigParser()
Config.read("config.ini")

#Get database info from config file

hostname = Config.get("cryptocurrency","hostname") 
username = Config.get("cryptocurrency","username")
password = Config.get("cryptocurrency","password")
database = Config.get("cryptocurrency","database")
port=Config.get("cryptocurrency","port")

#Get Number of Different Currencies

limit=Config.get("cryptoparams","limit")

conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database,port=port)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
curr = conn.cursor()
curr.execute("LISTEN events;")
collection=[]
print "Waiting for notifications on channel 'myEvent'"
def sendEmail(current_value,emails):
	from_addr = 'urja4bluestar@gmail.com'
	subject='Alert'
	body_text='price change'
	print(emails)
	bodytext = string.join(("From: %s" % from_addr,"To: %s" % ', '.join(emails),"Subject: %s" % subject ,"",body_text), "\r\n")

	# Credentials (if needed)
	username = 'urja4bluestar@gmail.com'
	password = 'powers123' 
  
	# The actual mail sent
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.login(username,password)
	server.sendmail(from_addr,emails, bodytext)
	server.quit()
	print("Mail Sent")
		
def checkThresholdAlert(threshold_min,threshold_max,price,userid):
	if(price < threshold_min or price > threshold_max):
		return True
	return False

def checkPriceAlert(price,priceInc,priceDec,c_price,userid):
	if(c_price < price):
		percentage=(price-c_price)/price*100
		if(percentage >= priceDec):
			return True
	else:
		percentage=(c_price-price)/price*100
		if(percentage >= priceInc):
			return True
	return False

def checkVolumeAlert(volume,volInc,volDec,c_volume,userid):
	if(c_volume > volume):
		percentage=(c_volume-volume)/volume*100
		if(percentge >= volInc):
			return True
	else:
		precentage=(volume-c_volume)/volume*100
		if(percentage >= volDec):
			return True		
	return False

def checkMarketCapAlert(marketcap,mktInc,mktDec,c_marketcap,userid):
	if(c_marketcap > marketcap):
		percentage=(c_marketcap-marketcap)/marketcap*100
		if(percentage >= mktInc):
			return True
	else:
		percentage=(marketcap-c_marketcap)/marketcap*100
		if(percentage >= mktDec):
			return True
	return False

def findEmail(userid):
	selectQuery="select email from public.user where user_id={}".format(userid)
	curr.execute(selectQuery)
	result=curr.fetchall()
	return result[0][0]

def checkForAlert(collection):
      
      for i in range(len(collection)):
	   emailList=dict()
	   symbol=collection[i]['symbol']
	   #alert_type=collection[i]['alert_type']
	   selectQuery="select * from alert where coin_symbol='{}'".format(symbol)
	   curr.execute(selectQuery)
	   result=curr.fetchall()
	   price=collection[i]['price_usd']
	   volume=collection[i]['c_24h_volume_usd']
	   market_cap=collection[i]['market_cap_usd']
	   if(curr.rowcount != 0):
		for r in result:
		    if(r[2] == 'THRESHOLD_ALERT'):
		    	check=checkThresholdAlert(r[8],r[9],price,r[1])
		    elif(r[2] == 'PRICE_ALERT'):
			check=checkPriceAlert(r[5],r[6],r[7],price,r[1])
		    elif(r[2] == 'VOLUME_ALERT'):
			check=checkVolumeAlert(r[10],r[11],r[12],volume,r[1])
		    elif(r[2] == 'MARKETCAP_ALERT'):
			check=checkMarketCapAlert(r[13],r[14],r[15],market_cap,r[1])
		    if check == True:
			   email=findEmail(r[1])
			   if r[2] in emailList:
			   	emailList[r[2]].append(email)
			   else:
				emailList[r[2]]=[email]
     	   if 'THRESHOLD_ALERT' in emailList:
		sendEmail(price,emailList['THRESHOLD_ALERT'])
           if 'PRICE_ALERT' in emailList:
		sendEmail(price,emailList['PRICE_ALERT'])
           if 'VOLUME_ALERT' in emailList:
		sendEmail(volume,emailList['VOLUME_ALERT'])
           if 'MARKETCAP_ALERT' in emailList:
		sendEmail(market_cap,emailList['MARKETCAP_ALERT'])

while 1:
      conn.poll()
      while conn.notifies:
           notify = conn.notifies.pop(0)
           response=json.loads(notify.payload)
	   jsonObject=response['data']
	   collection.append(jsonObject)
      if len(collection) == 5 : 
           checkForAlert(collection)     	
	   collection=[]
	    

