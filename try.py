#Author: 紀竺均
#Student ID: 109550027
#HW ID: hw1
import pandas as pd
import spacy
from tqdm import trange
nlp=spacy.load("en_core_web_sm")
sen = "Rhodes discovered he had cancer last October after he felt a sharp pain in his right leg ."

sen=nlp(sen)
for token in sen:
    tag = "subj"
    print(token, token.head, token.head.i)
    print(list(token.subtree))
    '''if tag in token.dep_ and token.head.i==2:
        subtree=list(token.subtree)
        start=subtree[0].i
        end=subtree[-1].i+1
        print(sen[start:end],"ok")'''


