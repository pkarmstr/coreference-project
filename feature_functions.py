
from file_reader import TREES_DICTIONARY, POS_DICTIONARY, RAW_DICTIONARY, PRONOUN_LIST, NONCONTENT_SET, FeatureRow
import re, os, nltk
from nltk.corpus import names
from nltk.corpus import wordnet as wn
from nltk.tree import ParentedTree

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
    """applies only to j (the second markable; this probably means the LATER one, not the right-hand side one)
        Its possible values are true or false. In our definition, a definite noun phrase is a noun phrase that
        starts with the word the. For example, the car is a definite noun phrase. If j is a definite noun phrase,
        return true; else return false."""

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


################
# Julia's stuff #
################

def dem_token(feats):
    """WORKS!"""
    dem_re = re.findall(r"these|this|that|those",feats.j_cleaned) #yes, only j!
    return "dem_token={}".format(len(dem_re) > 0)

def dem_np(feats):
    fname = feats.article +".raw"
    sent=POS_DICTIONARY[fname][feats.sentence_ref]
    if feats.offset_begin_ref>3:
        window = sent[feats.offset_begin_ref-3:feats.offset_begin_ref+1]
    else:
        window = sent[0:feats.offset_begin_ref+1]
    dems=set('this','these','that','those')
    match = dems.intersection(set(window))
    return "dem_j={}".format(len(match)>0)



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


def entity_type_agreement(feats):
    ##intuition similar to sem_class agreement (not implemented)
    """WORKS"""
    i_entity_type = feats.entity_type
    j_entity_type = feats.entity_type_ref
    return "entity_type_agreement={}".format(i_entity_type == j_entity_type)



def apposition(feats): #this was driving me MAD....I SHOULD CORRECT THE STYLE...aarrrrggghhshs
    """WORKS WITH THE EXAMPLES IN UNITTEST, HOPE THEY WERE NOT A COINDIDENCE"""
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

    parent_tree=t[position_tuple[:-2]]
    return parent_tree


def __is_subject__(curr_tree,token, parent):
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
            else:
                found = __is_subject__(child,token, parent)
        if found:
            break
    return found

    ######FOR PREVIOUS FUNCTION, WITHOUT THE GIVEN PARENT
    ##found = False
    #for child in curr_tree:
    #    if isinstance(child, ParentedTree):
    #        conditions = token in "_".join(child.leaves()) and curr_tree.node == "NP"
    #        if conditions:
    #            left_brother = curr_tree.left_sibling()
    #            right_brother = curr_tree.right_sibling()
    #            if isinstance(left_brother, ParentedTree): #SOV
    #                if left_brother.node == "VP":
    #                    found = True
    #            if isinstance(right_brother,ParentedTree): #OVS
    #                if right_brother.node == "VP":
    #                    found = True
    #        else:
    #            found = __is_subject__(child,token)
    #    if found:
    #        break
    #return found



def i_is_subject(feats):
    sentence_tree = TREES_DICTIONARY[feats.article+".raw"][int(feats.sentence_ref)]
    ptree = ParentedTree.convert(sentence_tree)
    parent = __get_parent_tree__(feats.token, ptree)
    i_subject = __is_subject__(ptree,feats.token)
    return "i_is_subject={}".format(i_subject)

def j_is_subject(feats):
    sentence_tree = TREES_DICTIONARY[feats.article+".raw"][int(feats.sentence_ref)]
    ptree = ParentedTree.convert(sentence_tree)
    parent = __get_parent_tree__(feats.token_ref, ptree)
    j_subject = __is_subject__(ptree,feats.token_ref)
    return "j_is_subject={}".format(j_subject)

def both_subjects(feats):
    both_bool = i_is_subject(feats).endswith("True") and j_is_subject(feats).endswith("True")
    return "both_subjects={}".format(both_bool)


def none_is_subject(feats):
    none_bool = i_is_subject(feats).endswith("False") and j_is_subject(feats).endswith("False")
    return "none_is_subject={}".format(none_bool)

def animacy_agreement(feats):
    both_people = feats.entity_type == "PER" and feats.entity_type_ref == "PER"
    both_not_people = feats.entity_type != "PER" and feats.entity_type_ref != "PER"
    return "animacy_agreement={}".format(both_people or both_not_people)

def same_max_NP(feats):
    if feats.sentence !=  feats.sentence_ref:
        return "same_max_NP={}".format(False)
    else:
        sentence_tree = TREES_DICTIONARY[feats.article+".raw"][int(feats.sentence)]
        ptree = ParentedTree.convert(sentence_tree)
        parent1 = __get_parent_tree__(feats.token, ptree)
        parent2 = __get_parent_tree__(feats.token_ref, ptree)
        max_p_i = __get_max_projection__(ptree,parent1)
        max_p_j = __get_max_projection__(ptree, parent2)
        both_NPs = max_p_i.node == "NP" and max_p_j.node == "NP"
        return "same_max_NP={}".format(max_p_i == max_p_j and both_NPs)



def __get_max_projection__(bigger_tree,target_tree):
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



def is_pred_nominal(feats):
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
    if feats.sentence != feats.sentence_ref:
        return "span={}".format(False)
    else:
        s_tree = ParentedTree.convert(TREES_DICTIONARY[feats.article+".raw"][int(feats.sentence)])
        i_parent = __get_parent_tree__(feats.token, s_tree)
        j_parent = __get_parent_tree__(feats.token_ref,s_tree)
        return "span={}".format(i_parent==j_parent)













    #OTHER VERSION, DIDN'T REMOVE IT JUST IN CASE
    #def is_j_apposition(curr_tree):
    #    found = False
    #    for child in curr_tree:
    #        if isinstance(child,ParentedTree):
    #            found = is_j_apposition(child)
    #            if found:
    #                break
    #        else: #a leaf
    #            if curr_tree.leaves() == feats.j_cleaned.split("_"):
    #                parent = curr_tree.parent()
    #                leaf_is_noun = curr_tree.node=="NN" or curr_tree == "NNS"
    #                if leaf_is_noun:
    #                    available_elders = isinstance(parent,ParentedTree) and \
    #                                       isinstance(parent.parent(),ParentedTree)
    #                    if available_elders:
    #                        if parent.node== "NP":
    #                            greatuncle = parent.parent().left_sibling()
    #                            if isinstance(greatuncle,ParentedTree):
    #                                previous_words = greatuncle.parent().leaves()
    #                                meets_constraits = greatuncle.node == "," and i_head in previous_words
    #                                if meets_constraits:
    #                                    found = True
    #            if found:
    #                break
    #    return found
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
    """applies only to j (the second markable; this probably means the LATER one, not the right-hand side one)
        Its possible values are true or false. In our definition, a definite noun phrase is a noun phrase that
        starts with the word the. For example, the car is a definite noun phrase. If j is a definite noun phrase,
        return true; else return false."""

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