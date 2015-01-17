__author__ = 'suvir'


class CommitteeMatrix(object):
    """
    Separate methods for each committee member
    """

    def __init__(self):
        self.committee_members = CommitteeMatrix.__init__member_list()

    @staticmethod
    def __init__member_list():
        committee = ["__is_title_or_abstract",
                     "__is_synonym",
                     "__is_exact_target",
                     "__is_partial_target",
                     "__is_disease",
                     "__is_compound_token",
                     "__location_in_doc"]
        return committee

    def __is_title_or_abstract(self, passage):
        pass

    def __is_synonym(self, passage):
        pass

    def __is_exact_target(self, passage):
        pass

    def __is_partial_target(self, passage):
        pass

    def __is_disease(self, passage):
        pass

    def __is_compound_token(self, passage):
        pass

    def __location_in_doc(self, passage):
        """
        Assume that document is divided into k parts with equal number of words.
        Return the index of the part in which the passage is found.
        :return: a list of k elements.
        """
        pass

    def get_committee_vector(self, passage):
        vector = []
        for cm in self.committee_members:
            method = getattr(CommitteeMatrix, cm)
            result = method()
            assert isinstance(result, list), "Each committee member must return a list"
            vector.extend(result)
        assert len(vector) > 0, "Committee vector cant be empty"
        return vector