# -*- coding: utf-8 -*-
#Author: Chen Chunyang, Teong Ke Ming
#Function
'''
This file is used to recognize the category of tags in Stack Overflow based on the first sentence in the tagWiki.
It achieves the goal in several steps:
1. Preprocess the data and extract the first sentence;
2. Extract POS tag for each sentence;
3. Extract svo (subject-verb-object) by chunking the sentences;
4. Refine the results in step 2 and find the category which is not applicable for the step 3 by simply word matching.
5. Normalize the category words and integrate all of them into one file.
6. Finally, check results manually especially tags with ".js"(javascript), "sharp"(c#), "4j"(java), "py"(python), "php"(php), "cpp"(c++) 
'''

import re
import os
import nltk
from operator import itemgetter
from nltk.tag.stanford import StanfordPOSTagger
os.environ['JAVAHOME'] = 'C:\\Program Files\\Java\\jre1.8.0_121\\bin' #Lynn
os.environ['CLASSPATH'] = 'C:\\jars\\stanford-postagger.jar' #Lynn:download and put into C drive
import string
from random import randint

#Delete some empty files and only get the first sentence of each file
#Preprocess the first sentence to remove unwanted words or symbols
def preprocess(inputFile, outputFile_processed): #delete outputFile
	firstSentences = {}        #Store the first sentence for each term
	findtagwiki = open('nulltagexcerpt.txt','w',encoding = 'utf8')
	
	f = open(inputFile, encoding = 'utf8') #Lynn
	lines = f.readlines()
	f.close()
	
	#removeList = ["Questions", "Question","For questions", "for questions","This tag", "this tag", "THIS TAG", "For issues", "for issues"] # "Use this tag", "DO NOT", "This is a tag"}
	#Lynn: disable the removeList, first sentence highly likely to contain category even with keywords in removeList	
	
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if len(items) == 2:
			if items[1] != r"\N":
				firstSentences[items[0]] = items[1].split(". ")[0]
				if ".&" in firstSentences[items[0]]:
					firstSentences[items[0]] = items[1].split(".&")[0]
					#print items[0]
			else:
				findtagwiki.write(items[0]+'\n')
	findtagwiki.close()


	
	print(str(len(firstSentences)))

	""" #Lynn: disabled the removeList, fw is not used
	fw = open(outputFile, 'w', encoding = 'utf8') #Lynn
	for item in firstSentences:
		remove = 0
		for removeItem in removeList:
			if removeItem in firstSentences[item]:
				remove =1
				break
		if remove ==0:
			fw.write(item+'		'+firstSentences[item]+'\n')      #Split by two tab spaces
		else:
			fw.write(item+'		\n') #removed tag
	fw.close()
	"""

	conjunctionList = [" set of", " sets of", " collection of", " collections of", " part of", \
						" parts of", " type of", " types of", " version of", " versions of", \
						" group of", " groups of", " kind of", " kinds of", "form of ", " forms of",\
						 " piece of", " pieces of", " sequence of", " iteration of the",\
						 "family of ", "families of ", "variety of ", "superset of ","subset of ",\
						 "series of ","one of ", "suite of ", "component of "]    #conjuction list #Lynn add in missing ones

	fwp = open(outputFile_processed, 'w', encoding = 'utf8') #Lynn
	for item ,value in firstSentences.items():
		#Delete content in bracklets
		if "(" in value:
			value = re.sub(r" \(.+?\)", "", value)          
		if "[" in value:
			value = re.sub(r" \[.+?\]", "", value)
		if "<" in value:
			value = re.sub(r" \<.+?\>", "", value)
		
		#Change phrases for pos 
		if "It's" in value.lower():
			value = value.replace("It's","It is")
		if "open source" in value.lower():
			value = value.replace("open source","open-source")
		if "neural network" in value.lower():
			value = value.replace("neural network","neural-network")
		if "cross platform" in value.lower():
			value = value.replace("cross platform","cross-platform")
		if "object oriented" in value.lower(): 
			value = value.replace("object oriented","object-oriented")
			value = value.replace("Object Oriented","Object-Oriented")
		if "end user" in value.lower():
			value = value.replace("end user","end-user")
			
		value = value.replace("\"","")
		
		#remove certain phrases
		for conjunction in conjunctionList:
			#print(conjunction)
			value = value.replace(conjunction, "") 
			#print(value)
		
		""" #Lynn disabled the removeList
		remove = 0
		for removeItem in removeList:
			if removeItem in firstSentences[item]:
				remove =1
				break
				
		if remove ==0:
		"""

		fwp.write(item+'		'+value+'\n')      #Split by two tab spaces
		
		"""#Lynn disabled the removeList
		else:
			fwp.write(item+'		\n') #removed tag
		"""
	
	fwp.close()
	
	
