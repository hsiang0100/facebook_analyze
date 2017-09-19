import sys
import json
import urllib.request
import requests
import datetime
import time
import statistics
import numpy as np

from snownlp import SnowNLP
from dateutil.parser import parse

access_token = 'your_token'
information_list = []

parameters_X = []
parameters_Y = []

#--------------------選擇1--------------------
def request_until_succeed(url):
	success = False
	times_try = 0
	while success is False and times_try<=3:
		try: 
			req = requests.get(url) #超過使用次數的時候回應<Response [403]>
			response = req.status_code
			#HTTP Status Code=200 is OK
			if response == 200:
				success = True
			times_try = times_try + 1
		except Exception as e:
			print(e)
			time.sleep(5)

			print("Error for URL %s: %s" % (url, datetime.datetime.now()))
			print("Retrying.")
	return req

def process_url(page_id, page_name, access_token, page_type):
	if(page_type=="search_id_from_name"):
		base = "https://graph.facebook.com"
		node = "/%s?" % page_name 
		parameters = "access_token=%s" % (access_token)
		url = base + node + parameters
		return url
	elif(page_type=="name_from_id"):
		base = "https://graph.facebook.com/v2.8"
		node = "/%s" % page_id 
		parameters = "/?access_token=%s" % (access_token)
		url = base + node + parameters
		return url	
	elif(page_type=="scrapeFacebookPage"):
		base = "https://graph.facebook.com/v2.8"
		node = "/%s/posts" % page_id 
		fields = "/?fields=message,link,created_time,type,name,id," + \
				"comments.limit(0).summary(true),shares,reactions.limit(0).summary(true)"
		parameters = "&limit=%s&access_token=%s" % (100, access_token)
		url = base + node + fields + parameters
		return url
	elif(page_type=="ranking_star"):
		base = "https://graph.facebook.com/v2.8"
		node = "/%s" % page_id 
		fields = "/?fields=overall_star_rating,rating_count,fan_count"
		parameters = "&access_token=%s" % (access_token)
		url = base + node + fields + parameters
		return url
	else:
		pass

def get_page_id(page_name):

	url = process_url(0, page_name, access_token, "search_id_from_name")
	res = request_until_succeed(url)

	if 'name' in res.json():
		page_name = res.json()['name']
		page_id = res.json()['id']
	else:
		page_name = "0"
		page_id = "0"
		
	return page_name, page_id 

def search_id_from_name():
	page_id_dict = {}
	stop = False

	while stop is False:
		page_name = input(">>> Please input page ID or name such as 186034394769383 or Cathaylife(0 to exit) ")
		
		#如果結束
		if page_name == "0":
			stop = True
		#如果不結束
		else:
			#找尋ID
			page_name, page_id  = get_page_id(page_name)
			#API出現error
			if page_name=="0":
				print ("Input error, try again")
			else:
				page_id_dict[page_id]=page_name
				print (page_id_dict)

#--------------------選擇1--------------------


#--------------------選擇2--------------------
#write and read json
def write_to_json_en(data):
	with open('id_to_name_dict.txt', 'w', encoding='UTF-8') as outfile:
		json.dump(data, outfile)

def read_from_json_en(file):
	with open(file, 'r', encoding='UTF-8') as outfile:
		data = json.load(outfile)
	return data

def read_file(file):
	with open(file, 'r', encoding='UTF-8') as outfile:
		data = outfile.readlines()
	return data
	
