__author__ = 'suvir'
import pandas as pd
import ast
from BinaryClassifiers import BinaryClassifiers
import numpy as np

class MatrixBuilder(object):
    def __init__(self, entity_df_csv, synonym_df_csv):
        """
        :param entity_df_csv: A dataframe with all the entities from different documents.
        :param synonym_df_csv: A dataframe with diseases and synonyms.
        Some entities might have empty synonym list. That's ok.
        :return: Nothing
        """
        self.entity_df = pd.read_csv(entity_df_csv, sep='\t')
        self.synonym_df = pd.read_csv(synonym_df_csv)
        self.matrix = None
        #print len(self.entity_df), len(self.synonym_df)
        #print self.entity_df.columns
        #print self.synonym_df.columns

    def build_matrix(self):
        committee_matrix = []
        for i in range(len(self.entity_df)):
            committee_row = []
            row = self.entity_df.iloc[i]

            """
            Handle special case of type mismatch
            """
            if not isinstance(row['Entity'], str):
                committee_row = [0, 0, 0, 0, 0, 0, 0]
            else:
                temp_syn_list = self.synonym_df[self.synonym_df['Description'] == row['DISEASETRAIT']]['Synonyms'].tolist()
                synonym_list = ast.literal_eval(temp_syn_list[0])
                # print row['Entity'], row['DISEASETRAIT'], synonym_list

                # Check if entity in title or abstract
                committee_row.append(BinaryClassifiers.in_title_abstract(row))

                # Check if exact match
                committee_row.append(BinaryClassifiers.exact_match(row))

                # Check if partial match
                committee_row.append(BinaryClassifiers.partial_match(row))

                # Check if synonym match
                committee_row.append(BinaryClassifiers.is_synonym_exact(row, synonym_list))

                # Partial match anything in synonym
                committee_row.append(BinaryClassifiers.is_synonym_partial(row, synonym_list))

                # Check if tag is in a probably garbage tag
                committee_row.append(BinaryClassifiers.suspect_xml_tags(row))

                # Check if there are multiple tokens in string
                committee_row.append(BinaryClassifiers.has_multiple_tokens(row))
            committee_matrix.append(committee_row)
            print i
        self.matrix = pd.DataFrame(committee_matrix).as_matrix()
        print type(self.matrix)

    def dump_matrix(self, filename):
        np.savetxt(filename, self.matrix)

if __name__ == "__main__":
    matrix_builder = MatrixBuilder("../df_ready.csv", "../gwas_synonyms_from_umls.csv")
    matrix_builder.build_matrix()
    matrix_builder.dump_matrix("../committee_matrix.txt")