#Extract POS tag extractPOS(f_preprocess2,f_allTags, f_version,f_pos)
def extractPOS(inputFile_data,  inputFile_tags, inputFile_version, outputFile_pos):

	f = open(inputFile_tags, encoding = 'utf8') #Lynn
	allTags=set(f.read().split(","))                #Load all tags
	f.close()
	
	f = open(inputFile_version, encoding = 'utf8') #Lynn
	lines = f.readlines()
	f.close()
	tag_version = []                                #tags with version number
	for index, row in enumerate(lines):
		items = row.strip().split()
		if items[0] in allTags:
			for tag in items[1].split(","):
				tag_version.append(tag)
				
	print("The number of tag_version is: "+ str(len(tag_version)))
	tag_version = set(tag_version)	
	
	fw_pos = open(outputFile_pos, "w", encoding = 'utf8') #Lynn
	english_postagger = StanfordPOSTagger('E:\RerunKeming-CategoryExtraction\models\english-bidirectional-distsim.tagger') #Lynn
	f = open(inputFile_data, encoding = 'utf8')
	lines = f.readlines()
	f.close()
	totallength = len(lines)
	
	for index, row in enumerate(lines):
		if index <=10000:
			if index %300 == 0:
				print(str(index) + " Finish " + str(float(index)/totallength))
			items = row.strip().split("\t\t")
			
			#if index >=5000 and index < 6000 and items[0] in tag_version:
			if items[0] in tag_version:
				fw_pos.write(str(index) +"	"+items[0]+"	\n")
			if items[0] not in tag_version:
				
				fw_pos.write(str(index)+"	"+items[0] +"	")	
				if len(items)>1:
					text = items[1].split(". ")[0]#.decode('utf-8')   #Lynn     
					pos = nltk.pos_tag(text.split())  #use nltk tagger method instead	
				
					for p in pos:
						fw_pos.write(str(p))
						fw_pos.write("	")
				
				fw_pos.write("\n")
			
			
	fw_pos.close()		

	
	
