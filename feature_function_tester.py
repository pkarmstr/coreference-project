__author__ = 'keelan'

import unittest
from feature_functions import *
from feature_functions import __determine_number__, __determine_gender__
from file_reader import RAW_DICTIONARY, POS_DICTIONARY, TREES_DICTIONARY, PRONOUN_LIST
from feature_functions import __determine_number__, __determine_gender__, __is_subject__, __get_parent_tree__, \
    __pos_match__, def_np, def_np_pos_match, __get_sem_class__
from file_reader import RAW_DICTIONARY, POS_DICTIONARY, TREES_DICTIONARY, PRONOUN_LIST, FeatureRow

class FeatureTest(unittest.TestCase):

    def setUp(self):
        self.article_title = "NYT20001230.1309.0093.head.coref.raw"

    ##quick note: in each line i have added manually the corresponding i_cleaned and j_cleaned before the coref-label.
    def test_dem_token(self):
        #this line does not exist in the data, but it would be the perfect example for the feature
        line1 = "NYT20001102.1839.0340.head.coref 17 2 3 PER candidates 30 8 9 PER those candidates those no".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001111.1247.0093.head.coref 19 5 7 LOC West_Bank 21 32 33 GPE city West_Bank city no".rstrip().split()
        feats2 = FeatureRow(*line2)
        self.assertEqual(dem_token(feats1).endswith("True"),True)
        self.assertEquals(dem_token(feats2).endswith("False"),True)

    def dem_np(self):
        line1 = "NYT20001111.1247.0093.head.coref 7 13 14 LOC area 13 5 6 PER they area they no".rstrip().split()
        feats1 = FeatureRow(*line1)
        self.assertEqual(dem_np(feats1).endswith("True"),True)

    def test__determine_number__(self):
        line1 = "NYT20001111.1247.0093.head.coref 13 5 6 PER they 15 12 13 WEA rifles they rifles no".rstrip().split()
        feats1=FeatureRow(*line1)
        #print determine_number(feats1.article,feats1.sentence,feats1.i_cleaned,feats1.offset_begin,feats1.offset_end)
        self.assertEqual(__determine_number__(feats1.article,feats1.sentence,feats1.i_cleaned,
                                          feats1.offset_begin,feats1.offset_end),"plural")
        line2 = "NYT20001111.1247.0093.head.coref 19 5 7 LOC West_Bank 21 32 33 GPE city West_Bank city no".rstrip().split()
        feats2 = FeatureRow(*line2)
        self.assertEqual(__determine_number__(feats2.article,feats2.sentence,feats2.i_cleaned,
                                          feats2.offset_begin,feats2.offset_end),"singular")

    def test_number_agreement(self):
        line1 = "NYT20001111.1247.0093.head.coref 13 5 6 PER they 15 12 13 WEA rifles they rifles no".rstrip().split()
        feats1=FeatureRow(*line1)
        line2 = "NYT20001111.1247.0093.head.coref 15 6 7 PER crowd 15 12 13 WEA rifles crowd rifles no".rstrip().split()
        feats2 = FeatureRow(*line2)
        self.assertEqual(number_agreement(feats1).endswith("True"),True)
        self.assertEqual(number_agreement(feats2).endswith("False"),True)

    def test_both_proper_names(self):
        line1 = "NYT20001111.1247.0093.head.coref 13 23 25 GPE Gush_Katif 15 12 13 WEA rifles Gush_Katif rifles no".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001019.2136.0319.head.coref 25 16 17 GPE Alaska 25 20 21 GPE Texas Alaska Texas no".rstrip().split()
        feats2 = FeatureRow(*line2)
        self.assertEqual(both_proper_name(feats1).endswith("False"),True)
        self.assertEqual(both_proper_name(feats2).endswith("True"),True)

    def test__determine_gender__(self):
        line1 = "NYT20001019.2136.0319.head.coref 8 0 3 PER George_W._Bush 26 8 9 GPE Texas George_W._Bush Texas no".rstrip().split()
        feats1= FeatureRow(*line1)
        line2 = "NYT20001020.2144.0366.head.coref 12 24 25 PER she 13 0 1 ORG Associates she Associates no".rstrip().split()
        feats2 = FeatureRow(*line2)

        self.assertEqual(__determine_gender__(feats1.article, feats1.sentence, feats1.i_cleaned, feats1.offset_begin,
                                          feats1.offset_end, feats1.entity_type), "male") #George Bush
        self.assertEqual(__determine_gender__(feats2.article, feats2.sentence, feats2.i_cleaned, feats2.offset_begin,
                                          feats2.offset_end, feats2.entity_type), "female")

    def test_gender_agreement(self):
        line1 = "NYT20001023.2203.0479.head.coref 16 9 10 PER his 32 15 16 PER Andrew his Andrew no".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001023.2203.0479.head.coref 17 10 11 PER governor 32 15 16 PER Andrew governor Andrew no".rstrip().split()
        feats2 = FeatureRow(*line2)
        self.assertEqual(gender_agreement(feats1).endswith("True"),True)
        self.assertEqual(gender_agreement(feats2).endswith("unknown"),True)

    def test_alias(self):
        #i have to make up these examples, nothing similiar in dev set...
        line1 ="NYT20001103.2226.0443.head.coref 21 14 16 PER Irma_Levin 21 0 1 PER Levin Irma_Levin Levin yes".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 ="NYT20001103.2226.0443.head.coref 21 14 16 ORG International_Business_Machines_Corp. 21 0 1 ORG IBM International_Business_Machines_Corp. IBM yes".rstrip().split()
        feats2 = FeatureRow(*line2)
        self.assertEqual(alias(feats1).endswith("True"),True)
        self.assertEqual(alias(feats2).endswith("True"),True)

    def test_entity_type_agreement(self):
        line1 = "NYT20001111.1247.0093.head.coref 9 27 29 LOC West_Bank 21 0 1 PER Mohtaseb West_Bank Mohtaseb no".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001023.2203.0479.head.coref 17 10 11 PER governor 32 15 16 PER Andrew governor Andrew no".rstrip().split()
        feats2 = FeatureRow(*line2)
        self.assertEqual(entity_type_agreement(feats1).endswith("False"),True)
        self.assertEqual(entity_type_agreement(feats2).endswith("True"),True)

    def test_apposition(self):
        line1 = "NYT20001020.2025.0304.head.coref 26 26 28 PER Mark_Madden 26 29 30 PER manager Mark_Madden manager yes".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001020.2025.0304.head.coref 31 1 3 PER Howard_Klein 31 6 7 PER broker Howard_Klein broker yes".rstrip().split()
        feats2 = FeatureRow(*line2)
        line3 = "NYT20001027.1622.0218.head.coref 8 12 13 PER spokesman 8 14 16 PER Mark_Murray spokesman Mark_Murray yes".rstrip().split()
        feats3 = FeatureRow(*line3)
        self.assertEqual(apposition(feats1).endswith("True"),True)
        self.assertEqual(apposition(feats2).endswith("True"),True)
        self.assertEqual(apposition(feats3).endswith("True"),True)

    def test__is_subject__(self):
        line1 = "NYT20001102.1839.0338.head.coref 9 16 17 PER he 18 7 8 ORG itself he itself no".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001102.1839.0338.head.coref 12 3 4 PER Levitt 18 7 8 ORG itself Levitt itself no".rstrip().split()
        feats2 = FeatureRow(*line2)
        line3 = "NYT20001102.1839.0338.head.coref 20 32 33 PER brokers 32 19 20 PER clients brokers clients no".rstrip().split()
        feats3 = FeatureRow(*line3)
        line4 = "NYT20001102.1839.0338.head.coref 20 33 34 PER who 32 19 20 PER clients who clients no".rstrip().split()
        feats4 = FeatureRow(*line4)
        tree1_i = ParentedTree.convert(TREES_DICTIONARY[feats1.article+".raw"][int(feats1.sentence)])
        tree1_j = ParentedTree.convert(TREES_DICTIONARY[feats1.article+".raw"][int(feats1.sentence_ref)])
        tree2_i = ParentedTree.convert(TREES_DICTIONARY[feats2.article+".raw"][int(feats2.sentence)])
        tree3_i = ParentedTree.convert(TREES_DICTIONARY[feats3.article+".raw"][int(feats3.sentence)])
        tree4_i = ParentedTree.convert(TREES_DICTIONARY[feats4.article+".raw"][int(feats4.sentence)])
        parent1_i = __get_parent_tree__(feats1.token, tree1_i)
        parent1_j = __get_parent_tree__(feats1.token_ref, tree1_j)
        parent2_i = __get_parent_tree__(feats2.token, tree2_i)
        parent3_i = __get_parent_tree__(feats3.token, tree3_i)
        parent4_i = __get_parent_tree__(feats4.token, tree4_i)
        self.assertEqual(__is_subject__(tree1_i,feats1.token, parent1_i,tree1_i),True)
        self.assertEqual(__is_subject__(tree1_j,feats1.token_ref,parent1_j,tree1_j),False)
        self.assertEqual(__is_subject__(tree2_i,feats2.token, parent2_i,tree2_i),True)
        self.assertEqual(__is_subject__(tree3_i,feats3.token, parent3_i,tree3_i),False)
        self.assertEqual(__is_subject__(tree4_i,feats4.token, parent4_i,tree4_i),True)

    def test_i_is_subject(self):
        line1 = "NYT20001102.1839.0338.head.coref 9 16 17 PER he 18 7 8 ORG itself he itself no".rstrip().split()
        feats1 = FeatureRow(*line1)
        self.assertEqual(i_is_subject(feats1).endswith("True"),True)

    def test_j_is_subject(self):
        line1 = "NYT20001027.1622.0218.head.coref 10 14 15 PER perpetrators 12 7 8 ORG we perpetrators we no".rstrip().split()
        feats1 = FeatureRow(*line1)
        self.assertEqual(j_is_subject(feats1).endswith("True"),True)

    def test_both_subjects(self):
        line1 = "NYT20001027.1622.0218.head.coref 12 24 26 PER Roberta_Burroughs 14 0 1 PER Ballmer Roberta_Burroughs Ballmer no".rstrip().split()
        feats1 = FeatureRow(*line1)
        self.assertEqual(j_is_subject(feats1).endswith("True"),True)
        self.assertEqual(i_is_subject(feats1).endswith("True"),True)
        self.assertEqual(both_subjects(feats1).endswith("True"), True)

    def test_none_is_subject(self):
        line1 = "NYT20001027.1622.0218.head.coref 13 13 14 GPE Sweden 13 35 36 ORG our Sweden our no ".rstrip().split()
        feats1 = FeatureRow(*line1)
        self.assertEqual(none_is_subject(feats1).endswith("True"),True)


    def test_animacy_agreement(self):
        line1 = "NYT20001111.1247.0093.head.coref 9 27 29 LOC West_Bank 21 0 1 PER Mohtaseb West_Bank Mohtaseb no".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001020.2025.0304.head.coref 31 1 3 PER Howard_Klein 31 6 7 PER broker Howard_Klein broker yes".rstrip().split()
        feats2 = FeatureRow(*line2)
        line3= "NYT20001111.1247.0093.head.coref 13 23 25 GPE Gush_Katif 15 12 13 WEA rifles Gush_Katif rifles no".rstrip().split()
        feats3 = FeatureRow(*line3)
        self.assertEqual(animacy_agreement(feats1).endswith("False"),True)
        self.assertEqual(animacy_agreement(feats2).endswith("True"),True)
        self.assertEqual(animacy_agreement(feats3).endswith("True"),True)


    def test_same_max_NP(self):
        line1 = "NYT20001111.1247.0093.head.coref 24 3 4 PER photographer 24 5 7 PER Yola_Monakhov photographer Yola_Monakhov yes".rstrip().split()
        feats1 = FeatureRow(*line1)
        #line2 = "NYT20001019.2136.0319.head.coref 8 0 3 PER George_W._Bush 8 5 6 PER guest George_W._Bush guest yes".rstrip().split()
        #feats2 = FeatureRow(*line2)
        #print same_max_NP(feats2)
        self.assertEqual(same_max_NP(feats1).endswith("True"),True)

    def test_predicate_nominal(self):
        line1 = "NYT20001027.2150.0417.head.coref 22 0 1 GPE Canada 22 2 3 GPE home Canada home yes".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001111.1247.0093.head.coref 24 3 4 PER photographer 24 5 7 PER Yola_Monakhov photographer Yola_Monakhov yes".rstrip().split()
        feats2 = FeatureRow(*line2)
        self.assertEqual(is_pred_nominal(feats1).endswith("True"),True)
        self.assertEqual(is_pred_nominal(feats2).endswith("False"),True)

    def test_span(self):
        line1 = "NYT20001111.1033.0046.head.coref 13 21 22 PER voters 13 20 21 PER Asian voters Asian no".rstrip().split()
        feats1 = FeatureRow(*line1)
        self.assertEqual(span(feats1).endswith("True"),True)


    def test_def_np(self):
        line1 = "NYT20001111.1247.0093.head.coref 7 13 14 LOC area 13 5 6 PER they area they no".rstrip().split()
        line2 = "APW20001110.1844.0453.head.coref 6 7 8 PER witness 4 14 15 PER Jewish witness Jewish no".rstrip().split()
        fs1 = FeatureRow(*line1)
        fs2 = FeatureRow(*line2)
        self.assertEqual(def_np(fs1).endswith("False"),True)
        self.assertEqual(def_np(fs2).endswith("True"),True)

    def test_def_np_pos_match(self):
        line1 = "NYT20001111.1247.0093.head.coref 7 13 14 LOC area 13 5 6 PER they area they no".rstrip().split()
        line2 = "APW20001110.1844.0453.head.coref 20 1 2 PER lawyer 21 11 12 FAC hide-out lawyer hide-out no".rstrip().split()
        fs1 = FeatureRow(*line1)
        fs2 = FeatureRow(*line2)
        self.assertEqual(def_np_pos_match(fs1).endswith("False"),True)
        self.assertEqual(def_np(fs2).endswith("False") and __pos_match__(fs2),True)

    def test_word_overlap(self):
        line1 = "NYT20001111.1247.0093.head.coref 7 13 14 LOC area 13 5 6 PER they area they no".rstrip().split()
        line2 = "APW20001110.1844.0453.head.coref 20 1 2 PER lawyer 21 11 12 FAC hide-out lawyer hide-out no".rstrip().split()
        fs1 = FeatureRow(*line1)
        fs2 = FeatureRow(*line2)
        self.assertEqual(word_overlap(fs1).endswith("False"),True)
        self.assertEqual(word_overlap(fs2).endswith("False"),True)

    def test_could_be_coindexed(self):
        line1 = "NYT20001020.2144.0366.head.coref 11 15 16 PER executive 11 17 18 ORG Associates executive Associates no".rstrip().split()
        feats1 = FeatureRow(*line1)
        self.assertEqual(could_be_coindexed(feats1).endswith("False"),True)

    def test_compatible_syntax(self):
        line1 = "NYT20001111.1033.0046.head.coref 15 14 15 PER majority 19 20 21 PER Gore majority Gore no".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001111.1033.0046.head.coref 15 14 15 PER majority 15 16 17 PER women majority women no".rstrip().split()
        feats2 = FeatureRow(*line2)
        self.assertEqual(compatible_syntax(feats1).endswith("True"),True)
        self.assertEqual(compatible_syntax(feats2).endswith("False"),True)

    def test_j_indefinite(self):
        line1 = "NYT20001111.1033.0046.head.coref 15 0 1 PER Bush 15 16 17 PER women Bush women no".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001027.1622.0218.head.coref 8 12 13 PER spokesman 8 14 16 PER Mark_Murray spokesman Mark_Murray yes".rstrip().split()
        feats2 = FeatureRow(*line2)
        self.assertEqual(j_indefinite(feats1).endswith("True"),True)
        self.assertEqual(j_indefinite(feats2).endswith("False"),True)

    def test_i_pron_j_not_pron(self):
        line1 = "NYT20001020.2144.0366.head.coref 12 24 25 PER she 13 0 1 ORG Associates she Associates no".rstrip().split()
        feats1 = FeatureRow(*line1)
        self.assertEqual(i_pron_j_not_pron(feats1).endswith("True"),True)

    def test_meet_all_constraints(self):
        line1 = "NYT20001111.1033.0046.head.coref 26 10 11 PER Gore 30 8 9 PER Democrat Gore Democrat yes".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001111.1033.0046.head.coref 10 0 2 PER Ralph_Nader 10 3 4 PER who Ralph_Nader who yes".rstrip().split()
        feats2 = FeatureRow(*line2)
        line3 = "NYT20001111.1033.0046.head.coref 60 0 1 PER Those 60 1 2 PER who Those who yes".rstrip().split()
        feats3 = FeatureRow(*line3)
        line4 = "NYT20001019.2136.0319.head.coref 19 14 15 PER people 19 15 16 PER who people who yes".rstrip().split()
        feats4 = FeatureRow(*line4)
        self.assertEqual(meet_all_constraints(feats1).endswith("True"),True)
        self.assertEqual(meet_all_constraints(feats2).endswith("True"),True)
        self.assertEqual(meet_all_constraints(feats3).endswith("True"),True)
        self.assertEqual(meet_all_constraints(feats4).endswith("True"),True)

    def test_closest_comp(self):
        line1 = "NYT20001019.2136.0319.head.coref 8 7 8 PER Letterman 8 0 3 PER George_W._Bush Letterman George_W._Bush no".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001019.2136.0319.head.coref 8 7 8 PER Letterman 9 0 1 PER He Letterman he yes".rstrip().split()
        feats2 = FeatureRow(*line2)
        self.assertEqual(closest_comp(feats1).endswith("False"), True)
        self.assertEqual(closest_comp(feats2).endswith("False"), True)

    def test__get_sem_class__(self):
        self.assertEqual(__get_sem_class__("Obama") == "PER", True)
        self.assertEqual(__get_sem_class__("anyone")=="PER", True)
        self.assertEqual(__get_sem_class__("America")=="GPE", True)
        self.assertEqual(__get_sem_class__("warship")=="VEH", True)
        self.assertEqual(__get_sem_class__("Yemen")=="GPE", True)

    def test_nominative_case(self):
        line1 = "NYT20001023.2203.0479.head.coref 6 5 8 PER George_W._Bush 26 30 31 PER her George_W._Bush her no".rstrip().split()
        feats1 = FeatureRow(*line1)
        self.assertEqual(nominative_case(feats1).endswith("she"), True)

    def test_number_composite(self):
        line1 = "NYT20001111.1247.0093.head.coref 13 5 6 PER they 15 12 13 WEA rifles they rifles no".rstrip().split()
        feats1=FeatureRow(*line1)
        self.assertEqual(number_composite(feats1).endswith("plural-plural"), True)

    def test_gender_composite(self):
        line1 = "NYT20001023.2203.0479.head.coref 6 5 8 PER George_W._Bush 26 30 31 PER her George_W._Bush her no".rstrip().split()
        feats1 = FeatureRow(*line1)
        self.assertEqual(gender_composite(feats1).endswith("male-female"), True)

    def test_entity_composite(self):
        line1 = "NYT20001020.2144.0366.head.coref 12 24 25 PER she 13 0 1 ORG Associates she Associates no".rstrip().split()
        feats1 = FeatureRow(*line1)
        self.assertEqual(entity_composite(feats1).endswith("PER-ORG"), True)

    def test_subclass(self):
        line1 = "NYT20001020.2025.0304.head.coref 14 29 30 GPE Yemen 33 1 2 GPE country Yemen country no".rstrip().split()
        feats1 = FeatureRow(*line1)
        line2 = "NYT20001106.1705.0187.head.coref 9 17 18 GPE states 9 6 7 GPE Tennessee states Tennessee no".rstrip().split()
        feats2 = FeatureRow(*line2)
        line3 = "NYT20001106.1705.0187.head.coref 10 14 15 GPE country 19 2 3 GPE Tennessee country Tennessee no".rstrip().split()
        feats3 = FeatureRow(*line3)
        line4 = "NYT20001023.2203.0479.head.coref 15 30 31 GPE Massachusetts 15 40 41 GPE state Massachusetts state yes".rstrip().split()
        feats4 = FeatureRow(*line4)
        self.assertEqual(subclass(feats1).endswith("True"),True)
        self.assertEqual(subclass(feats2).endswith("True"),True)
        self.assertEqual(subclass(feats3).endswith("False"),True)
        self.assertTrue(subclass(feats4).endswith("True"))

    def test_rule_resolve(self):
        fs1 = FeatureRow("APW20001001.2021.0521.head.coref", 3, 16, 18, "PER", "Bashar_Assad", 4, 0, 1, "PER", "Assad", "bashar_assad", "assad", "yes")
        self.assertTrue(rule_resolve(fs1).endswith("True"))
        fs2 = FeatureRow("APW20001001.2021.0521.head.coref", 3, 36, 37, "", "Palestinian", 4, 0, 1, "", "Assad", "palestinian", "assad", "no")
        self.assertFalse(rule_resolve(fs2).endswith("True"))

    def test_pro_resolve(self):
        fs1 = FeatureRow("APW20001001.2021.0521.head.coref", 21, 0, 1, "PER", "Moussa", 22, 2, 3, "PER", "he", "moussa", "he", "yes")
        self.assertTrue(pro_resolve(fs1).endswith("True"))
        fs2 = FeatureRow("APW20001001.2021.0521.head.coref", 22, 17, 18, "GPE", "Baghdad", 22, 2, 3, "PER", "he", "baghdad", "he", "no")
        self.assertTrue(pro_resolve(fs2).endswith("False"))

if __name__ == "__main__":
    unittest.main()

