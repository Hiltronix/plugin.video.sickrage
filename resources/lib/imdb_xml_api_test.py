import httplib2
import urllib
from bs4 import BeautifulSoup
import ast
import json
import re
import io

class IMDBCall:
	# This class gets JSON output for every search of IMDB API.

    def writeLog(self, title):
        # writeLog will write the content of those movies, which cannot be fetched.
        codec = 'cp1252'
        with io.open('D:\\Temp\\.cache\\error.json', mode='a', encoding=codec) as file_name:
            file_name.write(unicode(title, codec))


    def getResults(self,name):
		print "creating a request for", name
		#Get the movie name - and Percent Encode it.
		name = urllib.quote(name);
		title = ''

		#h = httplib2.Http()
		h = httplib2.Http("D:\\Temp\\.cache")
		#First make the call to IMDB and try getting the JSON.

		resp, content = h.request("http://www.imdb.com/xml/find?json=1&q="+name+"&s=all", "GET")

		try:

            #If the JSON returns is Valid, then process it and get the exact title name.
            #If the JSON isn't valid,i.e. if you get an XML, then raise an exception.
            #If you get a Valid JSON- You still don't have the information about
            #genres, so make an explicit call to IMDBAPI to get the tags from the
            #movie name.

			json.loads(content)

			#Catch any error
			try:
				#if the JSON is valid : IMDB gives two types of objects when you search
				#If there is an exact match, then you get `exact_match` object, else you
				#get `title_popular` if there is a approximate match.
				#convert the JSON into a Python dictionary.
				cont =  ast.literal_eval(content)
				#check for both title popular and title_exact, if none found, return.
				if 'title_popular' in cont:
					title  = ast.literal_eval(content)['title_popular'][0]['title']
				elif 'title_exact' in cont:
					title  = ast.literal_eval(content)['title_exact'][0]['title']
				else:
					print("No title_popular or title_exact found. Hence returning.")
					self.writeLog('No title_popular or title_exact found. Hence returning.',title);
					return;

			except:
				print("error with title_popular",content)
				self.writeLog(content+":"+title);
				return;

			#if all is well, then get the title
			actualTitle = title

			#replacing '  from the movie results(for making the next call)
			title = re.sub("&#x27;","",actualTitle)

            #Percent encode this(for making the next call)
			title = urllib.quote(title);

			#make the call to IMDBAPI for getting the tags.
			resp,content = h.request("http://mymovieapi.com/?title="+title+"&type=json&plot=simple&episode=1&limit=1&yg=0&mt=none&lang=en-US&offset=&aka=simple&release=simple&business=0&tech=0")



			#Evaluate the JSON and create a dictionary.
			try:
				movieDict1 = dict()
				try:
					movieDict1['tags'] = ast.literal_eval(content)[0]['genres']
					movieDict1['name'] = actualTitle
					movieDict1['ready'] = 'true'
					#return the information in the format after making it a string.
					return json.dumps(movieDict1);
				except KeyError:
					print("Did nothing, as there is no genre" ,content)
					self.writeLog(content);
					return ;
			except ValueError:
				print "Error"
				self.writeLog(content);
				return

		#Here is the best part about IMDB:
		#If it is very sure that the movie you are searching is already there
		#It returns the entire HTML page of that movie.
		#Hence all you have to do is to Scrape the page.
		#Using Beautiful Soup to scrape the page.
		#This page also contains the genres, So you actually don't need to
		#make another call.

		except :
			print 'inside'
			movieDict = dict();
        	soup = BeautifulSoup(content)
        	try:

        		movieDict['name'] = soup.find_all(itemprop="name")[0].get_text();
        		movieDict['ready'] = 'true'

        		movieDict['tags'] = [BeautifulSoup(str(x)).span.get_text()  for x in soup.find_all(itemprop ="genre") if str(BeautifulSoup(str(x)).span) != 'None' and BeautifulSoup(str(x)).span.get_text() != '|']
        	except:
        		self.writeLog(content)
        		return


        	return json.dumps(movieDict)

#sample call
print IMDBCall().getResults('8mm')