#Extract the tripul SVO (subject-verb-object) or nouns from incomplete sentence
def extractSVO(inputFile_data, inputFile_pos, outputFile_svo, outputFile_exception):
	
	grammar_sov = r"NP: {<DT>*<VBN>*<JJ>*<VBG>*<NN.*>+<VB[ZP]+><TO>*<IN>*<DT>*<VBN>*<JJ>*<VBG>*<NN.*>+}"    #Extract SVO from complete sentences e.g., LimeJS is a HTML5 game framework for building fast, native-experience games
	grammar_sov2 = r"NP2: {<DT>*<VBN>*<JJ>*<VBG>*<NN.*>+<VB[ZP]+><TO>*<IN>*<DT>*<VBN>*<JJ>*<VBG>*<NN.*>*<CC><DT>*<VBN>*<JJ>*<VBG>*<NN.*>+}"    #Extract two category e.g., 4store is a database storage and query engine that holds RDF data
	grammar_subject = r"SB: {<DT>*<VBN>*<JJ>*<VBG>*<NN.*>+<IN>}"              #Extract noun from incomplete sentence. e.g., A Server Process ID for MS SQL Server or Sybase ASE
	grammar_subject2 = r"SB2: {<DT>*<VBN>*<JJ>*<VBG>*<NN.*>+<WDT>}"              #Extract noun from incomplete sentence. e.g., A C++11 feature which allows braces to be used to initialize any variable in any context
	#Lynn add in the following:
	grammar_subject3 = r"SB3: {<DT>*<VBN>*<JJ>*<VBG>*<NN.*>+<JJ>}" #Assets necessary for implementing...
	grammar_subject4 = r"SB4: {<DT>*<VBN>*<JJ>*<VBG>*<NN.*>+<VB[NG]+>}" #Programming language constructs designed to handle errors 

	cp_sov = nltk.RegexpParser(grammar_sov)
	cp_sov2 = nltk.RegexpParser(grammar_sov2)
	cp_sb = nltk.RegexpParser(grammar_subject)
	cp_sb2 = nltk.RegexpParser(grammar_subject2)
	#Lynn add in the following:
	cp_sb3 = nltk.RegexpParser(grammar_subject3) #Assets necessary for implementing...
	cp_sb4 = nltk.RegexpParser(grammar_subject4) #Programming language constructs designed to handle errors 


	english_postagger = StanfordPOSTagger('E:\RerunKeming-CategoryExtraction\models\english-bidirectional-distsim.tagger') #Lynn
	
	fw_svo = open(outputFile_svo, "w", encoding = 'utf8') #Lynn
	fw_exception = open(outputFile_exception, "w", encoding = 'utf8') #Lynn
	
	
	f = open(inputFile_data, encoding = 'utf8') #Lynn
	lines = f.readlines()
	f.close()
	f = open(inputFile_pos, encoding = 'utf8') #Lynn
	poslines = f.readlines()
	f.close()
	
	
	for index, row in enumerate(lines):
		if index %300 == 0:
			#break
			print( str(index) + " Finish "+ str(float(index)/len(lines)))
		
		items = row.strip().split("		")
		
		text =""
		if len(items)>1:
			text = items[1].split(". ")[0]#.decode('utf-8') #Lynn
		pos =[]
		print(index)
		splitpos = poslines[index].split("	")
		for p in splitpos:
			if p != "\n" and splitpos.index(p)>1:
				pos.append(eval(p))
				
		
		chunkResult = cp_sov.parse(pos)
		
				
		svo = ""
		
		verbList = ["is", "are", "was", "were"]
		vb = 0
		for x in chunkResult.subtrees():
			
			if x.label() == "NP":
				
				i = -1
				while("NN" in x[i][1]):
					temp=svo					#temporary store the last few noun 
					svo =  x[i][0] + " " +temp   #append previous noun to svo	              				
					i-=1
				j=i
				while j>=-(len(x)):
					if "VB" in x[j][1]:			
						for verb in verbList:	#check if the VB is in verbList
							if verb == x[j][0]:
								vb=1
						break
					j-=1
				
				if vb==0:
					
					#svo = ""
					#Lynn: not is are was were, may be verb, extract noun at the beginning of sentence
					svo = ""
					i = 0
					while "DT" in x[i][1] or "VBN" in x[i][1] or "JJ" in x[i][1] or "VBG" in x[i][1]:
						i += 1
					while("NN" in x[i][1]):
						temp=svo					#temporary store the last few noun 
						svo =  temp + " " +x[i][0] #append previous noun to svo	              				
						i+=1
				break
			
		
		#Extract second category	
		chunkResult2 = cp_sov2.parse(pos)
		multipleCat = 0
		svo2=""
		for x in chunkResult2.subtrees():
			if x.label() == "NP2":
				i = -1
				while("NN" in x[i][1]):
					temp=svo2					#temporary store the last few noun 
					svo2 =  x[i][0] + " " +temp   #append previous noun to svo	              				
					i-=1
				
				j=i
				while j>=-(len(x)):
					if "CC" in x[j][1] and x[j][0]=="and":
						multipleCat =1
						break
					j-=1
					
					
				if multipleCat==0:
					svo2 = ""
				break	
		
		
		svo = svo.replace(",","")
		svo2 = svo2.replace(",","")
		
		if svo == "":
			chunkResult = cp_sb2.parse(pos)
			sb = ""
			for x in chunkResult.subtrees():
				if x.label() == "SB2":
					i = -2
					while i>=-(len(x)) and "NN" in x[i][1] :
						temp=sb					#temporary store the last few noun 
						sb =  x[i][0] + (" " +temp )  #append previous noun to sb	              				
						i-=1
					break
					
			if sb == "":
				chunkResult = cp_sb.parse(pos)
				for x in chunkResult.subtrees():
					if x.label() == "SB":
						#list(chunkResult)[1].draw()
						i = -2
						while i>=-(len(x)) and "NN" in x[i][1] :
							temp=sb					#temporary store the last few noun 
							sb =  x[i][0] + (" " +temp )  #append previous noun to sb	              				
							i-=1
						break

				#Lynn add in the following:
				if sb == "":
					chunkResult = cp_sb3.parse(pos)
					for x in chunkResult.subtrees():
						if x.label() == "SB3":
							#list(chunkResult)[1].draw()
							i = -3
							while i>= -(len(x)) and "NN" in x[i][1] :
								temp=sb					#temporary store the last few noun 
								sb =  x[i][0] + (" " +temp )  #append previous noun to sb	              				
								i-=1
							break


					if sb == "":
						chunkResult = cp_sb4.parse(pos)
						for x in chunkResult.subtrees():
							if x.label() == "SB4":
								#list(chunkResult)[1].draw()
								i = -3
								while i>= -(len(x)) and "NN" in x[i][1] :
									temp=sb					#temporary store the last few noun 
									sb =  x[i][0] + (" " +temp )  #append previous noun to sb	              				
									i-=1
								break


						if sb == "":
							fw_exception.write(items[0]+"	"+text+"\n")
						else:
							sb = sb.replace(",","")
							fw_svo.write(items[0]+"	"+sb+"	"+text+"\n")
					else:
						sb = sb.replace(",","")
						fw_svo.write(items[0]+"	"+sb+"	"+text+"\n")

				#Lynn add in the above
				else:
					sb = sb.replace(",","")
					fw_svo.write(items[0]+"	"+sb+"	"+text+"\n")
			else:
				sb = sb.replace(",","")
				fw_svo.write(items[0]+"	"+sb+"	"+text+"\n")
		elif svo2 =="":
			fw_svo.write(items[0]+"	"+svo+"	"+text+"\n")
		else:
			fw_svo.write(items[0]+"	"+svo+"|"+svo2+"	"+text+"\n")			
			
	fw_svo.close()
	fw_exception.close()
	
