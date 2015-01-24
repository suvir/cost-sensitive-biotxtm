__author__ = 'suvir'

import nltk, csv, os
import xml.etree.ElementTree as ET
from pytrie import SortedStringTrie as trie
import token_feature_builder


class Raw2Bio:
    def __init__(self, dirname, dictpath, outputdir):
        self.dictionary = trie()
        self.input_dir = dirname  # Directory to look up files inside
        self.label = "DT"  # DT = Disease Trait, ET = Ethnicity
        self.input_mode = 'XML'
        self.dictionary_path = dictpath
        self.output_dir = outputdir
        # List of all garbage tags
        # garbage_tags = ['ref','xref','ref-list','ext-link','contrib','email','job','doi','base_name']
        self.garbage_tags = []
        self.parent_map = dict()
        self.output_writer = None
        self.debug_flag = False

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def build_features_for_training(self, root, text):
        # Given an xml tag and its relevant text/tail portion, tokenize it and calculate features of each token
        tokens = text.encode('ascii', 'ignore')
        tokens = nltk.PunktWordTokenizer().tokenize(tokens)
        match_flag = False
        prev_token = ""
        current_match = ""
        current_match_tags = []

        for this_token in tokens:
            token = this_token.lower()
            this_token = this_token.lower()
            if match_flag:
                """
                Previous tokens have matched some pattern
                """
                prefix_string = current_match + " " + token
                if len(self.dictionary.keys(prefix=prefix_string + " ")) > 0:
                    """
                    Running Match
                    """
                    current_match = current_match + " " + this_token
                    current_match_tags.append(root)
                    if self.debug_flag is True:
                        print "2.", repr(current_match), ",", token, ",", root.tag
                elif current_match in self.dictionary or prefix_string in self.dictionary:
                    """
                    Exact Match
                    """
                    current_match = current_match + " " + this_token
                    current_match_tags.append(root)

                    if self.debug_flag is True:
                        print "3.", repr(current_match), ",", token, ",", root.tag

                    tokens_to_write = current_match.split(' ')
                    self.output_writer.writerow(
                        token_feature_builder.features_for_EFO(current_match_tags[0], tokens_to_write[0]) + [
                            "B-" + self.label])
                    for i in range(1, len(tokens_to_write)):
                        self.output_writer.writerow(
                            token_feature_builder.features_for_EFO(current_match_tags[i], tokens_to_write[i]) + [
                                "I-" + self.label])

                    match_flag = False
                    current_match_tags = []
                    current_match = ""
                else:
                    if self.debug_flag is True:
                        print "4.", repr(current_match), ",", repr(prefix_string), ",", token, ",", root.tag
                    """
                    The current_match was a good sequence. This token does not need to be added to the sequence.
                    """

                    tokens_to_write = current_match.split(' ')
                    for i in range(len(tokens_to_write)):
                        self.output_writer.writerow(
                            token_feature_builder.features_for_EFO(current_match_tags[i], tokens_to_write[i]) + [
                                "O-" + self.label])

                    current_match_tags = []
                    current_match = ""
                    match_flag = False  # Running pattern has stopped

            """
            Previous tokens have not matched any pattern
            """
            if not match_flag:
                if len(self.dictionary.keys(prefix=token + " ")) > 0:
                    match_flag = True  # Running pattern has started
                    current_match += this_token
                    current_match_tags.append(root)
                    if self.debug_flag is True:
                        print "1.", token, ",", root.tag
                elif token in self.dictionary:
                    if self.debug_flag is True:
                        print "5.", current_match, ",", token, ",", root.tag
                    self.output_writer.writerow(
                        token_feature_builder.features_for_EFO(root, this_token) + ["B-" + self.label])
                else:
                    if self.debug_flag is True:
                        print "6.", current_match, ",", token, ",", root.tag
                    self.output_writer.writerow(
                        token_feature_builder.features_for_EFO(root, this_token) + ["O-" + self.label])

        """
        If code reaches here, it means that a pattern has been matched
        and the process reached the end of text
        """
        if len(current_match) > 0:
            if current_match in self.dictionary:
                if self.debug_flag is True:
                    print "7.", current_match, ",", token, ",", root.tag
                tokens_to_write = current_match.split(' ')
                self.output_writer.writerow(
                    token_feature_builder.features_for_EFO(current_match_tags[0], tokens_to_write[0]) + [
                        "B-" + self.label])
                for i in range(1, len(tokens_to_write)):
                    self.output_writer.writerow(
                        token_feature_builder.features_for_EFO(current_match_tags[i], tokens_to_write[i]) + [
                            "I-" + self.label])
            else:
                tokens_to_write = current_match.split(' ')
                for i in range(len(tokens_to_write)):
                    self.output_writer.writerow(
                        token_feature_builder.features_for_EFO(current_match_tags[i], tokens_to_write[i]) + [
                            "O-" + self.label])

    def build_features_no_training(self, root, text):
        """
        Generate features for all tokens.
        This is NOT for training - so there are no labels.
        """
        # Given an xml tag and its relevant text/tail portion, tokenize it and calculate features of each token
        tokens = text.encode('ascii', 'ignore')
        tokens = nltk.PunktWordTokenizer().tokenize(tokens)
        for token in tokens:
            self.output_writer.writerow(token_feature_builder.features_for_EFO(root, token))

    def get_text_nodes(self, root):
        if root.tag in self.garbage_tags:
            return

        if "type" in root.attrib:
            if root.attrib["type"] in ["header", "footer"]:
                return

        if root.text and not root.text.startswith('\n'):
            self.build_features_for_training(root, root.text)

        if root.tail and not root.tail.startswith('\n'):
            self.build_features_for_training(root, root.tail)

        for child in root:
            self.get_text_nodes(child)

    def build_trie(self):
        stopwords = nltk.corpus.stopwords.words('english')
        t = dict()
        f = open(self.dictionary_path)
        l = f.readlines()
        f.close()
        line_number = 1
        for line in l:
            word = line.strip().lower()
            if word not in stopwords:
                t[word] = line_number
                line_number += 1
        self.dictionary.update(t)
        print "Finished building Trie"

    def execute(self):
        self.build_trie()

        # Choose the directory for training files
        files = os.listdir(self.input_dir)

        if self.input_mode == 'XML':
            # Keep only XML files
            files = [f for f in files if f.endswith('.xml')]

            #Extract tokens and features from each file
            for f in files:
                #Open a CSV file to write in
                output = open(self.output_dir + self.label + '_' + f, 'wb')
                self.output_writer = csv.writer(output, delimiter='\t', quotechar='', escapechar='\\',
                                                quoting=csv.QUOTE_NONE)
                print "Now parsing " + f
                #Parse XML for current file
                tree = ET.parse(self.input_dir + f)
                root = tree.getroot()
                self.parent_map = dict()
                self.parent_map = dict((c, p) for p in tree.getiterator() for c in p)
                token_feature_builder.set_parent_map(self.parent_map)
                self.get_text_nodes(root)

                #Close file stream
                output.close()


if __name__ == '__main__':
    runner = Raw2Bio("../../GWAS_data/nxml_bugfinding/",
                     "../../GWAS_data/gazzetteers/efo_disease_traits",
                     "../../GWAS_data/nxml_bugfinding/bio/")
    runner.execute()
    print "Finished processing all files"
