from taxonomies import models

class TaxonomyBuilder:
    def __init__(self):
        self.vocabulary = 'default_vocabulary'
        self.name = 'default name'

    def with_vocabulary(self, vocabulary):
        self.vocabulary = vocabulary
        return self

    def with_name(self, name):
        self.name = name
        return self

    def build(self):
        result = models.Taxonomy()
        result.vocabulary = self.vocabulary
        result.name = self.name
        return result