#some correct categories was replaced
#Postprocess results from extractSVO function in two results:
#1. refine results of the extractSVO function based on manual recognition of categories;
#2. categorized the undealed results from extractSVO function by simply word match.	
def postProcess(inputFile_results, inputFile_exception, inputFile_category, outputFile, outputFile_exception):	
	#Load category data
	f = open(inputFile_category, encoding = 'utf8') #Lynn
	lines = f.readlines()
	f.close()
	categoryList = []
	for index, row in enumerate(lines):
		categoryList.append(row.strip())
	categoryList = set(categoryList)
	
	fw = open(outputFile, "w", encoding = 'utf8') #Lynn
	fw_exception = open(outputFile_exception , "w", encoding = 'utf8') #Lynn
	
	count_preserve = 0
	count_refine = 0
	count_exception = 0
	
	#Refine results from extractSVO fuction
	f = open(inputFile_results, encoding = 'utf8') #Lynn
	lines = f.readlines()
	f.close()
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if len(items) == 3:
			items[1] = items[1].lower()
			items[1] = items[1].rstrip()
			if items[1][-1] == ".":
				items[1] = items[1][:-1]
			inCategory = 0
			if len(items[1].split("|")) == 2: #category : language|framework
				preserveTag = ""
				items1 = items[1].split("|")
				for item in categoryList:
					if item in items1[0].split(" "):
						inCategory = 1
						break
				
				if inCategory:
					count_preserve = count_preserve + 1
					preserveTag = items1[0]
				inCategory =0 
				for item in categoryList:
					if item in items1[1].split(" "):
						inCategory = 1
						break
					
				if inCategory and preserveTag == "":
					count_preserve = count_preserve + 1
					preserveTag = items1[1]
					fw.write("%s	%s	%s\n" % (items[0].strip(), preserveTag.strip(), items[2].strip()))
				elif inCategory and preserveTag != "":
					preserveTag = preserveTag +"|"+items1[1]
					fw.write("%s	%s	%s\n" % (items[0].strip(), preserveTag.strip(), items[2].strip()))
				elif preserveTag != "":
					fw.write("%s	%s	%s\n" % (items[0].strip(), preserveTag.strip(), items[2].strip()))
				else: #Lynn: changed the following to check sentence for category
					extractWord = ""
					for word in items[2].split():
						if word in categoryList:
							extractWord = word
							break
					if extractWord != "":
						count_refine = count_refine + 1
						fw.write("%s	%s	%s\n" % (items[0].strip(), extractWord.strip(), items[2].strip()))
					else:
						fw_exception.write(row)
				
			else: #category : 'language'
				for item in items[1].split(" "):
					if item in categoryList:
						inCategory = 1
						break
				
				if inCategory:
					count_preserve = count_preserve + 1
					fw.write(row)
				else:
					extractWord = ""
					for word in items[2].split():
						if word in categoryList:
							extractWord = word
							break
					if extractWord != "":
						count_refine = count_refine + 1
						fw.write("%s	%s	%s\n" % (items[0].strip(), extractWord.strip(), items[2].strip()))
					else:
						fw_exception.write(row)
					
		else:
			fw_exception.write(row)
		
					
	
	#Deal with exception results which are not processed by function extractSVO
	f = open(inputFile_exception, encoding = 'latin-1') #Lynn
	lines = f.readlines()
	f.close()
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		extractWord = ""
		if len(items)==2:
			for word in items[1].split():
				if word in categoryList:
					extractWord = word
					break
			if extractWord != "":
				count_exception  = count_exception + 1
				fw.write("%s	%s	%s\n" % (items[0].strip(), extractWord.strip(), items[1].strip()))
			else:
				fw_exception.write(row)
					
		else:
			fw_exception.write(row)
			
	fw.close()
	fw_exception.close()
	
	print("Preserve results: "+ str(count_preserve))
	print("Refine results: "+ str(count_refine))
	print("Exception results: "+ str(count_exception))

	
