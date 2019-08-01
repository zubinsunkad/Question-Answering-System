from nltk import pos_tag,word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn,stopwords

class PreprocessQuestion:
    def __init__(self, ques, useLemmatizer = False, useSynonyms = False, removeStopwords = False):
        self.ques = ques
        self.useLemmatizer = useLemmatizer
        self.useSynonyms = useSynonyms
        self.removeStopwords = removeStopwords
        self.stopWords = stopwords.words("english")
        self.lemmatizer = lambda k : k.lower()
        if self.useLemmatizer:
            lm = WordNetLemmatizer()
            #self.lemmatizer = lm.lemmatizer
        self.qType = self.determineQuestionType(ques)
        self.searchQuery = self.buildSearchQuery(ques)
        self.qVector = self.getQueryVector(self.searchQuery)
        self.result_type = self.determineAnswerType(ques)
    
    def determineAnswerType(self, ques):
        my_question = ['WP','WDT','WRB']
        qPOS = pos_tag(word_tokenize(ques))
        qTag = None

        for token in qPOS:
            if token[1] in my_question:
                qTag = token[0].lower()
                break


        if qTag == "who":
            return "PERSON/ORGANIZATION"
        elif qTag == "where":
            return "LOCATION"
        elif qTag == "when":
            return "DATE"

    def determineQuestionType(self, ques):
        my_question = ['WP','WRB']
        qPOS = pos_tag(word_tokenize(ques))
        qTags = []
        for token in qPOS:
            if token[1] in my_question:
                qTags.append(token[1])
        qType = ''
        if(len(qTags)>1):
            qType = 'complex'
        elif(len(qTags) == 1):
            qType = qTags[0]
        else:
            qType = "None"
        return qType

    def getQueryVector(self, searchQuery):
        vector = {}
        for token in searchQuery:
            if self.removeStopwords:
                if token in self.stopWords:
                    continue
            token = self.lemmatizer(token)
            if token in vector.keys():
                vector[token] += 1
            else:
                vector[token] = 1
        return vector

    def buildSearchQuery(self, ques):
        qPOS = pos_tag(word_tokenize(ques))
        searchQuery = []
        my_question = ['WP','WRB']
        for tag in qPOS:
            if tag[1] in my_question:
                continue
            else:
                searchQuery.append(tag[0])
                if(self.useSynonyms):
                    syn = self.getSynonyms(tag[0])
                    if(len(syn) > 0):
                        searchQuery.extend(syn)
        return searchQuery 

    def joinChunk(self,ques):
        my_chunk = []
        result_token = word_tokenize(ques)
        nc = pos_tag(result_token)

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
                    my_chunk.append((my_ent["pos"]," ".join(my_ent["chunk"])))
                    my_ent = {"pos":pos,"chunk":[token]}
                    prevPos = pos
        if not len(my_ent["chunk"]) == 0:
            my_chunk.append((my_ent["pos"]," ".join(my_ent["chunk"])))
        return my_chunk

    def getSynonyms(word):
        hypo=hyper=mero=holo=synonyms=word_bag=[]
        syns=wn.synsets(word)[0]
        hypernyms=syns.hypernyms()
        hyponyms=syns.hyponyms()
        meronyms=syns.part_meronyms()
        holonyms=syns.part_holonyms()
        
        for i in range(len(wn.synsets(word))):
            synonyms.append(wn.synsets(word)[i].name().split(".")[0])
        for i in range(len(hyponyms)):
            hypo.append(hyponyms[i].name().split(".")[0])
        for i in range(len(hypernyms)):
            hyper.append(hypernyms[i].name().split(".")[0])
        for i in range(len(holonyms)):
            holo.append(holonyms[i].name().split(".")[0])
        for i in range(len(meronyms)):
            mero.append(meronyms[i].name().split(".")[0])
        word_bag=set(synonyms+hypo+hyper+holo+mero)
        return(list(set(word_bag)))

    def __repr__(self):
        message = "Q: " + self.ques + "\n"
        message += "QType: " + self.qType + "\n"
        message += "QVector: " + str(self.qVector) + "\n"
        return message