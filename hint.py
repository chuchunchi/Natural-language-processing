#Author: 紀竺均
#Student ID: 109550027
#HW ID: hw1
import pandas as pd
import spacy
from tqdm import trange
nlp=spacy.load("en_core_web_sm")
'''
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
'''
data_path="dataset.csv"
data=pd.read_csv(data_path,header=None,names=['編號','句子','主詞','動詞','受詞'])

deptag = {"subj":["nsubj", "nsubjpass", "csubj",
            "csubjpass", "agent", "expl"], "obj": ["dobj", "dative", "attr", "oprd"]}
def subj_deptree(verb):
    head = verb.head
    while head.head != head:
        head = head.head
        if head.pos_ == "VERB":
            subs = [t for t in head.lefts if t.dep_ in deptag["subj"]]
            if len(subs) != 0:
                tmp = []
                for sub in subs:
                    tmp.extend(sub.conjuncts)
                subs.extend(tmp)
                return subs
            elif head.head != head:
                continue
            else:
                break
        elif head.pos_ == "NOUN" or head.pos_ == "PRON" or head.pos_ == "PROPN":
            return [head]
    return []

def obj_deptree(verb):
    head = verb.head
    while head.head != head:
        head = head.head
        if head.pos_ == "VERB":
            subs = [t for t in head.rights if t.dep_ in deptag["obj"]]
            if len(subs) != 0:
                tmp = []
                for sub in subs:
                    tmp.extend(sub.conjuncts)
                subs.extend(tmp)
                return subs
            elif head.head != head:
                continue
            else:
                break
        elif head.pos_ == "NOUN" or head.pos_ == "PRON" or head.pos_ == "PROPN":
            return [head]
    return []
def get_sth(sen,label):
    list=[]
    sen=nlp(sen)
    for token in sen:
        if token.pos_==label:
            list.append(token.text)
            return list


#Try to improve this function
def get_subj(sen,head_idx,tag):
    sen=nlp(sen)
    sublist = []
    for token in sen[0:head_idx]:
        if token.dep_ in deptag[tag] and token.pos_ != "DET" and not token.is_punct and token.text not in s:
            sublist.append(token)
    if(len(sublist)==0):
        subj_deptree(sen[head_idx])
    return sublist

def get_obj(sen,head_idx,tag):
    sen=nlp(sen)
    objlist = []
    for token in sen[head_idx+1:]:
        if token.dep_ in deptag[tag] and not token.is_punct and token.text not in o:
            '''subtree=list(token.subtree)
            start=subtree[0].i
            end=subtree[-1].i+1
            return sen[start:end]'''
            objlist.append(token)
        if token.pos_ == "ADP" and token.dep_ == "prep":
            objlist.extend([t for t in sen[head_idx+1:] if token.dep_ in deptag[tag] or (t.pos_ == "PRON" and t.lower == "me")])
        if(len(objlist)==0):
            obj_deptree(sen[head_idx])
    return objlist

def verb_idxs(sen):
    sen=nlp(sen)
    idxs=[(i,token) for i,token in enumerate(sen)if token.pos_=='VERB' and token.dep_ != "aux" and token.dep_ != 'auxpass']
    if len(idxs) == 0:
        idxs=[(i,token) for i,token in enumerate(sen) if token.pos_ == "VERB" or token.pos_ == "AUX"]
    return idxs


def word_in_sen(s,sen):
    for word in s:
        if word in sen:
            return True
    if len(s)==0:
        return True
    return False


ans=pd.DataFrame(columns=["index","T/F"])
s = []
v = []
o = []
win=0
for row in trange(len(data)):
    sen=data["句子"][row]
    sen=nlp(sen)
    s.clear()
    v.clear()
    o.clear()
    for idx in verb_idxs(sen):
        subj=get_subj(sen,idx[0],'subj')
        obj=get_obj(sen,idx[0],'obj')
        verb = sen[idx[0]]
        if len(subj)!=0:
            for su in subj:
                s.append(su.text)
        if obj is not None:
            for ob in obj:
                o.append(ob.text)
        if verb != None:
            v.append(verb.text)
    

    a = word_in_sen(s, str(data["主詞"][row]))
    b = word_in_sen(v, str(data["動詞"][row]))
    c = word_in_sen(o, str(data["受詞"][row]))
    predict=int(a and b and c)


    ans.loc[row] = [row,predict]

ans.to_csv("predict.csv",index=False)






