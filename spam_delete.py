#!/usr/bin/python3
import imaplib,datetime,configparser,logging

#function to handle imap connection
def connect_imap():
	imap_mail = imaplib.IMAP4_SSL('imap.gmail.com',port=993) #create SSL connection to host
	try:
		log.info("{0} Connecting to mailbox via IMAP...".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
		config = configparser.ConfigParser()
		config.read('config.properties')
		user_acct = config.get('ImapConfig','mail.account')
		pw = config.get('ImapConfig','mail.pw')
		imap_mail.login(user_acct,pw) #if 2-step verification is used, app password will need to be established
	except: 
		log.error("{0} Error on connecting to mailbox via IMAP...".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
		return -1
	return imap_mail


def delete_spam(imap):
	imap.select('[Gmail]/Spam') #select the Spam Folder
	res,count = imap.search(None,'ALL') #search and get a count
	result,spam_uid = imap.uid('Search',None,'ALL') #search all emails in the Spam Folder
	spam_count = count[0].decode()
	if not spam_count:
		log.info("No spam currently")
		imap.close() #close the selected folder
	else:
		log.info(spam_count[-1] + " Spam emails selected for removal")
		spamlist = spam_uid[0].split() #pass the list of UID to the spamlist
		#iterate over the list and set the flags to delete
		for spam in spamlist:
			type,resp = imap.uid('store',spam, '+FLAGS', r'(\Deleted)')
		expunge_result,response = imap.expunge() #delete the spam
		imap.close() #close the selected folder
		log.info("All Spam messages deleted") 

def delete_trash(imap):
	imap.select('[Gmail]/Trash') #select the Trash Folder
	res,count = imap.search(None,'ALL') #search and get a count
	result,trash_uid = imap.uid('Search',None,'ALL') #search all emails in the Trash Folder
	trash_count = str(count[0], encoding='utf8')
	trash_count = count[0].decode()
	if not trash_count:
		log.info("No trash currently") #this needs to be changed to logger
		imap.close() #close the selected folder
	else:
		log.info(trash_count[-1] + " Emails selected for deletion")
		trashlist = trash_uid[0].split() #pass the list of UID to the trashlist
		#iterate over the list and set the flags to delete
		for trash in trashlist:
			type,resp = imap.uid('store',trash, '+FLAGS', r'(\Deleted)')
		expunge_result,response = imap.expunge() #delete the trash
		imap.close() #close the selected folder
		log.info("Trash has been emptied") #

def disconnect_imap(imap):
	log.info("{0} Task Completed. Logging out.\n".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
	imap.logout() #log out of the system
	return

if __name__ == '__main__':
	#handle all the basic logging info
	logging.basicConfig(filename='imap_data.log',level=logging.DEBUG)
	log = logging.getLogger('imap')
	conn = connect_imap() #make connection to imap
	#if the connection has failed
	if conn == -1:
		log.error("Error! Unable to establish a connection. Aborting!\n")
	else:
		delete_spam(conn) #delete all spam
		delete_trash(conn) #clear the trash
		disconnect_imap(conn) #close the connection
