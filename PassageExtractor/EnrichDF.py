__author__ = 'suvir'

import re
import pandas as pd
from Raw2Bio import Raw2Bio
from Bio2Df import Bio2Df
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk.corpus import stopwords


class EnrichDF:
    def __init__(self, df=None):
        self.df = df

    def join_with_df(self, join_df, on_colname):
        """
        Given another dataframe, join it with the main dataframe of the class
        :param join_df: Another dataframe
        :param on_colname: Column name to join by
        :return: No return value. Updates the dataframe.
        """
        print "Inside join df"
        print len(self.df), len(join_df)
        self.df = self.df.merge(join_df, on=on_colname)

    def clean_text_column(self, column):
        """
        :param colname: column name to clean values of
        :return: No return value. Updates the dataframe.
        """
        stopwords_list = stopwords.words('english')
        tokenizer = PunktWordTokenizer()

        def cleaner(s):
            """
            Utility function to tokenize, remove stopwords and special characters
            :param s: A string of characters
            :return: Cleaned string
            """
            s = ' '.join([p for p in tokenizer.tokenize(s) if p.lower() not in stopwords_list and p.isalnum()])
            return s

        return column.apply(cleaner)

    def filter_column_by_value(self, colname, filter_list):
        """
        Function to filter out a column of dataframe by list of values.
        :param colname: column name to filter values of
        :param filter_list: list of values to filter out from column
        :return: No return value. Updates the dataframe.
        """
        self.df = self.df[-self.df[colname].isin(filter_list)]

    def get_df(self):
        """
        Returns the dataframe.
        :return: The dataframe
        """
        return self.df

    # def generate_label_heuristic(self):
    # """
    # Generate a label for each row in df based on string match heuristic between entity
    #     and manual annotation done by human annotators.
    #     :return: No explicit return. Updates the dataframe with a column called "Match" that
    #     has a series of Y or N labels.
    #     """
    #
    #     def partial_match(word, wlist):
    #         """
    #         Check if word is exact match or prefix match of any other word in the word list.
    #         :param word: A string
    #         :param wlist: A list of strings
    #         :return: True if word is exact match or prefix match of any other word in the word list.
    #         """
    #         word_parts = re.findall(r"[\w']+", word.lower())
    #         for w in wlist:
    #             this_parts = re.findall(r"[\w']+", w.lower())
    #             for p in word_parts:
    #                 if p in this_parts:
    #                     return True
    #
    #     some_match = []
    #     for index, row in self.df.iterrows():
    #         if row['Entity'] in [row['DISEASETRAIT'], row['EFOTRAIT'], row['PARENT']]:
    #             some_match.append('Y')
    #         elif row['Entity'].startswith((row['DISEASETRAIT'], row['EFOTRAIT'], row['PARENT'])):
    #             some_match.append('Y')
    #         elif partial_match(row['Entity'], [row['DISEASETRAIT'], row['EFOTRAIT'], row['PARENT']]):
    #             some_match.append('Y')
    #         else:
    #             some_match.append('N')
    #     self.df['Label'] = some_match

    # def generate_df_from_raw(self):
    #     # Convert raw files to BIO
    #     raw_to_bio = Raw2Bio("../../GWAS_data/nxml_bugfinding/", "../../GWAS_data/gazzetteers/efo_disease_traits",
    #                          "../../GWAS_data/nxml_bugfinding/bio/")
    #     raw_to_bio.execute()
    #
    #     #Convert BIO tagged files to a dataframe
    #     bio_to_df = Bio2Df("/Users/suvir/Documents/GWAS/Fall Research/Gold Standard/EFO DiseaseTrait GoldStandard/")
    #     bio_to_df.execute()
    #     self.df = bio_to_df.get_df()
    #     self.df.to_csv('temp_store.csv', sep='\t', index=False, index_label=False)

    def clean_entity_and_windows(self):
        self.df.Entity = self.clean_text_column(self.df.Entity)
        self.df.LeftWindow = self.clean_text_column(self.df.LeftWindow)
        self.df.RightWindow = self.clean_text_column(self.df.RightWindow)
        print "Finished cleaning text strings"

    # def filter_xml_tags(self):
    #     garbage_xml_tags = ['aff', 'ack', 'award_group', 'app', 'addr-line', 'author_notes', \
    #                         'addr_line', 'funding_source', 'inline_formula', 'ref', 'xref', \
    #                         'ref-list', 'ext-link', 'contrib', 'email', 'job', 'doi', 'base_name']
    #     for col in ['Tag1', 'Tag2']:
    #         self.filter_column_by_value(col, garbage_xml_tags)
    #     print "Length after filtering out the columns", len(self.df)


    def drop_nulls(self, colname):
        self.df = self.df[pd.notnull(self.df[colname])]

    def delete_nulls(self):
        # Drop rows with null entities or context
        for col in ['Entity', 'LeftWindow', 'RightWindow']:
            self.drop_nulls(col)

    def execute_all(self, df_csv):
        # Normally, start execution from here. Assume that the df exists in supplied filename
        self.df = pd.read_csv(df_csv, sep='\t')
        print "Initial size", len(self.df)

        #Join dataframe with EFO excel sheet
        efo = pd.read_excel("/Users/suvir/Documents/GWAS/Fall Research/Gold Standard/GWAS-EFO-Mappings201305.xlsx",
                            'Sheet1')
        self.join_with_df(efo, "PUBMEDID")
        print "Length after joining dataframe", len(self.df)

        #Keeping only relevant columns
        self.df = self.df[
            ['Entity', 'LeftWindow', 'RightWindow', 'Tag1', 'Tag2', 'PUBMEDID', 'DISEASETRAIT', 'EFOTRAIT', 'PARENT']]

        #Clean out text columns
        self.clean_entity_and_windows()

        #Delete null values
        self.delete_nulls()


if __name__ == "__main__":
    pipeline = EnrichDF()
    pipeline.execute_all('../temp_store.csv')
    df = pipeline.get_df()
    df.to_csv('../df_ready.csv', sep='\t', index=False, index_label=False)