#Normalize categories by capitalization and something else	
def furtherPostProcess(inputFile, outputFileLong, outputFile):
	f = open(inputFile, encoding = 'utf8') #Lynn
	lines = f.readlines()
	f.close()
	
	transformDic = {"tools":"tool", "libraries": "library", "functions": "function", "extensions": "extension", "bindings":"binding", "classes": "class", "systems": "system"}
	table = str.maketrans("","") #Lynn
	
	special_list = ['sdk','extension','api','ide','directive','exception','sdk','plugin'] #Lynn added. Contains high frenquency words in tags themselves

	
	fw = open(outputFileLong, "w", encoding = 'utf8') #Lynn
	f = open(outputFile, "w", encoding = 'utf8') #Lynn
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if len(items) == 3:
			found = 0
			#Lynn: check no special_list in tags:
			for term in special_list:
				if term in items[0]:
					items[1] = term
					found = 1
					fw.write(items[0]+'\t'+items[1]+'\t'+items[2]+'\n')
					f.write(items[0]+'\t'+items[1]+'\t'+items[2]+'\n')
					break

			if not found: 
				
				#General process
				items[1] = items[1].lower()
				items[1] = items[1].rstrip()
				if items[1][-1] == ".":
					items[1] = items[1][:-1]
				
				temp=""
				for item in items[1].split(" "):
					if item in transformDic:
						item = transformDic[item]		#From plural to singular
					temp += item + " "
				items[1] = temp
				
				#Specific transformation
				if "system" in items[1]:
					print(items[1])
					if "operating system" in items[2].lower() or "os" in items[2].lower():
						items[1] = "os"
					if "database management system" in items[2].lower():
						items[1] = "dbms"
				if "type" in items[1]: #Lynn add in dataType
					if "data type" in items[2].lower():
						items[1] = "dataType"
				if "data" in items[1]: #Lynn add in dataType
					if "data type" in items[2].lower():
						items[1] = "dataType"
				if "environment" in items[1]:
					if "development environment" in items[2].lower() or "programming environment" in items[2].lower():
						items[1] = "ide"
				if "machine" in items[1]:
					if "virtual machine" in items[2].lower():
						items[1] = "vm"
				if "replacement" in items[1]: #Lynn add in
					if items[1].strip() != 'replacement':
						temp = items[1].replace('replacement','')
						items[1] = temp
				
				
				fw.write("%s	%s	%s\n" % (items[0], items[1], items[2]))
				if "|" in items[1]:
					items1 = items[1].split("|")
					
					f.write("%s	%s	%s\n" % (items[0], items1[0].rsplit(None, 1)[-1]+"|"+items1[1].rsplit(None, 1)[-1], items[2]))
				else:
					print(items[0])
					print(items[1])
					print(items[2])
					f.write("%s	%s	%s\n" % (items[0], items[1].rsplit(None, 1)[-1], items[2]))
	fw.close()
	f.close()				

