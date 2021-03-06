from __future__ import division
from file_reader import TREES_DICTIONARY, POS_DICTIONARY, RAW_DICTIONARY, PRONOUN_LIST, NONCONTENT_SET, COREF_DICTIONARY, FeatureRow, TITLE_SET
import re, os, nltk
from nltk.corpus import names
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError as wn_error
from nltk.tree import ParentedTree
from nltk.corpus import wordnet as wn
from math import ceil
#SEM_CLASSES = {wn.synset('person.n.01'):"PER", wn.synset('location.n.01'):"LOC", wn.synset('organization.n.01'):"ORG",
#               wn.synset('date.n.01'):"DATE", wn.synset('time_unit.n.01'):"TIME", wn.synset('money.n.01'):"MONEY",
#               wn.synset('percent.n.01'):"PERCENT", wn.synset('object.n.01'):"OBJECT"}

SEM_CLASSES = {wn.synset('person.n.01'):"PER", wn.synset('district.n.01'):"GPE",
               wn.synset('location.n.01'):"LOC", wn.synset('organization.n.01'):"ORG",
               wn.synset('vehicle.n.01'):"VEH", wn.synset('structure.n.01'):"FAC"}


###############
# basic stuff #
###############

def is_coreferent(fs):
    return fs.is_referent

#################
# julia's stuff #
#################

def dem_token(feats):
    """WORKS!"""
    dem_re = re.findall(r"these|this|that|those",feats.j_cleaned) #yes, only j!
    return "dem_token={}".format(len(dem_re) > 0)

def dem_np(feats):
    """WORKS"""
    fname = feats.article +".raw"
    sent=RAW_DICTIONARY[fname][int(feats.sentence_ref)]
    if feats.offset_begin_ref>3:
        window = sent[feats.offset_begin_ref-3:feats.offset_begin_ref+1]
    else:
        window = sent[0:feats.offset_begin_ref+1]
    dems=set(['this','these','that','those'])
    match = dems.intersection(set(window))
    return "dem_j={}".format(len(match)>0)



def number_agreement(feats):
    "WORKS"
    i_number = __determine_number__(feats.article,feats.sentence, feats.token,
                                feats.offset_begin,feats.offset_end)
    j_number= __determine_number__(feats.article, feats.sentence_ref, feats.token_ref,
                               feats.offset_begin_ref,feats.offset_end_ref)
    one_unknown = i_number == "unknown" or j_number == "unknown"
    return "number_agreement={}".format(i_number==j_number or one_unknown)


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
    elif pos_tag == "WP" or pos_tag == "WP$":
        return "unknown"
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
        if isinstance(longest,list):
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


def i_entity_type__(feats):
    return "i_entity_type={}".format(feats.entity_type)

def j_entity_type__(feats):
    return "j_entity_type_={}".format(feats.entity_type_ref)


def entity_type_agreement(feats):
    ##intuition similar to sem_class agreement (not implemented)
    """WORKS"""
    i_entity_type = feats.entity_type
    j_entity_type = feats.entity_type_ref
    return "entity_type_agreement={}".format(i_entity_type == j_entity_type)


def number_composite(feats):
    i_number = __determine_number__(feats.article,feats.sentence, feats.token,
                                feats.offset_begin,feats.offset_end)
    j_number= __determine_number__(feats.article, feats.sentence_ref, feats.token_ref,
                               feats.offset_begin_ref,feats.offset_end_ref)
    return "number_composite={}".format(i_number +"-"+j_number)


def gender_composite(feats):
    i_gender = __determine_gender__(feats.article, feats.sentence, feats.i_cleaned,
                                feats.offset_begin, feats.offset_end, feats.entity_type)
    j_gender=__determine_gender__(feats.article, feats.sentence_ref, feats.j_cleaned,
                              feats.offset_begin_ref,feats.offset_end_ref, feats.entity_type_ref)
    return "gender_composite={}".format(i_gender + "-" + j_gender)

def entity_composite(feats):
    return "entity_composite={}".format(feats.entity_type + "-" + feats.entity_type_ref)



def apposition(feats): #this was driving me MAD....I SHOULD CORRECT THE STYLE...aarrrrggghhshs
    """WORKS WITH THE EXAMPLES IN UNITTEST, HOPE THEY WERE NOT A COINDIDENCE"""
    if feats.sentence!=feats.sentence_ref:
        return "apposition={}".format(False)
    else:
        sentence_tree = TREES_DICTIONARY[feats.article+".raw"][int(feats.sentence_ref)]
        ptree = ParentedTree.convert(sentence_tree)
        token_ref = set(feats.token_ref.split("_"))
        token = set(feats.token.split("_"))
        def is_j_apposition(curr_tree):
                found = False
                for child in curr_tree:
                    if found:
                        break
                    elif isinstance(child, ParentedTree):
                        child_leaves = set(child.leaves())
                        conditions = len(token_ref.intersection(child_leaves))>0 and curr_tree.node == "NP"
                        if conditions:
                            brother = child.left_sibling()
                            if isinstance(brother, ParentedTree) and brother.node == ",":
                                antecedent = brother.left_sibling()
                                if isinstance(antecedent,ParentedTree):
                                    previous_words = set(antecedent.leaves())
                                    if len(token.intersection(previous_words))>0:
                                        found = True
                        else:
                            found = is_j_apposition(child)

                return found
        return "apposition={}".format(is_j_apposition(ptree))


