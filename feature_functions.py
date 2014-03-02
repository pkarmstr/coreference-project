"""put your feature functions in here!"""

from file_reader import TREES_DICTIONARY, POS_DICTIONARY, RAW_DICTIONARY, PRONOUN_LIST
import re, os, nltk
from nltk.corpus import names
from collections import namedtuple

##################
# basic features #
##################

def is_coreferent(fr):
    return fr.is_referent

def token(fr):
    return "token={}".format(fr.token)

def entity_type(fr):
    return "entity_type={}".format(fr.entity_type)

def token_ref(fr):
    return "token_ref={}".format(fr.token_ref)

def entity_type_ref(fr):
    return "entity_type_ref={}".format(fr.entity_type_ref)

#################
# Julia's stuff #
#################

#####tesing right now just with this named tuple and this coreference pair
FeatureRow = namedtuple("GoldFeature", ["article", "sentence", "offset_begin",
                                        "offset_end", "entity_type", "token",
                                        "sentence_ref", "offset_begin_ref",
                                        "offset_end_ref", "entity_type_ref",
                                           "token_ref", "is_referent"])
line = "NYT20001017.1908.0279.head.coref 6 31 32 ORG corporations 9 9 10 ORG companies yes"
line = line.rstrip().split()
feats = FeatureRow(*line)


##getting the POS until Keelan's branch is updated with the other dictionaries
pos_files={}
for f in os.listdir("pos_sentences"):
    pos_files[f[:-4]]=[]
    for line in open(r"pos_sentences/"+f,"r"):
        if line!="\n":
            #print line
            pos_files[f[:-4]].append(line.rstrip())


##some feature functions, SOME OF THEM NOT FULLY DONE!

def dem_np(feats):
    dem_re = re.findall(r"these|this|that|those",feats.token_ref) #only j!
    return "dem_np={}".format(len(dem_re)>0)

def number_agreement(feats):
    i_number = determine_number(feats.article,feats.sentence, feats.token, feats.offset_begin)
    j_number= determine_number(feats.article, feats.sentence_ref, feats.token_ref, feats.offset_begin_ref)
    return "number_agreement={}".format(i_number==j_number)

def determine_number(article,sentence,token_to_check, index_to_check):
    article = article+".raw"
    tokens=pos_files[article][int(sentence)].split()
    pos_tagged_i=tokens[int(index_to_check)]
    pos_tag = pos_tagged_i[pos_tagged_i.index("_")+1:]
    if pos_tag== "PRP" or pos_tag == "PRP$":
        if token_to_check in ["they","them","their"]:
            return "plural"
        else:
            return "singular"
    else: #have to look the POS of the head of the phrase <<<<<----TO DO, NOT FIXED YET!
        if "_" not in token_to_check: #only one word, have been only looking at one/the first one..easy cases
            if pos_tag == "NNS":
                return "plural"
            else:
                return "singular"
        #else: ##NOT FINISHED!!
            #find head of entity, look number
            ##NOT FINISHED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def both_proper_name(feats):
    i_NNP = determine_proper_name(feats.article,feats.sentence,feats.offset_begin)
    j_NNP= determine_proper_name(feats.article, feats.sentence_ref, feats.offset_begin_ref)
    return "both_proper_name={}".format(i_NNP and i_NNP == j_NNP)

def determine_proper_name(article,sentence,index_to_check):
    article = article+".raw"
    tokens=pos_files[article][int(sentence)].split()
    pos_tagged_i=tokens[int(index_to_check)]
    pos_tag = pos_tagged_i[pos_tagged_i.index("_")+1:]
    return pos_tag == "NNP"


def semantic_class_agreement(feats):
    pass #TODO


def gender_agreement(feats):
    i_gender = determine_gender(feats.article,feats.sentence, feats.token, feats.offset_begin, feats.entity_type)
    j_gender=determine_gender(feats.article, feats.sentence_ref, feats.token_ref, feats.offset_begin_ref, feats.entity_type_ref)
    if i_gender == "unknown" or j_gender == "unknown":
        agreement="unknown"
    else:
        agreement = i_gender == j_gender
    return "gender_agreement={}".format(agreement)