#對資料集做增加刪減
def process_dataset():
	page_id_list_en = dict()
	times_error = 0
	time_get_page_id = 0
	id_to_name_dict = read_from_json_en("id_to_name_dict.txt")
	
	stop = False

	while stop is False:
		insert_or_delete = input(">>> Please input 1,2,3 or 4 (1 to insert, 2 to delete, 3 to initialize, 4 to review dataset, 0 to exit) ")

		if(insert_or_delete=="1"):
			stop_1 = False

			while stop_1 is False:
				insert_id = input(">>> Insert data to dataset, Please input page name such as Cathaylife (0 to exit)")
				
				if insert_id=="0":
					stop_1 = True
				else:
					page_name, page_id = get_page_id(insert_id)
					page_id_list_en[page_id]=insert_id

					if page_id =="0":
						print ("Input error, try again or contact developer")
					elif page_id in id_to_name_dict:
						print (page_id + " has existed in dataset")
					else:
						id_to_name_dict.update(page_id_list_en)

						try: 
							write_to_json_en(id_to_name_dict)
							print ("Sucess to update " + page_id + " into dataset")
						except Exception as e:
							print ("Fail to update " + page_id + " into dataset")
				
		elif(insert_or_delete=="2"):
			stop_2 = False

			while stop_2 is False:
				delete_id = input(">>> delete data from dataset, Please input page name such as Cathaylife: (0 to exit)")

				if delete_id=="0":
					stop_2 = True
				else:
					page_name, page_id = get_page_id(delete_id)
					page_id_list_en[page_id]=delete_id

					if page_id in id_to_name_dict:
						id_to_name_dict.pop(page_id, None)
						try: 
							write_to_json_en(id_to_name_dict)
							print ("Sucess to delete " + page_id + " from dataset")
						except Exception as e:
							print ("Fail to delete " + page_id + " from dataset")
					else:
						print (page_id + " has not existed in dataset")

		elif(insert_or_delete=="3"):
			print ("Initialize dataset")
			id_to_name_dict.clear()

			training_dataset = read_file("training_dataset.txt")

			for training_data_ele in training_dataset:
				print (time_get_page_id)
				page_name, page_id = get_page_id(training_data_ele.replace('\n',''))
				if page_name=="0":
					times_error = times_error + 1

				training_data = training_data_ele.replace('\n','')
				page_id_list_en[page_id]=training_data
				print (training_data.replace('\n',''))
				print (page_id)
				time_get_page_id = time_get_page_id + 1


			id_to_name_dict.update(page_id_list_en)
			try: 
				write_to_json_en(id_to_name_dict)
				print ("Sucess to update data into dataset")
			except Exception as e:
				print ("Fail to update data into dataset")

		elif(insert_or_delete=="4"):
			print ("Data in dataset")
			print (read_from_json_en("id_to_name_dict.txt"))

		else:
			stop = True


#--------------------選擇2--------------------