#ANYA'S FUNCTION :)
def __get_parent_tree__(unclean_token, t):
    """
    Given a token, returns the subtree that dominates that token in the corresponding parse tree.
    (Goes one level up from the POS)
    """
    words = unclean_token.split('_')
    leaf_indices=[]
    for word in words:
        word=re.sub(r'O\'|d\'|;T','',re.sub(r'\'s$','',re.sub(r'[^\w\s.]+$','',re.sub(r'^[^\w\s-]+','',word))))
        word=re.sub(r'Bond/|/ABC','',word)
        if word=='':
            word='&'
        elif word=='CBS' and word not in t.leaves():
            continue
        elif word=='AMP' and word not in t.leaves():
            word='&AMP'
        elif word not in t.leaves():
            pass
        leaf_indices.append(t.leaves().index(word))

    start=leaf_indices[0]
    end=leaf_indices[-1]

    if end > start:
        position_tuple=t.treeposition_spanning_leaves(start,end)
    else:
        position_tuple=t.leaf_treeposition(start)

    #if a phrase spans an entire NP, we want to just return that NP instead of going one level up
    if not isinstance(t[position_tuple],str) and t[position_tuple].node.endswith('P') and \
                    t[position_tuple].node!='PRP' and t[position_tuple].node!='NNP':
        parent_tree=t[position_tuple]

    else:
        parent_tree=t[position_tuple[:-2]]

    return parent_tree

def parent_test(fs):
    """
    Used for testing the ___get_parent_tree__ function. DNU otherwise.
    """
    i_t=TREES_DICTIONARY[fs.article+'.raw'][int(fs.sentence)]
    j_t=TREES_DICTIONARY[fs.article+'.raw'][int(fs.sentence_ref)]
    parent_i=__get_parent_tree__(fs.token,i_t)
    parent_j=__get_parent_tree__(fs.token_ref,j_t)
    print "LEFT SIDE:"
    print fs.token
    print parent_i.__repr__()
    print
    print "RIGHT SIDE:"
    print fs.token_ref
    print parent_j.__repr__()
    print
    print
    return "parent_test={}".format('Blah')

def __get_max_projection__(bigger_tree,target_tree):
    """this actually only returns the parent of the target tree.
     The get_parent functions is used for tokens, this one is for subtrees
    """
    max_p = None
    for child in bigger_tree:
        if isinstance(max_p, ParentedTree):
            break
        elif isinstance(child, ParentedTree):
            if child == target_tree:
                max_p = bigger_tree
            else:
                max_p = __get_max_projection__(child,target_tree)
    return max_p

def __is_subject__(curr_tree,token, parent, sentence_tree):
    """WORKS"""
    found = False
    for child in curr_tree:
        if isinstance(child, ParentedTree):
            if child == parent and (child.node == "NP" or child.node == "WHNP"):
                left_brother = child.left_sibling()
                right_brother = child.right_sibling()
                if isinstance(left_brother, ParentedTree): #SVO
                    if left_brother.node == "VP":
                        found = True
                if isinstance(right_brother,ParentedTree): #OVS
                    if right_brother.node == "VP" or right_brother.node == "S":
                        found = True

                OVS_with_apposition = __get_max_projection__(sentence_tree,parent)
                if isinstance(OVS_with_apposition, ParentedTree):
                    if __is_subject__(sentence_tree,token,OVS_with_apposition,sentence_tree):
                        found = True
            else:
                found = __is_subject__(child,token, parent,sentence_tree)
        if found:
            break
    return found


def i_is_subject(feats):
    "WORKS"
    sentence_tree = TREES_DICTIONARY[feats.article+".raw"][int(feats.sentence)]
    ptree = ParentedTree.convert(sentence_tree)
    parent = __get_parent_tree__(feats.token, ptree)
    i_subject = __is_subject__(ptree,feats.token,parent,ptree)
    return "i_is_subject={}".format(i_subject)

def j_is_subject(feats):
    "WORKS"
    sentence_tree = TREES_DICTIONARY[feats.article+".raw"][int(feats.sentence_ref)]
    ptree = ParentedTree.convert(sentence_tree)
    parent = __get_parent_tree__(feats.token_ref, ptree)
    j_subject = __is_subject__(ptree,feats.token_ref, parent,ptree)
    return "j_is_subject={}".format(j_subject)

def both_subjects(feats):
    """WORKS"""
    both_bool = i_is_subject(feats).endswith("True") and j_is_subject(feats).endswith("True")
    return "both_subjects={}".format(both_bool)


def none_is_subject(feats):
    """WORKS"""
    none_bool = i_is_subject(feats).endswith("False") and j_is_subject(feats).endswith("False")
    return "none_is_subject={}".format(none_bool)

def animacy_agreement(feats):
    """"WORKS"""
    both_people = feats.entity_type == "PER" and feats.entity_type_ref == "PER"
    both_not_people = feats.entity_type != "PER" and feats.entity_type_ref != "PER"
    return "animacy_agreement={}".format(both_people or both_not_people)


def same_max_NP(feats):
    """WORKS"""
    if feats.sentence !=  feats.sentence_ref:
        return "same_max_NP={}".format(False)
    else:
        sentence_tree = TREES_DICTIONARY[feats.article+".raw"][int(feats.sentence)]
        ptree = ParentedTree.convert(sentence_tree)
        parent1 = __get_parent_tree__(feats.token, ptree)
        parent2 = __get_parent_tree__(feats.token_ref, ptree)
        #print "parent of: ", feats.token, ":", parent1
        #print "parent of: ", feats.token_ref, ":", parent2
        max_p_i = __get_max_projection__(ptree,parent1)
        max_p_j = __get_max_projection__(ptree, parent2)
        if max_p_i is not None and max_p_j is not None:
            both_NPs = max_p_i.node == "NP" and max_p_j.node == "NP"
        else:
            both_NPs = False
        return "same_max_NP={}".format(max_p_i == max_p_j and both_NPs)