#Analyze the category from the extractSVO/postProcess function to clean the results
def categoryAnalysis(inputFile, outputFile):
	f = open(inputFile, encoding = 'utf8') #Lynn
	lines = f.readlines()
	f.close()
	
	categoryDic = {}
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if len(items) == 3:
			if "|" in items[1]:
				for items1 in items[1].split("|"):
					if items1 in categoryDic:
						categoryDic[items1] = categoryDic[items1] + 1
					else:
						categoryDic[items1] = 1
			else:
				if items[1] in categoryDic:
					categoryDic[items[1]] = categoryDic[items[1]] + 1
				else:
					categoryDic[items[1]] = 1
	
	fw = open(outputFile, "w", encoding = 'utf8') #Lynn
	for key in categoryDic:
		fw.write(key+"	"+str(categoryDic[key])+"\n")
	fw.close()



#Integrate information such as tag name, frequency, category and the first sentence of its tagWiki
#for better view and further manual check
def tagsInfo(inputFile_raw, inputFile_category, inputFile_exception, outputFile):
	#Load categorized tags
	f = open(inputFile_category, encoding = 'utf8') #Lynn
	lines = f.readlines()
	f.close()
	categoryDic = {}
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if len(items) == 3:
			categoryDic[items[0]] = items[1] + "	"+ items[2]
	
	print(str(len(categoryDic)))
	
	#Load uncategorized tags
	f = open(inputFile_exception, encoding = 'utf8') #Lynn
	lines = f.readlines()
	f.close()
	uncategoryDic = {}
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		uncategoryDic[items[0]] = items[-1]
	
	print(str(len(uncategoryDic)))
	
	f = open(inputFile_raw, encoding = 'utf8') #Lynn
	lines = f.readlines()
	f.close()
	
	tagDic = {}
	for index, row in enumerate(lines):
		for item in row.strip().split(","):
			if item in tagDic:
				tagDic[item] = tagDic[item] + 1
			else:
				tagDic[item] = 1
	
	print("number of tags: "+ str(len(tagDic)))
	
	 
	fw = open(outputFile, "w", encoding = 'utf8') #Lynn
	for key in tagDic:
		if key in categoryDic:
			fw.write("%s	%s	%s\n" % ( str(tagDic[key]), key, categoryDic[key]))
		elif key in uncategoryDic:
			fw.write("%s	%s	 	%s\n" % (str(tagDic[key]), key, uncategoryDic[key]))
		else:
			fw.write("%s	%s\n" % (str(tagDic[key]), key))
			
	fw.close()		

#Extract 100 samples randomly for manual accuracy check
def verifyAccuracy(inputFile, outputFile):
	f = open(inputFile, encoding = 'utf8') #Lynn
	lines = f.readlines()
	f.close()
	
	popularCatDic = {}
	i=0;
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if len(items) == 4 and items[2]!=" " and int(items[0])>100:		#usage >100
			popularCatDic[i] =items[0] +"	"+items[1]+"	"+ items[2] + "	"+ items[3]
			i+=1
			
	fw = open(outputFile, "w", encoding = 'utf8') #Lynn
	for j in range(100):
		ran = randint(0,i)
		fw.write("%s\n" % (popularCatDic[ran]))
	fw.close()		

