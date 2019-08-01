import re
import sys
import json
from InformationExtraction import InformationExtraction as DRModel
from PreprocessQuestion import PreprocessQuestion as PQ
import os



myPath='Data/'
myPara = []
para_dict={}
for file in os.listdir(myPath):
	try:
		myDataset = open(myPath+file,"r",encoding='utf-8-sig')
	except FileNotFoundError:
		print("Oops! Unable to locate \"" + myPath + file + "\"")
		exit()
	for para in myDataset.readlines():
		if(len(para.strip()) > 0):
			myPara.append(para.strip())
			para_dict[file]=myPara


DRModel = DRModel(myPara,True,False)
test_path='questions.txt'
test = open(test_path,"r",encoding='utf-8-sig')

ques_array=[]
f= open ('data.txt','w')
for line in test.readlines():
		if(len(line.strip()) > 0):
			ques_array.append(line.strip())
			line=line.strip()
			pq = PQ(line,False,False,True)
			answer,sentence =DRModel.query(pq)
			display_dict={"Input question":line,"Exact Answer":answer,"Supporting sentence":sentence,"Supporting Wikipedia Document":file}
			json.dump(display_dict,f)