def is_pred_nominal(feats):
    """WORKS"""
    if feats.sentence != feats.sentence_ref:
        return "is_pred_nominal={}".format(False)
    else:
        s_tree = ParentedTree.convert(TREES_DICTIONARY[feats.article+".raw"][int(feats.sentence)])
        NP_i = __get_parent_tree__(feats.token, s_tree)
        NP_j = __get_parent_tree__(feats.token_ref,s_tree)
        nominal= __get_max_projection__(s_tree,NP_j)
        copula_verbs = ["is","are","were","was","am"]
        def check_nominal_construction(tree):
            found = False
            for t in tree:
                if found:
                    break
                elif isinstance(t, ParentedTree):
                    if t == NP_i:
                        brother = t.right_sibling()
                        if isinstance(brother,ParentedTree) and brother.node == "VP":
                            verb = brother.leaves()[0]
                            if verb in copula_verbs:
                                for subtree in brother:
                                    if subtree == nominal:
                                        found = True
                                        break
                    else:
                        found = check_nominal_construction(t)
            return found

        return "is_pred_nominal={}".format(check_nominal_construction(s_tree))



def span(feats):
    """WORKS"""
    if feats.sentence != feats.sentence_ref:
        return "span={}".format(False)
    else:
        s_tree = ParentedTree.convert(TREES_DICTIONARY[feats.article+".raw"][int(feats.sentence)])
        i_parent = __get_parent_tree__(feats.token, s_tree)
        j_parent = __get_parent_tree__(feats.token_ref,s_tree)
        return "span={}".format(i_parent==j_parent)



def could_be_coindexed(feats):
    """two non pronominal entities separated by a preposition cannot be coindexed
    WORKS"""
    if feats.sentence != feats.sentence_ref:
        return "could_be_coindexed={}".format(True)
    else:
        sent=POS_DICTIONARY[feats.article +".raw"][int(feats.sentence)]
        i_pron = i_pronoun(feats).endswith("True")
        j_pron = j_pronoun(feats).endswith("True")
        if not i_pron and not j_pron:
            if feats.offset_end < feats.offset_begin_ref:
                inbetween= [tag for w,tag in sent[int(feats.offset_end):int(feats.offset_begin_ref)]]
            else:
                inbetween=[tag for w,tag in sent[int(feats.offset_begin_ref):int(feats.offset_begin)]]

            if len(inbetween)<=2 and 'IN' in inbetween:
                return "could_be_coindexed={}".format(False)

        return "could_be_coindexed={}".format(True)


def compatible_syntax(feats):
    """WORKS"""
    compatible = could_be_coindexed(feats).endswith("True") and span(feats).endswith("False")
    return "compatible_syntax={}".format(compatible)

def j_indefinite(feats):
    """j is not definite but it isn't an apposition either
    WORKS"""
    return "j_indefinite={}".format(def_np(feats).endswith("False") and
                                    apposition(feats).endswith("False"))

def i_pron_j_not_pron(feats):
    """WORKS"""
    return "i_pron_j_not_pron={}".format(i_pronoun(feats).endswith("True") and
                                         j_pronoun(feats).endswith("False"))

def meet_all_constraints(feats):
    """WORKS"""
    gender_agree = gender_agreement(feats).endswith("True") or gender_agreement(feats).endswith("unknown")
    number_agree = number_agreement(feats).endswith("True")
    compatible_syntx = compatible_syntax(feats).endswith("True")
    animacy_agree = animacy_agreement(feats).endswith("True")
    entity_agree = animacy_agreement(feats).endswith("True")
    compatible = gender_agree and number_agree and \
                 compatible_syntx and animacy_agree and entity_agree
    return "meet_all_constraints={}".format(compatible)
    return "meet_all_constraints={}".format(compatible)
def closest_comp(feats):
    closest = True
    
    ##Find which one comes first in the paragraph
    later_one = _later_markable(feats)
    if later_one == "j":
        first_instance = (feats.token, feats.sentence,
                          feats.offset_end, feats.entity_type)
        later_instance = (feats.token_ref, feats.sentence_ref,
                          feats.offset_begin_ref, feats.entity_type_ref)
    else:
        first_instance = (feats.token_ref, feats.sentence_ref,
                          feats.offset_end_ref, feats.entity_type_ref)
        later_instance = (feats.token, feats.sentence,
                          feats.offset_begin, feats.entity_type)
    
    #Check compatibillity values
    if entity_type_agreement(feats).endswith("True") and \
            compatible_syntax(feats).endswith("True"):


        # Occur in same sentence, check for closest NP candidates 
        if first_instance[1] == later_instance[1]: #same sentence
            sentence = POS_DICTIONARY[feats.article+".raw"][int(later_instance[1])]
            candidate_antecedents = sentence[int(first_instance[2]):int(later_instance[2])]
        
        #Occur in different sentences: Check for NPs before j and between i that could be
        #candidates in other sentences inbetween
        else:
            candidate_antecedents = _get_inbetween_words__(feats,first_instance[1],later_instance[1],
                                                          first_instance[2],later_instance[2])

        candidate_antecedents.reverse()
        #check closer NP (reverse list) for compatibility. If one is found,
        #then i is not the closest compatible one.
        for c,tag in candidate_antecedents:
            ok_tags = ["NNP", "NNS", "NN", "PRP", "PRP$"]
            if tag in ok_tags:
                c_sem_class = __get_sem_class__(c)
                if c_sem_class == later_instance[3]: #entity of NP2
                    closest = False
                    break

    return "closes_comp={}".format(closest)