#--------------------選擇3--------------------
#可新增刪除但還沒有訓練
def training_model(days):
	id_to_name_dict = read_from_json_en("id_to_name_dict.txt")

	parameters_X = []
	parameters_Y = []
	result_NLP = []
	result_likes = []
	result_comments = []
	result_shares = []
	result_fans = []
	score_list = []
	blank_list=[]
	count = 0
	#利用scrapeFacebookPage取得所需要的值
	for id_to_name_ele in id_to_name_dict:
		
		print ("###########################")
		print (count)
		print (id_to_name_dict[id_to_name_ele])
		
		NLP_list_avg, median_reaction, median_comment, median_share, page_rating, page_fan_count = scrapeFacebookPage(id_to_name_ele,days)

		if(page_rating!=0 and NLP_list_avg!=0):
			parameters_X.append([round(NLP_list_avg,3), round(median_reaction,3), round(median_comment,3), round(median_share,3), page_fan_count])
			
			print (page_rating)
			if(page_rating<=3):
				page_rating=1
			elif(page_rating>3 and page_rating<=3.5):
				page_rating=2
			elif(page_rating>3.5 and page_rating<=4):
				page_rating=3
			elif(page_rating>4 and page_rating<=4.5):
				page_rating=4
			elif(page_rating>4.5 and page_rating<=5):
				page_rating=5
			parameters_Y.append(page_rating)
			blank_list.append([page_rating, id_to_name_ele,round(NLP_list_avg,3), round(median_reaction,3), round(median_comment,3), round(median_share,3), page_fan_count])
		else:
			pass
		count = count + 1

	print ("###########################")
	for ele in blank_list:
		print (ele)
	print ("###########################")

	parameters = blank_list
	parameters_X = []
	parameters_Y = []
	result_NLP = []
	result_likes = []
	result_comments = []
	result_shares = []
	result_fans = []
	score_list = []

	for parameters_ele in parameters:
		parameters_X.append([parameters_ele[2],parameters_ele[3],parameters_ele[4],parameters_ele[5],parameters_ele[6]])
		parameters_Y.append(parameters_ele[0])
		result_NLP.append(parameters_ele[2])
		result_likes.append(parameters_ele[3])
		result_comments.append(parameters_ele[4])
		result_shares.append(parameters_ele[5])
		result_fans.append(parameters_ele[6])

	#NLPs
	result_NLP_25 = np.percentile(result_NLP,25)
	result_NLP_50 = np.percentile(result_NLP,50)
	result_NLP_75 = np.percentile(result_NLP,75)
	#likess
	result_likes_25 = np.percentile(result_likes,25)
	result_likes_50 = np.percentile(result_likes,50)
	result_likes_75 = np.percentile(result_likes,75)
	#comments
	result_comment_25 = np.percentile(result_comments,25)
	result_comment_50 = np.percentile(result_comments,50)
	result_comment_75 = np.percentile(result_comments,75)
	#s
	result_shares_25 = np.percentile(result_shares,25)
	result_shares_50 = np.percentile(result_shares,50)
	result_shares_75 = np.percentile(result_shares,75)
	#fans
	result_fans_25 = np.percentile(result_fans,25)
	result_fans_50 = np.percentile(result_fans,50)
	result_fans_75 = np.percentile(result_fans,75)

	file = open("parameter.txt", 'w', encoding = 'UTF-8')
	file.write(str(result_NLP_25)+"\n"+str(result_NLP_50)+"\n"+str(result_NLP_75)+"\n"+ \
				str(result_likes_25)+"\n"+str(result_likes_50)+"\n"+str(result_likes_75)+"\n"+
				str(result_comment_25)+"\n"+str(result_comment_50)+"\n"+str(result_comment_75)+"\n"+
				str(result_shares_25)+"\n"+str(result_shares_50)+"\n"+str(result_shares_75)+"\n"+
				str(result_fans_25)+"\n"+str(result_fans_50)+"\n"+str(result_fans_75)+"\n")
	file.close()

	print (result_NLP_25,result_NLP_50,result_NLP_75)
	print (result_likes_25,result_likes_50,result_likes_75)
	print (result_comment_25,result_comment_50,result_comment_75)
	print (result_shares_25,result_shares_50,result_shares_75)
	print (result_fans_25,result_fans_50,result_fans_75)

#--------------------選擇3--------------------

#--------------------選擇4--------------------
def check_datetime(time,days):
	
	result = 0
	post_time = parse(time).date()
	now_time = datetime.datetime.now().date()
	
	diff = now_time - post_time
	diff_to_int = int(str(diff.days))
	if (diff_to_int<days):
		result = True
	else:
		result = False

	return result

def NLP_sentimental(post_message_lists):
	#s = SnowNLP('')
	score_list = []
	for post_message_ele in post_message_lists:
		s = SnowNLP(post_message_ele)
		score_list.append(s.sentiments)

	try:
		NLP_list_avg=sum(score_list)/len(score_list)
	except Exception as e:
		NLP_list_avg = 0

	return NLP_list_avg

def process_Info(information, access_token):
	information_id = information['id']

	if 'reactions' not in information:
		num_reactions = 0
	else:
		num_reactions = information['reactions']['summary']['total_count']

	if 'comments' not in information:
		num_comments = 0
	else:
		num_comments = information['comments']['summary']['total_count']

	if 'shares' not in information: 
		num_shares = 0
	else:
		num_shares = information['shares']['count']

	if 'message' not in information: 
		post_message = 0
	else:
		post_message = information['message']

	if 'id' not in information: 
		post_id = 0
	else:
		post_id = information['id']

	if 'created_time' not in information: 
		post_time = 0
	else:
		post_time = information['created_time'][:10]
	
	return (num_reactions, num_comments, num_shares, post_message, post_id, post_time)

