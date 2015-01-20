__author__ = 'suvir'


class BinaryClassifiers(object):
    @staticmethod
    def __in_title_abstract(row):
        """
        Checks if the disease/trait mention appears in the title or abstract
        :param row: A row of a dataframe
        :return: boolean
        """
        return row['tag'] in ['title', 'abstract']

    @staticmethod
    def __exact_match(row, target):
        """
        Checks if the disease/trait mention is an exact match of the target.
        :param row: A row of a dataframe.
        :param target: Target disease trait of the paper.
        :return: boolean
        """
        return row['diseasetrait'] == target

    @staticmethod
    def __partial_match(row, target):
        """
        Checks if the disease/trait mention is a partial match of the target.
        :param row: A row of a dataframe.
        :param target: Target disease trait of the paper.
        :return: boolean
        """
        return target.startswith(row['diseasetrait'])

    @staticmethod
    def __is_synonym(row, synonyms):
        """
        Checks if the disease/trait mention is a synonym of the target.
        :param row: A row of a dataframe
        :param synonyms: A list of synonyms
        :return: boolean
        """
        return row['diseasetrait'] in synonyms


    @staticmethod
    def __has_multiple_tokens(row):
        dt = row['diseasetrait']
        assert len(dt) > 0, "Empty disease trait mention"
        return not dt.isalpha()