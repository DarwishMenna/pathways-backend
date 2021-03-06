import spacy
import sklearn.preprocessing
from textacy.vsm import Vectorizer
from django.utils.text import slugify


def to_task_ids_and_descriptions(tasks):
    ids = []
    descriptions = []
    for _, task in tasks['taskMap'].items():
        ids.append(slugify(task['id']))
        english_description = task['title']['en'] + ' ' + task['description']['en']
        descriptions.append(english_description)
    return (ids, descriptions)


def to_service_ids_and_descriptions(services):
    ids = []
    descriptions = []
    for service in services:
        ids.append(service.id)
        descriptions.append(service.name + ' ' + service.description)
    return (ids, descriptions)


def compute_similarities(docs):
    nlp = spacy.load('en')
    spacy_docs = [nlp(doc) for doc in docs]
    tokenized_docs = ([tok.lemma_ for tok in doc] for doc in spacy_docs)
    # tf-idf
    vectorizer = Vectorizer(tf_type='linear', apply_idf=True, idf_type='smooth', apply_dl=False)
    term_matrix = vectorizer.fit_transform(tokenized_docs)
    return compute_cosine_doc_similarities(term_matrix)


def compute_cosine_doc_similarities(matrix):
    normalized_matrix = sklearn.preprocessing.normalize(matrix, axis=1)
    return normalized_matrix * normalized_matrix.T
