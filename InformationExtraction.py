from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import json
import math
import spacy
from nltk.tree import Tree
from nltk import pos_tag,ne_chunk
from Date_Extraction import extractDate

class InformationExtraction:
    def __init__(self,myParas,removeStopWord = False,useLemmatizer = False):
        self.id_freq = {}               
        self.paraInfo = {}     
        self.myParas = myParas
        self.totalParas = len(myParas)
        self.stopwords = stopwords.words('english')
        self.removeStopWord = removeStopWord
        self.useLemmatizer = useLemmatizer
        self.vData = None
        self.lemmatizer = lambda k : k.lower()
        if self.useLemmatizer:
            lm = WordNetLemmatizer()

        self.computeTFIDF()
        

    def TermFrequencyCount(self,para):
        sents = sent_tokenize(para)
        word_dict = {}
        for s in sents:
            for w in word_tokenize(s):
                if self.removeStopWord == True:
                    if w.lower() in self.stopwords:
                        #Ignore stopwords
                        continue

                if w in word_dict.keys():
                    word_dict[w] += 1
                else:
                    word_dict[w] = 1
        return word_dict
    

    def computeTFIDF(self):
        # Compute Term Frequency
        self.paraInfo = {}
        for myIndex in range(0,len(self.myParas)):
            my_word_count = self.TermFrequencyCount(self.myParas[myIndex])
            self.paraInfo[myIndex] = {}
            self.paraInfo[myIndex]['wF'] = my_word_count
        
        word_count = {}
        for myIndex in range(0,len(self.paraInfo)):
            for wrd in self.paraInfo[myIndex]['wF'].keys():
                if wrd in word_count.keys():
                    word_count[wrd] += 1
                else:
                    word_count[wrd] = 1
        
        self.id_freq = {}
        for wrd in word_count:
            self.id_freq[wrd] = math.log((self.totalParas+1)/word_count[wrd])
        
        #Compute Paragraph Vector
        for myIndex in range(0,len(self.paraInfo)):
            self.paraInfo[myIndex]['vector'] = {}
            for wrd in self.paraInfo[myIndex]['wF'].keys():
                self.paraInfo[myIndex]['vector'][wrd] = self.paraInfo[myIndex]['wF'][wrd] * self.id_freq[wrd]
    
    def query(self,pQ):
        rel_para = self.getSimilarParagraph(pQ.qVector)
        my_sentences = []
        for my_tuple in rel_para:
            if my_tuple != None:
                p2 = self.myParas[my_tuple[0]]
                my_sentences.extend(sent_tokenize(p2))
        
        
        if len(my_sentences) == 0:
            return "Unable to find result answer"

        rel_sents = self.getMostRelevantSentences(my_sentences,pQ,1)
        result_type = pQ.result_type
        result = rel_sents[0][0]
        ne = self.NamedEntity([s[0] for s in rel_sents])
        
        if result_type == "PERSON/ORGANIZATION":
            ne = self.NamedEntity([s[0] for s in rel_sents])
            for my_ent in ne:
                if my_ent[0] == "PERSON":
                    result = my_ent[1]
                    result_token = [w for w in word_tokenize(result.lower())]
                    qTokens = [w for w in word_tokenize(pQ.ques.lower())]
                    
                    if [(a in qTokens) for a in result_token].count(True) >= 1:
                        continue
                    break
                elif my_ent[0] == "ORGANIZATION":
                    result = my_ent[1]
                    result_token = [w for w in word_tokenize(result.lower())]
                    
                    qTokens = [w for w in word_tokenize(pQ.ques.lower())]
                    if [(a in qTokens) for a in result_token].count(True) >= 1:
                        continue
                    break
        elif result_type == "LOCATION":
            ne = self.NamedEntity([s[0] for s in rel_sents])
            for my_ent in ne:
                if my_ent[0] == "GPE":
                    result = my_ent[1]
                    result_token = [w for w in word_tokenize(result.lower())]
                    qTokens = [w for w in word_tokenize(pQ.ques.lower())]
                    
                    if [(a in qTokens) for a in result_token].count(True) >= 1:
                        continue
        elif result_type == "DATE":
            allDates = []
            for s in rel_sents:
                allDates.extend(extractDate(s[0]))
            if len(allDates)>0:
                result = allDates[0]
        elif result_type in ["NN","NNP"]:
            ne = self.joinChunk([s[0] for s in rel_sents])
            for my_ent in ne:
                if result_type == "NN":
                    if my_ent[0] == "NN" or my_ent[0] == "NNS":
                        result = my_ent[1]
                        result_token = [w for w in word_tokenize(result.lower())]
                        qTokens = [w for w in word_tokenize(pQ.ques.lower())]
                        
                        if [(a in qTokens) for a in result_token].count(True) >= 1:
                            continue
                        break
                elif result_type == "NNP":
                    if my_ent[0] == "NNP" or my_ent[0] == "NNPS":
                        result = my_ent[1]
                        result_token = [w for w in word_tokenize(result.lower())]
                        qTokens = [w for w in word_tokenize(pQ.ques.lower())]
                        
                        if [(a in qTokens) for a in result_token].count(True) >= 1:
                            continue
                        break
        return (result,rel_sents[0][0])
 
    def getSimilarParagraph(self,query_vec):    
        query_vec_dis = 0
        for wrd in query_vec.keys():
            if wrd in self.id_freq.keys():
                query_vec_dis += math.pow(query_vec[wrd]*self.id_freq[wrd],2)
        query_vec_dis = math.pow(query_vec_dis,0.5)
        if query_vec_dis == 0:
            return [None]
        rank_list = []
        for myIndex in range(0,len(self.paraInfo)):
            similarity = self.computeCosineSimilarity(self.paraInfo[myIndex], query_vec, query_vec_dis)
            rank_list.append((myIndex,similarity))
        
        return sorted(rank_list,key=lambda x: (x[1],x[0]), reverse=True)[:3]

    def computeCosineSimilarity(self, pInfo, query_vec, queryDistance):
        
        pVectorDistance = 0
        for wrd in pInfo['wF'].keys():
            pVectorDistance += math.pow(pInfo['wF'][wrd]*self.id_freq[wrd],2)
        pVectorDistance = math.pow(pVectorDistance,0.5)
        if(pVectorDistance == 0):
            return 0

        # Computing dot product
        dotProduct = 0
        for wrd in query_vec.keys():
            if wrd in pInfo['wF']:
                q = query_vec[wrd]
                w = pInfo['wF'][wrd]
                id_freq = self.id_freq[wrd]
                dotProduct += q*w*id_freq*id_freq
        
        similarity = dotProduct / (pVectorDistance * queryDistance)
        return similarity

    def getMostRelevantSentences(self, my_sentences, pQ, nGram=4):
        rel_sents = []
        for sent in my_sentences:
            similarity = 0
            if(len(word_tokenize(pQ.ques))>nGram+1):
                similarity = self.Ngram_sim(pQ.ques,sent,nGram)
            else:
                similarity = self.sim_sentence(pQ.qVector, sent)
            rel_sents.append((sent,similarity))
        
        return sorted(rel_sents,key=lambda x:(x[1],x[0]),reverse=True)
    

    def Ngram_sim(self, question, sentence,nGram):

        getToken = lambda question:[ w.lower() for w in word_tokenize(question) ]
        getNGram = lambda tokens,n:[ " ".join([tokens[myIndex+i] for i in range(0,n)]) for myIndex in range(0,len(tokens)-n+1)]
        qToken = getToken(question)
        sToken = getToken(sentence)

        if(len(qToken) > nGram):
            q3gram = set(getNGram(qToken,nGram))
            s3gram = set(getNGram(sToken,nGram))
            if(len(s3gram) < nGram):
                return 0
            qLen = len(q3gram)
            sLen = len(s3gram)
            similarity = len(q3gram.intersection(s3gram)) / len(q3gram.union(s3gram))
            return similarity
        else:
            return 0
    
    def sim_sentence(self, query_vec, sentence):
        sentToken = word_tokenize(sentence)
        similarity = 0
        for wrd in query_vec.keys():
            if wrd in sentToken:
                similarity += 1
        return similarity/(len(sentToken)*len(query_vec.keys()))

    def NamedEntity(self,results):
        chunks = []
        for result in results:
            answerToken = word_tokenize(result)
            nc = ne_chunk(pos_tag(answerToken))
            my_ent = {"label":None,"chunk":[]}
            for c_node in nc:
                if(type(c_node) == Tree):
                    if(my_ent["label"] == None):
                        my_ent["label"] = c_node.label()
                    my_ent["chunk"].extend([ token for (token,pos) in c_node.leaves()])
                else:
                    (token,pos) = c_node
                    if pos == "NNP":
                        my_ent["chunk"].append(token)
                    else:
                        if not len(my_ent["chunk"]) == 0:
                            chunks.append((my_ent["label"]," ".join(my_ent["chunk"])))
                            my_ent = {"label":None,"chunk":[]}
            if not len(my_ent["chunk"]) == 0:
                chunks.append((my_ent["label"]," ".join(my_ent["chunk"])))
           
        return chunks

    def joinChunk(self,results):
        chunks = []
        for result in results:
            answerToken = word_tokenize(result)
            if(len(answerToken)==0):
                continue
            nc = pos_tag(answerToken)
            
            prevPos = nc[0][1]
            my_ent = {"pos":prevPos,"chunk":[]}
            for c_node in nc:
                (token,pos) = c_node
                if pos == prevPos:
                    prevPos = pos       
                    my_ent["chunk"].append(token)
                elif prevPos in ["DT","JJ"]:
                    prevPos = pos
                    my_ent["pos"] = pos
                    my_ent["chunk"].append(token)
                else:
                    if not len(my_ent["chunk"]) == 0:
                        chunks.append((my_ent["pos"]," ".join(my_ent["chunk"])))
                        my_ent = {"pos":pos,"chunk":[token]}
                        prevPos = pos
            if not len(my_ent["chunk"]) == 0:
                chunks.append((my_ent["pos"]," ".join(my_ent["chunk"])))
        return chunks
    
    def getqRev(self, pq):
        if self.vData == None:
            
            self.vData = json.loads(open("validatedata.py","r").readline())
        revMatrix = []
        for t in self.vData:
            sent = t["q"]
            revMatrix.append((t["a"],self.sim_sentence(pq.qVector,sent)))
        return sorted(revMatrix,key=lambda x:(x[1],x[0]),reverse=True)[0][0]
        
    def __repr__(self):
        message = "Total Paras " + str(self.totalParas) + "\n"
        message += "Total Unique Word " + str(len(self.id_freq)) + "\n"
        message += str(self.getMostSignificantWords())
        return message