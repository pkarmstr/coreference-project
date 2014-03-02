
from file_reader import TREES_DICTIONARY, POS_DICTIONARY, RAW_DICTIONARY, PRONOUN_LIST, FeatureRow
import re, os, nltk
from nltk.corpus import names


def dem_np(feats):
    """WORKS!"""
    dem_re = re.findall(r"these|this|that|those",feats.j_cleaned) #yes, only j!
    return "dem_np={}".format(len(dem_re) > 0)

def number_agreement(feats):
    "WORKS"
    i_number = __determine_number__(feats.article,feats.sentence, feats.token,
                                feats.offset_begin,feats.offset_end)
    j_number= __determine_number__(feats.article, feats.sentence_ref, feats.token_ref,
                               feats.offset_begin_ref,feats.offset_end_ref)
    return "number_agreement={}".format(i_number==j_number)


def __get_pos__(fname,sent_num,start_index,end_index):
    """from Anya, just changed the +.raw part. WORKS"""
    fname += ".raw"
    sent_num=int(sent_num)
    start_index=int(start_index)
    end_index=int(end_index)
    sent=POS_DICTIONARY[fname][sent_num]
    word=sent[start_index:end_index]
    pos=word[-1][1]
    return pos

def __determine_number__(article,sentence,token, start_index, end_index):
    """WORKS"""
    pos_tag = __get_pos__(article,sentence,start_index, end_index)
    if pos_tag == "PRP" or pos_tag == "PRP$":
        if token in ["they","them","their"]:
            return "plural"
    elif pos_tag == "NNS":
        return "plural"
    return "singular"


def both_proper_name(feats):
    """WORKS"""
    i_pos = __get_pos__(feats.article, feats.sentence, feats.offset_begin, feats.offset_end)
    j_pos = __get_pos__(feats.article, feats.sentence_ref, feats.offset_begin_ref, feats.offset_end_ref)
    return "both_proper_name={}".format(i_pos == "NNP" and i_pos == j_pos)



def gender_agreement(feats):
    """WORKS"""
    i_gender = __determine_gender__(feats.article, feats.sentence, feats.i_cleaned,
                                feats.offset_begin, feats.offset_end, feats.entity_type)
    j_gender=__determine_gender__(feats.article, feats.sentence_ref, feats.j_cleaned,
                              feats.offset_begin_ref,feats.offset_end_ref, feats.entity_type_ref)
    if i_gender == "unknown" or j_gender == "unknown":
        agreement = "unknown"
    else:
        agreement = i_gender == j_gender
    return "gender_agreement={}".format(agreement)

def __determine_gender__(article, sentence, token, start_index, end_index, entity_type):
    """WORKS"""
    if entity_type == "PER":
        if token in PRONOUN_LIST:
            if token in ["he","his"]:
                return "male"
            elif token in ["she","her"]:
                return "female"
        elif token.startswith("Mr.") or token.split("_")[0] in names.words("male.txt"):
            return "male"
        elif token.startswith("Mrs.") or token.split("_")[0] in names.words("female.txt"):
            return "female"
    return "unknown"


def alias(feats):
    """WORKS"""
    i_tokens = feats.i_cleaned.split("_")
    j_tokens = feats.j_cleaned.split("_")
    if feats.entity_type == "PER" and feats.entity_type_ref == "PER":
        alias = i_tokens[len(i_tokens)-1] == j_tokens[len(j_tokens)-1] #Murray_Schwartz, Schwartz.
    elif feats.entity_type == "ORG" and feats.entity_type_ref == "ORG":
        postmodifiers = ["Corp.", "Ltd."]
        if len(i_tokens) > len(j_tokens):
            longest = i_tokens
            shortest = j_tokens
        elif len(j_tokens) > len(i_tokens):
            longest = j_tokens
            shortest = i_tokens
        else:
            longest = None
            alias = False
        if longest != None:
            for m in postmodifiers:
                if m in longest:
                    longest.remove(m)
            acro_no_period = "".join([w[0] for w in longest if w.istitle()])
            acro_period = "".join([w[0]+"." for w in longest if w.istitle()])
            match_bool = shortest[0] == acro_no_period or shortest[0] == acro_period
            alias = match_bool
    else:
        alias = False

    return "alias={}".format(alias)


def apposition(feats):
    pass #TODO


def semantic_class_agreement(feats):
    pass #TODO


