def determine_gender(article,sentence,token_to_check, index_to_check, entity_type):
    article = article+".raw"
    tokens=pos_files[article][int(sentence)].split()
    pos_tagged_i=tokens[int(index_to_check)]
    pos_tag = pos_tagged_i[pos_tagged_i.index("_")+1:]
    if entity_type == "PER":
        if pos_tag== "PRP" or pos_tag == "PRP$":
            if token_to_check in ["he","his"]:
                return "male"
            elif token_to_check in ["she","her"]:
                return "female"
            else:
                return "unknown"
        elif token_to_check.startswith("Mr."):
            return "male"
        elif token_to_check.startswith("Mrs."):
            return "female"
        elif token_to_check in names("male.txt"):
            return "male"
        elif token_to_check in names("female.txt"):
            return "female"
    else: #organization, locations...
        return "unknown"
        #THIS IS INCOMPLETE, FOR ENTITY-TYPES THAT ARE NOT PERSON YOU CHECK
        #SEMANTIC CLASSES BUT I HAVEN'T DONE SEMANTIC CLASSES YET (TOMORROW)


def alias(feats):
    i_tokens = feats.token.split("_")
    j_tokens = feats.token_ref.split("_")
    if feats.entity_type == "PER" and feats.entity_type_ref == "PER":
        alias = i_tokens(len(i_tokens)-1) == j_tokens(len(j_tokens)-1) #Murray_Schwartz, Schwartz.
    elif feats.entity_type == "ORG":
        postmodifiers = ["Corp.", "Ltd."]
        if len(i_tokens)>len(j_tokens):
            longest = i_tokens
            shortest = j_tokens
        elif len(j_tokens)>len(i_tokens):
            longest = j_tokens
            shortest=i_tokens
        else:
            longest=None
            alias = False
        if longest!=None:
            for m in postmodifiers:
                if m in longest:
                    longest.remove(m)
            acro_no_period = "".join([w[0] for w in longest if w.istitle()])
            acro_period = "".join([w[0]+"." for w in longest if w.istitle()])
            alias =  shortest==acro_no_period or shortest == acro_period
    else:
        alias = False

    return "alias={}".format(alias)

def apposition(feats):
    pass #TOMORROW

################
# Anya's stuff #
################

def i_pos(fs):
    """written for practice, don't have to use"""
    sent_num=fs.sentence
    start_index=fs.offset_begin
    end_index=fs.offset_end
    fname=fs.article+".raw"
    return "i_pos={}".format(get_pos(fs,fname,sent_num,start_index,end_index))

def get_pos(fs,fname,sent_num,start_index,end_index):
    """written for practice, don't have to use"""
    sent_num=int(sent_num)
    start_index=int(start_index)
    end_index=int(end_index)
    sent=POS_DICTIONARY[fname][sent_num]

    word=sent[start_index:end_index]

    pos=word[-1][1]
    #print fs.token,'\t',word,'\t',pos,'\n'
    return pos

def dist(fs):
    """number of sentences between the markables"""
    distance=int(fs.sentence_ref) - int(fs.sentence)
    #print fs.sentence,'\t',fs.sentence_ref,'\t',distance,'\n'
    return "dist={}".format(str(distance))

def i_pronoun(fs):
    """the first markable is a pronoun (includes reflexives)"""
    #print fs.token,'\t',fs.token.split('_')[0] in PRONOUN_LIST,'\n'
    return "i_pronoun={}".format(fs.token.split('_')[0].lower() in PRONOUN_LIST)

def j_pronoun(fs):
    """the second markable is a pronoun (includes reflexives)"""
    return "j_pronoun={}".format(fs.token_ref.split('_')[0].lower() in PRONOUN_LIST)

def string_match(fs):
    """allows full string match or partial string match, both ways"""
    i_cleaned=re.sub(r'(\W+)(\w)', r'\2', fs.token).lower()
    j_cleaned=re.sub(r'(\W+)(\w)', r'\2', fs.token_ref).lower()
    #print i_cleaned,'\t',j_cleaned,'\t',(i_cleaned in j_cleaned) or (j_cleaned in i_cleaned),'\n'
    return "string_match={}".format((i_cleaned in j_cleaned) or (j_cleaned in i_cleaned))

if __name__ == "__main__":
    print dem_np(feats)
    print number_agreement(feats)
    print both_proper_name(feats)
    print gender_agreement(feats)
    print alias(feats)