def information_append(page_id, information, reactions_lists, comment_lists, share_lists, post_message_lists, num_processed):
	(num_reactions, num_comments, num_shares, post_message, post_id, post_time) = process_Info(information, access_token)
	#information_list.append([page_id, information_name, information_id, information_message, information_time, num_reactions, num_comments, num_shares])
	information_list.append([page_id, post_id, post_time, num_reactions, num_comments, num_shares])

	reactions_lists.append(num_reactions)
	comment_lists.append(num_comments)
	share_lists.append(num_shares)
	post_message_lists.append(post_message)

	num_processed += 1
	# if num_processed % 100 == 0:
	# 	print("%s Statuses Processed: %s" % (num_processed, datetime.datetime.now()))
	#print (num_reactions)
	return (reactions_lists, comment_lists, share_lists, post_message_lists, num_processed)

def scrapeFacebookPage(page_id, days):
	num_processed = 0
	scrape_starttime = datetime.datetime.now()

	print (page_id)
	reactions_lists=[]
	comment_lists=[]
	share_lists=[]
	nlp_lists=[]
	post_message_lists=[]

	#----------------get page name----------------
	url_name_from_id = process_url(page_id, 0, access_token, "name_from_id")
	res_name_from_id = request_until_succeed(url_name_from_id)

	if 'name' in res_name_from_id.json():
		page_name = res_name_from_id.json()['name']
	else:
		page_name = 0

	#----------------get page rank----------------
	url_rank = process_url(page_id, 0, access_token, "ranking_star")
	res_rank = request_until_succeed(url_rank)

	#print (url_rank)
	if 'overall_star_rating' in res_rank.json():
		page_rating = res_rank.json()['overall_star_rating']
	else:
		page_rating = 0

	if 'fan_count' in res_rank.json():
		page_fans = res_rank.json()['fan_count']
	else:
		page_fans = 0	

	
	#----------------get information from specific page----------------
	url_scrape = process_url(page_id, 0, access_token, "scrapeFacebookPage")
	res_scrape = request_until_succeed(url_scrape)

	#get page information each page	
	while 'paging' in res_scrape.json(): 
		for information in res_scrape.json()['data']:
			#check wheher date smaller than three year
			if_smaller_days = check_datetime(information['created_time'], days)
			
			if 'message' in information and if_smaller_days:
				reactions_lists, comment_lists, share_lists, post_message_lists, num_processed= information_append(page_id, information, reactions_lists, comment_lists, share_lists, post_message_lists, num_processed)
				
		res_scrape = request_until_succeed(res_scrape.json()['paging']['next'])

	#caculate
	page_NLP = NLP_sentimental(post_message_lists)
	
	try:
		page_reaction = sum(reactions_lists)/len(reactions_lists)
		median_reaction = statistics.median(sorted(reactions_lists))
	except Exception as e:
		page_reaction = 0
		median_reaction = 0

	try:
		page_comment = sum(comment_lists)/len(comment_lists)
		median_comment = statistics.median(sorted(comment_lists))
	except Exception as e:
		page_comment = 0
		median_comment = 0

	try:
		page_share = sum(share_lists)/len(share_lists)
		median_share = statistics.median(sorted(share_lists))
	except Exception as e:
		avg_share = 0
		page_share = 0
	
	return page_NLP, page_reaction, page_comment, page_share, page_rating, page_fans 