def _get_inbetween_words__(feats, first_sentence_offset, later_sentence_offset, i_offset_end, j_offset_begin):
    """Watch out, i and j correspond to former and later tokens, not to feats.token and feats.token_ref:
    the first occurring in the text is i, the latter is j"""
    words_inbetween = POS_DICTIONARY[feats.article+".raw"][int(first_sentence_offset)][int(i_offset_end):]
    until_j = POS_DICTIONARY[feats.article+".raw"][int(later_sentence_offset)][:int(j_offset_begin)]
    if int(first_sentence_offset) != int(later_sentence_offset) + 1: #there is at least a sentence inbetween the two sents.
        middle_sentences = POS_DICTIONARY[feats.article+".raw"][int(first_sentence_offset)+1:int(later_sentence_offset)]
        middle_tokens = []
        for s in middle_sentences:
            middle_tokens.extend([l for l in s])
        middle_tokens.extend(until_j)
        words_inbetween.extend(middle_tokens)
    else: #i sentences precedes j sentence (difference of 1)
        words_inbetween.extend(until_j)
    return words_inbetween

def subclass(feats):
    if string_match(feats).endswith("False"):
        try:
            result = False
            i_clean = wn.morphy(feats.i_cleaned.lower(), wn.NOUN)
            i_synsets = wn.synsets(i_clean)
            j_clean = wn.morphy(feats.j_cleaned.lower(), wn.NOUN)
            j_synsets = wn.synsets(j_clean)
            def get_common_hypernym(i_synset,j_synset):
                i_hypernyms = i_synset.hypernyms()
                j_hypernyms = j_synset.hypernyms()
                if len(i_hypernyms) == 0:
                    i_synset = i_synset.instance_hypernyms()[0]
                if len(j_hypernyms) == 0:
                    j_synset = j_synset.instance_hypernyms()[0]
                subc = i_synset.common_hypernyms(j_synset)
                return (i_synset in subc) or (j_synset in subc)

            for synset in i_synsets:
                for syn in j_synsets:
                    result = get_common_hypernym(synset,syn)
                    if result: break
                if result:break
            return "subclass={}".format(result)
        except:
            wn_error
            return "subclass={}".format(False)

    else:
        return "subclass={}".format(False)




def __get_sem_class__(token):
    token = re.sub(r'[`]','',token)
    per_pronouns = ["she", "he", "they", "you", "we",
                    "i", "them", "her", "him", "us", "who","whom"]
    if token.lower() in per_pronouns:
        sem_class = "PER"
    else:
        sem_class = "PER" #it will crash with NNP that are not GPE, so probably people
        try:
            token_clean = wn.morphy(token.lower(), wn.NOUN)
            token_sense = ""+token_clean+".n.01"
            token_synset = wn.synset(token_sense)
            for synset in SEM_CLASSES.keys():
                hypernyms = token_synset.hypernyms()
                if len(hypernyms) == 0: #need to get the instance
                    token_synset = token_synset.instance_hypernyms()[0]

                if synset in token_synset.common_hypernyms(synset):
                    sem_class = SEM_CLASSES[synset]
                    break
                else:
                    sem_class = "OTHER"
        except:
            wn_error
    return sem_class


def nominative_case(feats):
    if j_pronoun(feats).endswith("True"):
        nc = {"him":"he", "her":"she",
          "them":"they", "us":"we"}
        token = feats.token_ref.lower()
        if token in nc.keys():
            return "nominative_case={}".format(nc[token])
        else:
            return "nominative_case={}".format(token)
    else:
        return "nominative_case=unapplicable"

################
# Anya's stuff #
################

def _later_markable(fs):
    """
    Tells you which token in a coref pair occurs later in the text.
    Returns 'i' if it's the first one, and 'j' if it's the second one.
    """

    if int(fs.sentence) > int(fs.sentence_ref):
        return 'i'
    elif int(fs.sentence) < int(fs.sentence_ref):
        return 'j'
    elif int(fs.sentence)==int(fs.sentence_ref):
        if int(fs.offset_begin) > int(fs.offset_begin_ref):
            return 'i'
        elif int(fs.offset_begin) < int(fs.offset_begin_ref):
            return 'j'
    else:
        print "Error in later_markable(): Something screwy going on with offsets"

def __pos_match__(fs):
    """
    True if both markables have the same part of speech, False otherwise.
    Used in conjunction with def_np feature (and maybe dem_np too?)
    """

    pos_i = __get_pos__(fs.article,fs.sentence,fs.offset_begin,fs.offset_end)
    pos_j = __get_pos__(fs.article,fs.sentence_ref,fs.offset_begin_ref,fs.offset_end_ref)

    return pos_i==pos_j

def def_np_pos_match(fs):
    result=((def_np(fs).endswith("True")) and __pos_match__(fs))
    return "def_np_pos_match={}".format(result)

