#Author: 紀竺均
#Student ID: 109550027
#HW ID: hw1
import numpy as np
import pandas as pd
import spacy
from tqdm import trange

def trace_dep_tree_for_subject(verb):
    head = verb.head
    while head.head != head:
        head = head.head
        if head.pos_ == "VERB":
            subs = [t for t in head.lefts if t.dep_ in SUBJECTS]
            if len(subs) > 0:
                new_subs = list()
                for sub in subs:
                    new_subs.extend(sub.conjuncts)
                subs.extend(new_subs)
                return subs
            elif head.head != head:
                continue
            else:
                return []
        elif head.pos_ == "NOUN":
            return [head]

    return []


def get_subjects(verb):
    subs = [t for t in verb.lefts if t.dep_ in SUBJECTS and t.pos_ != "DET"]  # RULE
    if len(subs) == 0:
        # RULE
        subs = trace_dep_tree_for_subject(verb)
    else:
        new_subs = list()
        for sub in subs:
            new_subs.extend(sub.conjuncts)
        subs.extend(new_subs)
    return subs


def get_objects_from_prep(rights):
    ret = list()
    for t in rights:
        if t.pos_ == "ADP" and t.dep_ == 'prep':
            ret.extend([tt for tt in t.rights if tt.dep_ in OBJECTS or
                        (tt.pos_ == "PRON" and tt.lower_ == "me")])
    return ret


# find verbs without subject
def get_open_objects(rights):
    for t in rights:
        if t.pos_ == "VERB" and t.dep_ == "xcomp":
            new_v = t
            objs = [tt for tt in new_v.rights if tt.dep_ in OBJECTS]
            objs.extend(get_objects_from_prep(new_v.rights))
            if len(objs) > 0:
                return objs
    return None


def get_objects(verb):
    objs = [t for t in verb.rights if t.dep_ in OBJECTS]  # RULE

    objs.extend(get_objects_from_prep(verb.rights))  # RULE

    new_objs = get_open_objects(verb.rights)  # RULE
    if new_objs is not None:
        objs.extend(new_objs)

    new_objs = list()
    for obj in objs:
        new_objs.extend(obj.conjuncts)  # RULE
    objs.extend(new_objs)
    return objs


def expand_token(item, doc):  # expend object/subject to whole chunk
    if item.lower_ == 'that':  # replace that by original entity if possible
        for t in doc:
            if 'that' in {tt.text for tt in t.lefts}:  # RULE
                item = t
                break
    parts = list()

    # find left components
    for t in item.lefts:
        if t.pos_ in BREAKER_POS:
            break
        if t.lower_ not in NEGATIONS:
            parts.append(t)

    # token itself
    parts.append(item)

    # find right components
    for t in item.rights:
        if t.pos_ in BREAKER_POS:
            break
        if t.lower_ not in NEGATIONS:
            parts.append(t)

    return parts


def extract_SVO(sentence):
    tokens = nlp(sentence)
    tokens = [t for t in tokens if not (t.is_stop or t.is_punct)]
    ret = list()
    verbs = [t for t in tokens if t.pos_ ==
             "VERB" and t.dep_ != "aux" and t.dep_ != 'auxpass']
    if len(verbs) == 0:
        # include auxiliary verb if no verb found
        verbs = [t for t in tokens if t.pos_ == "VERB" or t.pos_ == "AUX"]

    for verb in verbs:
        subs = get_subjects(verb)
        if len(subs) == 0:
            continue

        # find right conjunction verb (CCONJ)
        conj_verb = None
        try:
            if next(verb.rights).pos_ == 'CCONJ':
                for t in verb.rights:
                    if t.pos_ == "VERB" and t.dep_ != "aux" and t.dep_ != 'auxpass':
                        conj_verb = t
                        break
        except StopIteration:
            pass
        if conj_verb is not None:
            objs = get_objects(verb) + get_objects(conj_verb)
        else:
            objs = get_objects(verb)
        for sub in subs:
            for obj in objs:
                ret.append(expand_token(sub, tokens) +
                           [verb] + expand_token(obj, tokens))
                if conj_verb is not None:
                    ret.append(expand_token(sub, tokens) +
                               [conj_verb] + expand_token(obj, tokens))

    return ret


# Hyper-parameters & settings
nlp = spacy.load("en_core_web_sm")
threshold = 0.99

SUBJECTS = {"nsubj", "nsubjpass", "csubj",
            "csubjpass", "agent", "expl"}  # DEP tags
OBJECTS = {"dobj", "dative", "attr", "oprd"}  # DEP tags
BREAKER_POS = {"CCONJ", "VERB"}  # POS tags
NEGATIONS = {"no", "not", "n't", "never", "none"}  # words


def main():
    data_path="dataset.csv"
    data=pd.read_csv(data_path,header=None,names=['編號','句子','主詞','動詞','受詞'])

    predictions = list()
    cache = None
    for row in trange(len(data)):
        label = 0
        if row != cache:
            svos = extract_SVO(row)
        eval_svo = nlp(" ".join(list(row['S':'O'])))
        for pos in svos:
            pos = nlp(" ".join([t.text for t in pos]))
            if eval_svo.similarity(pos) >= threshold:
                label = 1
                break
        predictions.append(label)
        cache = row

    '''data['label'] = predictions
    data[['id', 'label']].to_csv("submit.csv", index=False)
    print(f'Threshold: {threshold}, positive labels: {np.sum(data.label)}')'''


if __name__ == '__main__':
    main()