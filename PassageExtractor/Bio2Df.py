__author__ = 'suvir'

import os
import re
import pandas as pd


class Bio2Df:
    """
    Class to convert files in BIO format to a dataframe
    """

    def __init__(self, dirname="."):
        """
        Constructor
        :param dirname: directory with BIO format files
        :return:
        """
        self.input_dir = dirname
        self.window_size = 10
        self.df = pd.DataFrame()

    def parsePubmedId(self, filename):
        try:
            pubmed_id = re.findall("\d{8}", filename)[0]
            return pubmed_id
        except:
            print "Error in parsing pubmed id", filename
            return "123"
            pass

    def get_words_in_window(self, lines, start_idx, end_idx):
        s = []
        for idx in range(start_idx, end_idx):
            try:
                token = lines[idx].split()[0]
                s.append(token)
            except IndexError:
                pass
        return " ".join(s)

    def get_lr_window(self, lines, lindex, rindex):
        left_window = self.get_words_in_window(lines, lindex - self.window_size, lindex)
        right_window = self.get_words_in_window(lines, rindex + 1, rindex + self.window_size)
        return left_window, right_window

    def parseLines(self, lines, filename):
        # Parse BIO entities and return as a dataframe
        multi_flag = False
        multi_word_entity = []
        list_of_list = []
        last_tag_pair = ()
        start_index = -1
        end_index = -1

        for idx in range(len(lines)):
            l = lines[idx]
            try:
                token, tag1, tag2, label = l.split('\t')
            except:
                print "Error in parsing line", repr(l)
                continue
            #print token,tag1,tag2,label
            if label.startswith('O') and multi_flag == True:
                #First append the multi word entity
                left_window, right_window = self.get_lr_window(lines, start_index, end_index)
                list_of_list.append(
                    [' '.join(multi_word_entity), 'Y', last_tag_pair[0], last_tag_pair[1], filename, left_window,
                     right_window])
                #Then append the current entity
                list_of_list.append([token, 'N', tag1, tag2, filename, "NONE", "NONE"])
                #Clear out all state variables
                multi_flag = False
                start_index = -1
                end_index = -1
                last_tag_pair = ()
                multi_word_entity = []

            elif label.startswith('I') and multi_flag == False:
                raise ValueError("Error! I found without B")

            elif label.startswith('I') and multi_flag == True:
                multi_word_entity.append(token)
                last_tag_pair = (tag1, tag2)
                multi_flag = True
                if end_index == -1:
                    raise ValueError("Error! I found without B")
                else:
                    end_index = idx

            elif label.startswith('B'):
                multi_word_entity.append(token)
                last_tag_pair = (tag1, tag2)
                multi_flag = True
                start_index = idx
                end_index = idx

            else:
                #save multi_word_entity to df
                list_of_list.append([token, 'N', tag1, tag2, filename, "NONE", "NONE"])
                #Clear out all state variables
                multi_flag = False
                start_index = -1
                end_index = -1
                last_tag_pair = ()
                multi_word_entity = []

        #print len(list_of_list)
        return pd.DataFrame(list_of_list, columns=['Entity', 'IsDiseaseTrait', 'Tag1', 'Tag2', 'PUBMEDID', 'LeftWindow',
                                                   'RightWindow'])

    def execute(self):
        files = [f for f in os.listdir(self.input_dir) if not f.startswith(".")]
        df_list = []
        for f in files:
            lines = open(self.input_dir + f).readlines()
            # Parse pubmed id of the file
            filename = self.parsePubmedId(f)
            #Get all entities in the file in a single df
            file_df = self.parseLines(lines, filename)
            #All the dataframes in a single df
            df_list.append(file_df)
        # Combine all the files into a pandas dataframe
        self.df = pd.concat(df_list, axis=0)
        self.df = self.df[self.df.IsDiseaseTrait == 'Y']

    def get_df(self):
        print "Return dataframe made from BIO files"
        print len(self.df)
        return self.df


if __name__ == '__main__':
    # runner = Bio2Df("../../GWAS_data/nxml_bugfinding/bio/")
    # runner.execute()
    # df = runner.get_df()
    # print df.columns
    # print df
    # print "Finished processing all files"
    bio_to_df = Bio2Df("/Users/suvir/Documents/GWAS/Fall Research/Gold Standard/EFO DiseaseTrait GoldStandard/")
    bio_to_df.execute()
    df = bio_to_df.get_df()
    df.to_csv('../temp_store.csv', sep='\t', index=False, index_label=False)