def def_np(fs):
    """
    applies only to the second markable; this probably means the LATER one, not the right-hand side one)
    Its possible values are true or false. In our definition, a definite noun phrase is a noun phrase that
    starts with the word the. For example, the car is a definite noun phrase. If j is a definite noun phrase,
    return true; else return false.
    """

    #figure out which mention is the later one
    later_mention = _later_markable(fs)

    # get the tree that dominates the later mention
    if later_mention=='i':
        sent_tree=TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence)]
        parent_tree=__get_parent_tree__(fs.token, sent_tree)
    elif later_mention=='j':
        sent_tree=TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence_ref)]
        parent_tree=__get_parent_tree__(fs.token_ref, sent_tree)

    # see if that parent tree is an NP that starts with "the" and return true if it does
    return "def_np={}".format(parent_tree.node=='NP' and parent_tree.leaves()[0].lower()=='the')

def i_pos(fs):
    """written for practice, don't have to use"""
    sent_num=fs.sentence
    start_index=fs.offset_begin
    end_index=fs.offset_end
    fname=fs.article+".raw"
    return "i_pos={}".format(__get_pos__(fname,sent_num,start_index,end_index))

def dist(fs):
    """number of sentences between the markables"""
    distance=int(fs.sentence_ref) - int(fs.sentence)
    return "dist={}".format(str(distance))

def dist_ten(fs):
    """
    True if the number of sentences b/w the markables is less than or equal to ten, False otherwise.
    """
    distance=int(fs.sentence_ref) - int(fs.sentence)
    return "dist_ten={}".format(distance<10)

def i_pronoun(fs):
    """the first markable is a pronoun (includes reflexives)"""
    return "i_pronoun={}".format(fs.token.split('_')[0].lower() in PRONOUN_LIST)

def j_pronoun(fs):
    """the second markable is a pronoun (includes reflexives)"""
    return "j_pronoun={}".format(fs.token_ref.split('_')[0].lower() in PRONOUN_LIST)

def string_match(fs):
    """allows full string match or partial string match, both ways"""
    return "string_match={}".format((fs.i_cleaned in fs.j_cleaned) or (fs.j_cleaned in fs.i_cleaned))

def word_overlap(fs):
    """
    True if the intersection between the content words in NP(i) and NP(j) is not empty;
    else False.
    """
    sent_i=TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence)]
    sent_j=TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence_ref)]
    parent_i = __get_parent_tree__(fs.token,sent_i)
    parent_j = __get_parent_tree__(fs.token_ref,sent_j)

    #convert everything to lowercase
    lowercase_leaves_i=parent_i.leaves()
    lowercase_leaves_j=parent_j.leaves()

    for p,word in enumerate(lowercase_leaves_i):
        lowercase_leaves_i[p] = lowercase_leaves_i[p].lower()

    for q,word in enumerate(lowercase_leaves_j):
        lowercase_leaves_j[q] = lowercase_leaves_j[q].lower()

    all_words_i = set(lowercase_leaves_i)
    all_words_j = set(lowercase_leaves_j)

    content_words_i=all_words_i.difference(NONCONTENT_SET) #all words minus non-content words
    content_words_j=all_words_j.difference(NONCONTENT_SET)

    intersection=content_words_i.intersection(content_words_j)

    return "word_overlap={}".format(len(intersection)>0)

def word_overlap_complete(fs):
    """
    True if all the content words in the two phrases are exactly the same.
    """
    sent_i=TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence)]
    sent_j=TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence_ref)]
    parent_i = __get_parent_tree__(fs.token,sent_i)
    parent_j = __get_parent_tree__(fs.token_ref,sent_j)

    #convert everything to lowercase
    lowercase_leaves_i=parent_i.leaves()
    lowercase_leaves_j=parent_j.leaves()

    for p,word in enumerate(lowercase_leaves_i):
        lowercase_leaves_i[p] = lowercase_leaves_i[p].lower()

    for q,word in enumerate(lowercase_leaves_j):
        lowercase_leaves_j[q] = lowercase_leaves_j[q].lower()

    all_words_i = set(lowercase_leaves_i)
    all_words_j = set(lowercase_leaves_j)

    content_words_i=all_words_i.difference(NONCONTENT_SET) #all words minus non-content words
    content_words_j=all_words_j.difference(NONCONTENT_SET)

    intersection=content_words_i.intersection(content_words_j)

    result=(len(content_words_i)==len(content_words_j)) and (len(intersection)==len(content_words_i))

    return "word_overlap_complete={}".format(result)