def testing_model(days):

	stop = False

	while stop is False:
		page_id_input = input(">>> Please input page ID such as 186034394769383 (0 to exit) ")

		if (page_id_input=="0"):
			stop = True
		else:
			page_NLP, page_reaction, page_comment, page_share, page_rating, page_fans = scrapeFacebookPage(page_id_input, days)
			if(page_NLP==0 and page_reaction==0 and page_comment==0 and page_share==0 and page_fans==0):
				print ("Input error page ID, please try again or contact to developer")
			else:
				parameter = read_file("parameter.txt")
				parameter_list = []
				for parameter_list_ele in parameter:
					parameter_list.append(float(parameter_list_ele.replace('\n','')))

				#print (parameter_list)
				score = 0

				#NLP
				if(page_NLP<parameter_list[0]):
					score = score + 1
				elif(page_NLP>=parameter_list[0] and page_NLP<parameter_list[1]):
					score = score + 2		
				elif(page_NLP>=parameter_list[1] and page_NLP<parameter_list[2]):
					score = score + 3		
				elif(page_NLP>=parameter_list[2]):
					score = score + 4		

				#likes
				if(page_reaction<parameter_list[3]):
					score = score + 1
				elif(page_reaction>=parameter_list[3] and page_reaction<parameter_list[4]):
					score = score + 2		
				elif(page_reaction>=parameter_list[4] and page_reaction<parameter_list[5]):
					score = score + 3		
				elif(page_reaction>=parameter_list[5]):
					score = score + 4	
					
				#comments
				if(page_comment<parameter_list[6]):
					score = score + 1
				elif(page_comment>=parameter_list[6] and page_comment<parameter_list[7]):
					score = score + 2		
				elif(page_comment>=parameter_list[7] and page_comment<parameter_list[8]):
					score = score + 3		
				elif(page_comment>=parameter_list[8]):
					score = score + 4	
					
				#shares
				if(page_share<parameter_list[9]):
					score = score + 1
				elif(page_share>=parameter_list[9] and page_share<parameter_list[10]):
					score = score + 2		
				elif(page_share>=parameter_list[10] and page_share<parameter_list[11]):
					score = score + 3		
				elif(page_share>=parameter_list[11]):
					score = score + 4	
					
				#fans
				if(page_fans<parameter_list[12]):
					score = score + 1
				elif(page_fans>=parameter_list[12] and page_fans<parameter_list[13]):
					score = score + 2		
				elif(page_fans>=parameter_list[13] and page_fans<parameter_list[14]):
					score = score + 3		
				elif(page_fans>=parameter_list[14]):
					score = score + 4	
					
				print ("Evaluate " + page_id_input + " page credit is " + str(int(score/4)))

#--------------------選擇4--------------------


def main():

	length_of_time = input(">>> Please input 1,2 or 3 to choose length of time to scrape from facebook (1 to one years, 2 to two years, 3 to three years)")
	stop = False
	days = 0
	while stop==False:
		if (length_of_time!="1" or length_of_time!="2" or length_of_time!="3"):
			if length_of_time=="1":
				days = 365
				print ("Length of time is one year")
			elif length_of_time=="2":
				days = 730
				print ("Length of time is two years")
			elif length_of_time=="3":
				days = 1095
				print ("Length of time is three years")
			stop =True
		else:
			print ("Input error, exit")


	service_option = input(">>> Please input 1,2,3 or 4 (1 to search page ID, 2 to insert or delete data of dataset, 3 to train dataset, 4 to evaluate credit, other to exit)")
	while (service_option!="1" or service_option!="2" or service_option!="3" or service_option!="4"):
		#完成
		if(service_option=="1"):
			print("----------Search page ID----------")
			search_id_from_name()
			
		#完成
		elif(service_option=="2"):
			print("----------Insert or delete data of dataset----------")
			process_dataset()

		#完成
		elif(service_option=="3"):
			print("----------Train dataset----------")
			training_model(days)

		#完成
		elif(service_option=="4"):
			print("----------Evaluate credit----------")
			testing_model(days)

		#完成
		else:
			print("Exit")
			sys.exit()

		service_option = input(">>> Please input 1,2,3 or 4 (1 to search page ID, 2 to insert or delete data of dataset, 3 to train dataset, 4 to evaluate credit, other to exit)")

if __name__ == '__main__':
	main()