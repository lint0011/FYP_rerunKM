# -*- coding: utf-8 -*-
#Author: Teong Ke Ming
#Function
'''
This file is used to extract the relation of tags in Stack Overflow based on the first sentence in the tagWiki.
It achieves the goal in several steps:
1. Extract relation by looking for keywords
2. Refine the results in step 1 through manual recognition.
3. Extract relation which is not found in step 2 by using noun category from the result in tagCategory
4. Refine the results in step 3 through manual recognition.
5. Combine result in step 2 and 4 then output in specified format for graph visualization
'''
import re
import networkx as nx

#Extract relation by looking for keywords such as "for", "of" after its category
def extractRelation(inputFile_cat,inputFile, outputFile, outputFile_exception):
	f = open(inputFile)
	item = f.readlines()
	f.close()
	
	tagList = []
	for index, row in enumerate(item):
		items = row.strip().split("	")
		if len(items) == 3:
			tagList.append(items[0])
	
	f = open(inputFile_cat)
	lines = f.readlines()
	f.close()
	
	fw = open(outputFile, "w")
	fw_exception = open(outputFile_exception, "w")
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if items[0] in tagList:
			#Process the sentence for word matching
			sentence = items[2].replace(",","")
			sentence = sentence.replace("\"","")
			
			if "(" in sentence:
				sentence = re.sub(r" \(.+?\)", "", sentence)          
			if "[" in sentence:
				sentence = re.sub(r" \[.+?\]", "", sentence)
			if "<" in sentence:
				sentence = re.sub(r" \<.+?\>", "", sentence)
			if sentence[-1] ==".":
				sentence = sentence[:-1]
		
			sentence = sentence.lower()
			
			if "os x" in sentence:
				sentence = sentence.replace("os x","osx")
			
			sentence = sentence.split()
			
			if len(items[1].split("|")) == 2:
				cat = items[1].replace("|","and ")
			else:
				cat = items[1].strip()
			if cat[-1] ==".":
				cat = cat[:-1]
			cat = cat.lower()
			cat = cat.split()
			
			try:
				if len(cat)==1 or sentence.index(cat[-1]) == (sentence.index(cat[-2])+1) :
					index = sentence.index(cat[-1])
					if len(sentence)> (index+2) and (sentence[index+1] =="for" or sentence[index+1] =="of"):
						if len(sentence)> (index+3) and sentence[index+2] =="the":
							fw.write("%s	%s	%s	%s\n" % (items[0] , sentence[index+3], items[1], items[2]))
						else:
							fw.write("%s	%s	%s	%s\n" % (items[0] , sentence[index+2], items[1], items[2]))
					else:
						fw_exception.write(row)
				else:
					fw_exception.write(row)
			except ValueError:
				fw_exception.write(row)
		else:
			fw_exception.write(row)

	fw.close()
	fw_exception.close()
	
#Refine results based on manual recognition of relations;
def manualRelation(inputFile,inputFile_category,inputFile_raw,outputFile,outputFile_exception):
	#Load categorized tags
	f = open(inputFile_category)
	cat = [line.rstrip('\n') for line in f]
	f.close()
	
	f = open(inputFile_raw)
	lines_raw = f.readlines()
	f.close()
	
	tagA = []
	tagDic = {}
	for index, row in enumerate(lines_raw):
		item = row.strip().split(",")
		if item[0] not in tagA:
			tagDic[item[0]] = item[1]
			tagA.append(item[0])
			
	f = open(inputFile)
	lines = f.readlines()
	f.close()
	
	#Extract recognized relation
	fw = open(outputFile, "w")
	fw_exception = open(outputFile_exception, "w")
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if items[1] in tagA:
			items[1] = tagDic[items[1]]
			row = items[0] +"	"+items[1]+"	"+items[2] +"	"+items[3]+"\n"
		if items[1] in cat:
			fw.write(row)
		else:
			fw_exception.write(row)
			
	fw.close()
	fw_exception.close()
			
#Extract relation from undealed results from extractRelation function
def furtherExtractRelation(inputFile,inputFile2, outputFile, outputFile_exception):
	#Load categorized tags
	f = open(inputFile)
	lines = f.readlines()
	f.close()
	categoryDic = {}
	sentenceDic = {}
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if len(items) == 3:
			categoryDic[items[0]] = items[1].lower()
			sentenceDic[items[0]] = items[2]
	
	f = open(inputFile2)
	lines = f.readlines()
	f.close()
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if len(items) == 4:
			categoryDic[items[0]] = items[2].lower()
			sentenceDic[items[0]] = items[3]
	
	#Compare nouns in category with tags e.g., A JavaScript port of the Processing language. Category: JavaScript port
	fw = open(outputFile, "w")
	fw_exception = open(outputFile_exception, "w")
	for item in categoryDic:
		written = 0
		cat = categoryDic[item]
		if len(cat.split("|")) == 2:
			for cat2 in cat.split("|"):
				cat2split = cat2.split()
				if len(cat2split) > 1:
					if cat2split[0] in categoryDic:
						fw.write("%s	%s	%s	%s\n" % (item , cat2split[0], cat, sentenceDic[item]))
						written = 1
						break
		else:
			catsplit =cat.split()
			if len(catsplit) > 1:
				if catsplit[0] in categoryDic:
					written = 1
					fw.write("%s	%s	%s	%s\n" % (item , catsplit[0], cat, sentenceDic[item]))
		
		if written ==0:
			fw_exception.write("%s	%s	%s\n" % (item , cat, sentenceDic[item]))
			
	fw.close()
	fw_exception.close()