def modifier(fs):
    """
    C if the prenominal modifiers of one NP are a subset of the prenominal modifiers of the other; else I.
    Anya assumptions:
    - for this function to return true, both tokens have to be nouns
    - a noun's prenominal modifier is _any_ word that precedes it in that NP
    """
    result=False

    i_pos = __get_pos__(fs.article, fs.sentence, fs.offset_begin, fs.offset_end)
    j_pos = __get_pos__(fs.article, fs.sentence_ref, fs.offset_begin_ref, fs.offset_end_ref)

    if i_pos.startswith('NN') and j_pos.startswith('NN'):
        #identify the parent tree (=NP)
        parent_i = __get_parent_tree__(fs.token,TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence)])
        parent_j = __get_parent_tree__(fs.token_ref,TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence_ref)])

        #clean up the tokens so we can find them in the tree (same operations as in get parent tree)
        i_treecleaned=fs.token.split('_')[0]
        i_treecleaned=re.sub(r'O\'|d\'|;T','',re.sub(r'\'s$','',re.sub(r'[^\w\s.]+$','',re.sub(r'^[^\w\s-]+','',i_treecleaned))))
        i_treecleaned=re.sub(r'Bond/|/ABC','',i_treecleaned)
        if i_treecleaned=='':
            i_treecleaned='&'
        elif i_treecleaned=='AMP' and i_treecleaned not in parent_i.leaves():
            i_treecleaned='&AMP'
        elif i_treecleaned not in parent_i.leaves():
            i_treecleaned=parent_i.leaves()[0]  #this a way to return False if we can't find the word in the tree

        j_treecleaned=fs.token_ref.split('_')[0]
        j_treecleaned=re.sub(r'O\'|d\'|;T','',re.sub(r'\'s$','',re.sub(r'[^\w\s.]+$','',re.sub(r'^[^\w\s-]+','',j_treecleaned))))
        j_treecleaned=re.sub(r'Bond/|/ABC','',j_treecleaned)
        if j_treecleaned=='':
            j_treecleaned='&'
        elif j_treecleaned=='AMP' and j_treecleaned not in parent_j.leaves():
            j_treecleaned='&AMP'
        elif j_treecleaned not in parent_j.leaves():
            j_treecleaned=parent_j.leaves()[0]  #this a way to return False if we can't find the word in the tree

        if i_treecleaned != parent_i.leaves()[0] and j_treecleaned != parent_j.leaves()[0]:

            #convert everything to lowercase
            lowercase_leaves_i=parent_i.leaves()
            lowercase_leaves_j=parent_j.leaves()

            for p,word in enumerate(lowercase_leaves_i):
                lowercase_leaves_i[p] = lowercase_leaves_i[p].lower()

            for q,word in enumerate(lowercase_leaves_j):
                lowercase_leaves_j[q] = lowercase_leaves_j[q].lower()

            #look at all the words that precede i and j and see if one is a subset of the other
            leaves_i_before_token = set(lowercase_leaves_i[:lowercase_leaves_i.index(i_treecleaned.lower())]).difference(NONCONTENT_SET)
            leaves_j_before_token = set(lowercase_leaves_j[:lowercase_leaves_j.index(j_treecleaned.lower())]).difference(NONCONTENT_SET)
            if len(leaves_i_before_token)>0 and len(leaves_j_before_token)>0: #nec. b/c empty subset is a subset of any set
                if leaves_i_before_token.issubset(leaves_j_before_token) or \
                        leaves_j_before_token.issubset(leaves_i_before_token):
                    result=True

    return "modifier={}".format(result)

def pro_str(fs):
    """
    C if both NPs are pronominal and are the same string.
    """
    result=False

    i_pos=__get_pos__(fs.article,fs.sentence,fs.offset_begin,fs.offset_end)
    j_pos=__get_pos__(fs.article,fs.sentence_ref,fs.offset_begin_ref,fs.offset_end_ref)

    return "pro_str={}".format(i_pos.startswith('PRP') and j_pos.startswith('PRP') and fs.i_cleaned==fs.j_cleaned)

def pn_str(fs):
    """
    C if both NPs are proper names and are the same string.
    """
    result=False

    i_pos=__get_pos__(fs.article,fs.sentence,fs.offset_begin,fs.offset_end)
    j_pos=__get_pos__(fs.article,fs.sentence_ref,fs.offset_begin_ref,fs.offset_end_ref)

    return "pro_str={}".format(i_pos.startswith('NNP') and j_pos.startswith('NNP') and fs.i_cleaned==fs.j_cleaned)

def pn_substr(fs):
    """
    C if both NPs are proper names and one NP is a proper substring (w.r.t. content words
    only) of the other; else I.
    """
    result=False

    i_pos=__get_pos__(fs.article,fs.sentence,fs.offset_begin,fs.offset_end)
    j_pos=__get_pos__(fs.article,fs.sentence_ref,fs.offset_begin_ref,fs.offset_end_ref)

    if i_pos=='NNP' and j_pos=='NNP':
        if word_overlap(fs).endswith('True'):
            result=True

    return "pn_substr={}".format(result)

def words_str(fs):
    """
    C if both NPs are non-pronominal and are the same string.
    """
    result=False

    i_pos=__get_pos__(fs.article,fs.sentence,fs.offset_begin,fs.offset_end)
    j_pos=__get_pos__(fs.article,fs.sentence_ref,fs.offset_begin_ref,fs.offset_end_ref)

    return "words_str={}".format(not i_pos.startswith('PRP') and not j_pos.startswith('PRP') and fs.i_cleaned==fs.j_cleaned)

def words_substr(fs):
    """
    C if both NPs are non-pronominal and one NP is a proper substring (w.r.t. content words
    only) of the other; else I.
    """
    result=False

    i_pos=__get_pos__(fs.article,fs.sentence,fs.offset_begin,fs.offset_end)
    j_pos=__get_pos__(fs.article,fs.sentence_ref,fs.offset_begin_ref,fs.offset_end_ref)

    if not i_pos.startswith('PRP') and not j_pos.startswith('PRP'):
        if word_overlap(fs).endswith('True'):
            result=True

    return "words_substr={}".format(result)