#Lynn add this function to perform word match in whole tagwiki
def categoryExceptionProcess(f_exception2,f,f_manualCategory,f_rescued, f_failed_rescued):

	f_exp = open(f_exception2, encoding = 'utf8') #Lynn
	lines_exp = f_exp.readlines()
	f_exp.close()

	f_wiki = open(f, encoding = 'utf8') #Lynn
	lines_wiki = f_wiki.readlines()
	f_wiki.close()

	f_cate = open(f_manualCategory, encoding = 'utf8') #Lynn
	lines_cate = f_cate.readlines()
	f_cate.close()	

	#extract tags with no category from tagcategory_exception file
	tags = []
	for line in lines_exp:
		items = line.strip().split('\t')
		tags.append(items[0])

	#import manual category list
	categories = []
	for line in lines_cate:
		items = line.strip()
		categories.append(items)

	print(categories)

	special_list = ['sdk','extension','api','ide','directive','exception','sdk','plugin'] #Lynn added. Contains high frenquency words in tags themselves


	fw = open(f_rescued,'w',encoding = 'utf8')
	fw_failed = open(f_failed_rescued, 'w',encoding = 'utf8')

	for line in lines_wiki:
		items = line.strip().split('\t')
		if items[0] in tags:
			#search tagwiki
			found = 0

			#Lynn: check no special_list in tags:
			for term in special_list:
				if term in items[0]:
					category = term
					found = 1
					fw.write(items[0]+'\t'+category+'\t'+items[1]+'\n')
					break
					
			if not found:
				print(items[0])
				for category in categories:
					print(category)
					if category in items[1]:
						print(category)
						fw.write(items[0]+'\t'+category+'\t'+items[1]+'\n')
						found = 1
						break
				if not found:
					fw_failed.write(line)

	fw.close()
	fw_failed.close()


if __name__ == '__main__':

	f = "tagWiki.txt"								#Input
	f_preprocess = 'tagWiki_preprocess.txt'
	f_preprocess2 = 'tagWiki_preprocess2.txt'
	f_allTags = "allTags_test.txt"						#Input
	f_version = "tag_version_manual.txt"			#Input
	f_pos = "pos_nltk.txt"
	f_svo = "svo_nltk.txt"
	f_exception = "svo_exception_nltk.txt"
	f_analysis = "analysis.txt"
	f_manualCategory = "allCategory_test.txt"			#Input
	f_tagCategory = "tagCategory_nltk.txt"
	f_refineLong = "tagCategory_refineLong_nltk.txt"
	f_refine = "tagCategory_refine_nltk.txt"
	f_exception2 = "tagCategory_exception_nltk.txt"
	f_tagInfo = "tagInfo.txt"
	f_tagAccuracy = "tagAccuracy4.txt"
	#f_tagRevise = "tags_revise.csv"					#Input
	f_rescued = "tagCategory_rescued_nltk.txt"
	f_failed_rescued = "tagCategory_failed_rescued_nltk.txt"

	try:
	
		#preprocess(f, f_preprocess2)
		#extractPOS(f_preprocess2,f_allTags, f_version,f_pos)
		#extractSVO(f_preprocess2, f_pos, f_svo, f_exception)
		#postProcess(f_svo, f_exception, f_manualCategory, f_tagCategory, f_exception2)	
		#furtherPostProcess(f_tagCategory, f_refineLong,f_refine)
		#categoryAnalysis(f_refine, f_analysis)
		#tagsInfo(f_tagRevise, f_refine, f_exception2, f_tagInfo)
		#verifyAccacuracy(f_tagInfo, f_tagAccuracy)
		categoryExceptionProcess(f_exception2,f,f_manualCategory,f_rescued, f_failed_rescued) #Lynn add this function to perform word match in whole tagwiki
		
	except Exception as e :
		print('There are exceptions')
		print(e)
		raise