#Analysis the category for each relation
def relInfo(inputFile,inputFile2,outputFile):
	f = open(inputFile)
	lines = f.readlines()
	relTag = {}
	relTagP = []
	tagline  = lines
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if len(items) == 4:
			relTagP.append((items[0],items[1]))
			rel = items[2].rsplit(None, 1)[-1]
			if rel not in relTag:
				relTag[rel] = 1
			else:
				relTag[rel] = relTag[rel] +1
	f.close()
	
	f = open(inputFile2)
	lines2 = f.readlines()
	tagline = tagline + lines2
	for index, row in enumerate(lines2):
		items2 = row.strip().split("	")
		if len(items2) == 4:
			relTagP.append((items2[0],items2[1]))
			rel = items2[2].rsplit(None, 1)[-1]
			if rel not in relTag:
				relTag[rel] = 1
			else:
				relTag[rel] = relTag[rel] +1
	f.close()

	fw = open(outputFile, "w")
	for relation in relTag:
		fw.write("%s,%d\n" % (relation,relTag[relation])) 
	
	fw.close()	

#Format the relations for graph visualization
def graphCSV(inputFile_cat,inputFile,inputFile2,outputFile):

	
	f = open(inputFile)
	lines = f.readlines()
	relTag = []
	relTagP = []
	tagline  = lines
	for index, row in enumerate(lines):
		items = row.strip().split("	")
		if len(items) == 4:
			relTagP.append((items[0],items[1]))
			rel = items[2].rsplit(None, 1)[-1]
			if rel not in relTag:
				relTag.append(rel)
	f.close()
	
	f = open(inputFile2)
	lines2 = f.readlines()
	tagline = tagline + lines2
	for index, row in enumerate(lines2):
		items2 = row.strip().split("	")
		if len(items2) == 4:
			relTagP.append((items2[0],items2[1]))
			rel = items2[2].rsplit(None, 1)[-1]
			if rel not in relTag:
				relTag.append(rel)
	f.close()
	
	G = nx.DiGraph()
	G.add_edges_from(relTagP)
	edgenum = nx.degree(G)
	
	relNum = ["others","library","package","tool","class","implementation","component","extension","engine","system","client","interface","server","language","gem","app","platform"]
	relDic = {"frameworks":"library", "framework": "library", "libraries": "library", "apis":"library", "api":"library", "plugins": "library", "plug-in": "library", "plug-ins":"library",
	"plugin":"library","tools": "tool", "toolkit": "tool", "packages": "package", "classes": "class","functions":"class","function":"class","functionality":"class","feature":"class","features":"class",
	"modules":"class","module":"class","wrappers":"class","wrapper":"class","adapter":"class","components":"component","extensions":"extension","engines":"engine","systems":"system","interfaces":"interface",
	"gui":"interface","application":"app","applications":"app","apps":"app","platforms":"platform","ide":"platform"}
	
	parentcat={}
	f = open(inputFile_cat)
	parentline = f.readlines()
	for index, row in enumerate(parentline):
		items = row.strip().split("	")
		parentcat[items[0]] = items[1].rsplit(None, 1)[-1]
	f.close()

	#dest: parent tag, edgestag: number of edges for tag, edgesdest: number of edges for parent tag
	fw = open(outputFile, "w")
	fw.write("tag,dest,rel,relvalue,prel,prelvalue,edgestag,edgesdest\n")
	for index, row in enumerate(tagline):
		items = row.strip().split("	")
		if len(items) == 4:
			rel = items[2].rsplit(None, 1)[-1]
			rel = rel.replace("|","")
			rel = rel.replace(".","")
			rel = rel.lower()
			grprel = rel
			if rel in relDic:
				grprel = relDic[rel]
			if grprel not in relNum:	
				grprel = "others"
			if items[1] in parentcat:
				prel = parentcat[items[1]]
				prel = prel.replace("|","")
				prel = prel.replace(".","")
				prel = prel.lower()
				pgrprel = prel
				if prel in relDic:
					pgrprel = relDic[prel]
				if pgrprel not in relNum:	
					pgrprel = "others"
			else:
				pgrprel = "others"
			fw.write("%s,%s,%s,%d,%s,%d,%d,%d\n" % (items[0] , items[1],grprel,relNum.index(grprel),pgrprel,relNum.index(pgrprel),edgenum[items[0]],edgenum[items[1]]))
	
	fw.close()	
	
if __name__ == '__main__':
	
	f_tagCategory = "tagCategory.txt"					
	f_refineLong = "tagCategory_refineLong.txt"
	f_rel = "rel.txt"
	f_relException = "rel_exception.txt"
	f_relf = "relf.txt"
	f_relExceptionf = "rel_exceptionf.txt"
	f_mCategory = "relCategory.txt"						#Input
	f_mrel = "mrel.txt"
	f_mrelException = "mrel_exception.txt"
	f_mrel2 = "mrel2.txt"
	f_mrelException2 = "mrel_exception2.txt"
	f_relInfo = "relInfo.csv"
	f_graph = "graph.csv"
	f_acronym = "acronym.csv"							#Input
	
	try:
		#extractRelation(f_tagCategory, f_refineLong, f_relf,f_relExceptionf)
		#manualRelation(f_relf,f_mCategory,f_acronym,f_mrel,f_mrelException)
		#furtherExtractRelation(f_relExceptionf,f_mrelException, f_rel,f_relException)
		#manualRelation(f_rel,f_mCategory,f_acronym,f_mrel2,f_mrelException2)
		#relInfo(f_mrel,f_mrel2,f_relInfo)
		graphCSV(f_refineLong,f_mrel,f_mrel2,f_graph)
		
	except Exception, e :
		print 'There are exceptions'
		print e
		raise