def soon_str_nonpro(fs):
    """
    C if both NPs are non-pronominal and the string of NP matches that of NP; else I.
    """
    i_pos=__get_pos__(fs.article,fs.sentence,fs.offset_begin,fs.offset_end)
    j_pos=__get_pos__(fs.article,fs.sentence_ref,fs.offset_begin_ref,fs.offset_end_ref)

    return "soon_str_nonpro={}".format(not i_pos.startswith('PRP') and not j_pos.startswith('PRP') and string_match(fs).endswith('True'))

def both_definites(fs):
    """
    C if both NPs start with "the." Same as def_np, except it applies to both markables.
    """

    parent_i = __get_parent_tree__(fs.token,TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence)])
    parent_j = __get_parent_tree__(fs.token_ref,TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence_ref)])

    i_def=parent_i.node=='NP' and parent_i.leaves()[0].lower()=='the'
    j_def=parent_j.node=='NP' and parent_j.leaves()[0].lower()=='the'

    return "both_definites={}".format(i_def and j_def)

def definite_1(fs):
    """
    Y if NP1 starts with the; else N.
    """

    parent_i = __get_parent_tree__(fs.token,TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence)])

    i_def=parent_i.node=='NP' and parent_i.leaves()[0].lower()=='the'

    return "definite_1={}".format(i_def)

def both_embedded(fs):
    """
    C if both NPs are prenominal modifiers.
    Approach:
        - look at 2 tokens ahead of i and j and see if either of them are nouns (the tree approach didn't work)
    """
    i_embedded=False
    j_embedded=False

    sent_i=POS_DICTIONARY[fs.article +".raw"][int(fs.sentence)]
    sent_j=POS_DICTIONARY[fs.article +".raw"][int(fs.sentence_ref)]

    #see if there is a noun within 2 words after i
    p=int(fs.offset_end)

    while p<int(fs.offset_end)+2 and p<len(sent_i) and i_embedded==False:

        if sent_i[p][-1].startswith('NN'):
            i_embedded=True
        p+=1

    #see if there is a noun within 2 words after j
    q=int(fs.offset_end_ref)

    while q<int(fs.offset_end_ref)+2 and q<len(sent_j) and j_embedded==False:

        if sent_j[q][-1].startswith('NN'):
            j_embedded=True
        q+=1

    return "both_embedded={}".format(i_embedded and j_embedded)

def embedded_1(fs):
    """
    C if the first NP is a prenominal modifier.
    Approach:
        - look at 2 tokens ahead of i and see if either of them are nouns (the tree approach didn't work)
    """
    i_embedded=False

    sent_i=POS_DICTIONARY[fs.article +".raw"][int(fs.sentence)]

    #see if there is a noun within 2 words after i
    p=int(fs.offset_end)

    while p<int(fs.offset_end)+2 and p<len(sent_i) and i_embedded==False:

        if sent_i[p][-1].startswith('NN'):
            i_embedded=True
        p+=1

    return "embedded_1={}".format(i_embedded)

def embedded_2(fs):
    """
    C if the second NP is a prenominal modifier.
    Approach:
        - look at 2 tokens ahead of j and see if either of them are nouns (the tree approach didn't work)
    """
    j_embedded=False

    sent_j=POS_DICTIONARY[fs.article +".raw"][int(fs.sentence_ref)]

    #see if there is a noun within 2 words after j
    p=int(fs.offset_end_ref)

    while p<int(fs.offset_end_ref)+2 and p<len(sent_j) and j_embedded==False:

        if sent_j[p][-1].startswith('NN'):
            j_embedded=True
        p+=1

    return "embedded_2={}".format(j_embedded)

def both_pronouns(fs):
    """C if both markables are pronouns"""
    i_pos=__get_pos__(fs.article,fs.sentence,fs.offset_begin,fs.offset_end)
    j_pos=__get_pos__(fs.article,fs.sentence_ref,fs.offset_begin_ref,fs.offset_end_ref)
    return "both_pronouns={}".format(i_pos.startswith('PRP') and j_pos.startswith('PRP'))

def __pos_by_index__(fname,sent_num,start_index):
    """from Anya, just changed the +.raw part. WORKS"""
    fname += ".raw"
    sent_num=int(sent_num)
    start_index=int(start_index)
    sent=POS_DICTIONARY[fname][sent_num]
    if start_index < len(sent):
        word=sent[start_index]
        pos=word[1]
    else:
        pos="none"
    return pos

def contains_pn(fs):
    """
    I if both NPs are not proper names but contain proper names that mismatch on every word; else C.
    """
    result=False

    #print fs.token, '\t', fs.token_ref

    i_pos=__get_pos__(fs.article,fs.sentence,fs.offset_begin,fs.offset_end)
    j_pos=__get_pos__(fs.article,fs.sentence_ref,fs.offset_begin_ref,fs.offset_end_ref)

    if i_pos!='NNP' or j_pos!='NNP':
        parent_i = __get_parent_tree__(fs.token,TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence)])
        parent_j = __get_parent_tree__(fs.token_ref,TREES_DICTIONARY[fs.article+".raw"][int(fs.sentence_ref)])
        #print parent_i.__repr__()
        #print parent_j.__repr__()
        leaves_i=parent_i.leaves()
        leaves_j=parent_j.leaves()

        i_NNP=[] #collect all the proper names in NPi
        for word in leaves_i:
            start_index_i = leaves_i.index(word)
            #pos=__pos_by_index__(fs.article,fs.sentence,start_index_i)
            pos=parent_i[parent_i.leaf_treeposition(start_index_i)[:-1]].node
            #print word, '\t', pos
            if pos.startswith('NNP'):
                i_NNP.append(word)
        i_NNP=set(i_NNP)

        j_NNP=[] #collect all the proper names in NPj
        #print "============="
        for word in leaves_j:
            start_index_j = leaves_j.index(word)
            #pos=__pos_by_index__(fs.article,fs.sentence_ref,start_index_j)
            pos=parent_j[parent_j.leaf_treeposition(start_index_j)[:-1]].node
            #print word, '\t', pos
            if pos.startswith('NNP'):
                j_NNP.append(word)
        j_NNP=set(j_NNP)

        #if two sets of proper names do not overlap (i.e. mismatch on every word)
        if len(i_NNP)>0 and len(j_NNP)>0 and len(i_NNP.intersection(j_NNP))<1:
            result=True

    #print result
    #print
    #print
    return "contains_pn={}".format(result)

