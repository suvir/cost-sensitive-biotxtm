__author__ = 'suvir'
import re


class BinaryClassifiers(object):
    @staticmethod
    def in_title_abstract(row):
        """
        Checks if the disease/trait mention appears in the title or abstract
        :param row: A row of a dataframe
        :return: boolean
        """
        # return row['tag'] in ['title', 'abstract']
        tag1 = row['Tag1']
        tag2 = row['Tag2']
        assert isinstance(tag1, str)
        assert isinstance(tag2, str)
        if 'title' in tag1 or 'title' in tag2 or 'abstract' in tag1 or 'abstract' in tag2:
            return 1
        else:
            return 0

    @staticmethod
    def exact_match(row):
        """
        Checks if the disease/trait mention is an exact match of the target.
        :param row: A row of a dataframe.
        :param target: Target disease trait of the paper.
        :return: boolean
        """
        entity = row['Entity'].lower()
        target = [row['DISEASETRAIT'].lower(), row['EFOTRAIT'].lower(), row['PARENT'].lower()]
        # print entity, target
        return int(entity in target)

    @staticmethod
    def __partial_match(word, wlist):
        """
        Check if word is exact match or prefix match of any other word in the word list.
        :param word: A string
        :param wlist: A list of strings
        :return: True if word is exact match or prefix match of any other word in the word list.
        """
        word_parts = re.findall(r"[\w']+", word.lower())
        for w in wlist:
            this_parts = re.findall(r"[\w']+", w.lower())
            for p in word_parts:
                if p in this_parts:
                    return True
        return False

    @staticmethod
    def partial_match(row):
        """
        Checks if the disease/trait mention is a partial match of the target.
        :param row: A row of a dataframe.
        :param target: Target disease trait of the paper.
        :return: boolean
        """
        entity = row['Entity'].lower()
        target = [row['DISEASETRAIT'].lower(), row['EFOTRAIT'].lower(), row['PARENT'].lower()]
        return int(BinaryClassifiers.__partial_match(entity, target))

    @staticmethod
    def is_synonym_exact(row, synonyms):
        """
        Checks if the disease/trait mention is a synonym of the target.
        :param row: A row of a dataframe
        :param synonyms: A list of synonyms
        :return: boolean
        """
        if len(synonyms) == 0:
            return 0
        return int(row['Entity'] in synonyms)

    @staticmethod
    def is_synonym_partial(row, synonyms):
        """
        Checks if the disease/trait mention is a synonym of the target.
        :param row: A row of a dataframe
        :param synonyms: A list of synonyms
        :return: boolean
        """
        if len(synonyms) == 0:
            return 0
        return int(BinaryClassifiers.__partial_match(row['Entity'], synonyms))

    @staticmethod
    def suspect_xml_tags(row):
        garbage_xml_tags = ['aff', 'ack', 'award_group', 'app', 'addr-line', 'author_notes', \
                            'addr_line', 'funding_source', 'inline_formula', 'ref', 'xref', \
                            'ref-list', 'ext-link', 'contrib', 'email', 'job', 'doi', 'base_name']
        if row['Tag1'] in garbage_xml_tags or row['Tag2'] in garbage_xml_tags:
            return 0
        else:
            return 1

    @staticmethod
    def has_multiple_tokens(row):
        dt = row['Entity']
        assert len(dt) > 0, "Empty disease trait mention"
        if dt.isalnum():
            return 1
        else:
            return 0