def proper_noun(fs):
    """
    I if both NPs are proper names, but mismatch on every word; else C.
    """
    i_pos=__get_pos__(fs.article,fs.sentence,fs.offset_begin,fs.offset_end)
    j_pos=__get_pos__(fs.article,fs.sentence_ref,fs.offset_begin_ref,fs.offset_end_ref)
    return "proper_noun={}".format(i_pos.startswith('NNP') and j_pos.startswith('NNP') and string_match(fs).endswith('False'))

def title(fs):
    """
    I if one or both of the NPs is a title; else C.
    """
    return "title={}".format(fs.i_cleaned in TITLE_SET or fs.j_cleaned in TITLE_SET)

def title_per(fs):
    """
    True if one is a title and the other is a person.
    """
    result=(fs.i_cleaned in TITLE_SET and fs.entity_type_ref=='PER') or (fs.j_cleaned in TITLE_SET and fs.entity_type=='PER')
    return "title_per={}".format(result)

def wndist(fs):
    """
    Distance between NP1 and NP2 in WordNet (using the first sense only)
    """

    wndist=-100000

    i_pos=__get_pos__(fs.article,fs.sentence,fs.offset_begin,fs.offset_end)
    j_pos=__get_pos__(fs.article,fs.sentence_ref,fs.offset_begin_ref,fs.offset_end_ref)

    #print "Orig:", fs.token, '\t', fs.token_ref

    if i_pos.startswith('NN') and j_pos.startswith('NN') and not i_pos.endswith('P') and not j_pos.endswith('P'):
        # considering only common nouns
        lemmatizer = nltk.WordNetLemmatizer()
        i=lemmatizer.lemmatize(fs.i_cleaned, pos='n')
        j=lemmatizer.lemmatize(fs.j_cleaned, pos='n')
        synsets_i=wn.synsets(i)
        synsets_j=wn.synsets(j)
        if len(synsets_i)>0 and len(synsets_j)>0:
            wn_sense1_i=synsets_i[0]
            wn_sense1_j=synsets_j[0]
            wn_pos_i=str(wn_sense1_i).split('.')[1]
            wn_pos_j=str(wn_sense1_j).split('.')[1]
            if wn_pos_i==wn_pos_j:
                wndist=wn_sense1_i.lch_similarity(wn_sense1_j)
                wndist=(ceil(wndist * 100) / 100.0)
                #print "Lemmatized:", i, '\t', j, '\t', str(wndist)

    #print
    #print

    return "wndist={}".format(wndist)

        
##################
# keelan's stuff #
##################
    
def rule_resolve(fs):
    dcoref = COREF_DICTIONARY[fs.article]
    for group in dcoref:
        found_i = False
        found_j = False
        for referent in group:
            if _coref_helper(referent, fs.sentence, fs.offset_begin, fs.offset_end, fs.i_cleaned):
                found_i = True
            if _coref_helper(referent, fs.sentence_ref, fs.offset_begin_ref, fs.offset_end_ref, fs.j_cleaned):
                found_j = True

            if found_i and found_j:
                return "rule_resolve=True"

    return "rule_resolve=False"

def _coref_helper(i, sentence, offset_begin, offset_end, cleaned):
    """heuristically, i[2] and i[3] will have a later index, especially i[3]"""
    cleaned = cleaned.replace("_", " ")
    return i[1] == sentence and \
           i[2]-2 <= offset_begin <= i[2] and \
           i[3]-3 <= offset_end <= i[3]

def pro_resolve(fs):
    dcoref = COREF_DICTIONARY[fs.article]
    i_pos_tag = __get_pos__(fs.article, fs.sentence, fs.offset_begin, fs.offset_end)
    j_pos_tag = __get_pos__(fs.article, fs.sentence_ref, fs.offset_begin_ref, fs.offset_end_ref)
    if not ("PRP" in i_pos_tag or "PRP" in j_pos_tag):
        return "pro_resolve=False"
    for group in dcoref:
        found_i = False
        found_j = False
        for referent in group:
            if "PRP" in i_pos_tag:
                if fs.sentence == referent[1] and fs.i_cleaned in referent[0]:
                    found_i = True
            elif _coref_helper(referent, fs.sentence, fs.offset_begin, fs.offset_end, fs.i_cleaned):
                found_i = True

            if "PRP" in j_pos_tag:
                if fs.sentence_ref == referent[1] and fs.j_cleaned in referent[0]:
                    found_j = True
            elif _coref_helper(referent, fs.sentence_ref, fs.offset_begin_ref, fs.offset_end_ref, fs.j_cleaned):
                found_j = True

            if found_i and found_j:
                return "pro_resolve=True"

    return "pro_resolve=False"

