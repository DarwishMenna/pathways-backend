from django.test import TestCase
from human_services.organizations.tests.helpers import OrganizationBuilder
from human_services.services.tests.helpers import ServiceBuilder
from search.save_similarities import save_task_similarities, save_task_service_similarity_scores
from search.models import Task, TaskSimilarityScore, TaskServiceSimilarityScore
from common.testhelpers.random_test_values import a_string, a_float
from newcomers_guide.tests.helpers import create_tasks
import scipy


class TestSavingTaskSimilarities(TestCase):

    def test_deletes_existing_records(self):
        first_task_id = a_string()
        second_task_id = a_string()
        create_tasks([first_task_id, second_task_id])
        record = TaskSimilarityScore(first_task_id=first_task_id,
                                     second_task_id=second_task_id,
                                     similarity_score=a_float())
        record.save()

        save_task_similarities([], [], 0)

        self.assertEqual(TaskSimilarityScore.objects.count(), 0)

    def test_saves_required_number_of_records_for_each_row(self):
        ids = [a_string() for i in range(5)]
        create_tasks(ids)
        scores = scipy.sparse.csr_matrix([[a_float() for i in range(5)] for j in range(5)])

        scores_to_save_per_row = 2
        save_task_similarities(ids, scores, scores_to_save_per_row)

        scores_saved_in_all = 5 * 2
        self.assertEqual(TaskSimilarityScore.objects.count(), scores_saved_in_all)

    def test_saves_all_off_diagonal_scores_if_number_of_scores_to_save_is_large(self):
        ids = [a_string() for i in range(5)]
        create_tasks(ids)
        scores = scipy.sparse.csr_matrix([[a_float() for i in range(5)] for j in range(5)])

        too_many_records_to_save = 2000
        save_task_similarities(ids, scores, too_many_records_to_save)

        number_of_off_diagonal_elements = 5 * 4
        self.assertEqual(TaskSimilarityScore.objects.count(), number_of_off_diagonal_elements)

    def test_saves_two_non_diagonal_elements_with_the_highest_scores_in_each_row(self):
        ids = [a_string() for i in range(4)]
        create_tasks(ids)
        scores = scipy.sparse.csr_matrix([[1, 2, 3, 4],
                                          [5, 6, 7, 8],
                                          [9, 10, 11, 12],
                                          [13, 14, 15, 16]])

        records_to_save_per_row = 2
        save_task_similarities(ids, scores, records_to_save_per_row)

        records = TaskSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 8)
        self.assertEqual(records[0].similarity_score, 3.0)
        self.assertEqual(records[1].similarity_score, 4.0)
        self.assertEqual(records[2].similarity_score, 7.0)
        self.assertEqual(records[3].similarity_score, 8.0)
        self.assertEqual(records[4].similarity_score, 10.0)
        self.assertEqual(records[5].similarity_score, 12.0)
        self.assertEqual(records[6].similarity_score, 14.0)
        self.assertEqual(records[7].similarity_score, 15.0)

    def test_saves_elements_with_first_task_id(self):
        ids = [a_string() for i in range(4)]
        create_tasks(ids)
        scores = scipy.sparse.csr_matrix([[1, 2, 3, 4],
                                          [5, 6, 7, 8],
                                          [9, 10, 11, 12],
                                          [13, 14, 15, 16]])

        records_to_save_per_row = 2
        save_task_similarities(ids, scores, records_to_save_per_row)

        records = TaskSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 8)
        self.assertEqual(records[0].first_task_id, ids[0])
        self.assertEqual(records[1].first_task_id, ids[0])
        self.assertEqual(records[2].first_task_id, ids[1])
        self.assertEqual(records[3].first_task_id, ids[1])
        self.assertEqual(records[4].first_task_id, ids[2])
        self.assertEqual(records[5].first_task_id, ids[2])
        self.assertEqual(records[6].first_task_id, ids[3])
        self.assertEqual(records[7].first_task_id, ids[3])

    def test_saves_elements_with_second_task_id(self):
        ids = [a_string() for i in range(4)]
        create_tasks(ids)
        scores = scipy.sparse.csr_matrix([[1, 2, 3, 4],
                                          [5, 6, 7, 8],
                                          [9, 10, 11, 12],
                                          [13, 14, 15, 16]])

        records_to_save_per_row = 2
        save_task_similarities(ids, scores, records_to_save_per_row)

        records = TaskSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 8)
        self.assertEqual(records[0].second_task_id, ids[2])
        self.assertEqual(records[1].second_task_id, ids[3])
        self.assertEqual(records[2].second_task_id, ids[2])
        self.assertEqual(records[3].second_task_id, ids[3])
        self.assertEqual(records[4].second_task_id, ids[1])
        self.assertEqual(records[5].second_task_id, ids[3])
        self.assertEqual(records[6].second_task_id, ids[1])
        self.assertEqual(records[7].second_task_id, ids[2])


class TestSavingTaskServiceSimilarities(TestCase):
    def setUp(self):
        self.organization = OrganizationBuilder().create()
        self.three_task_ids = [a_string() for i in range(3)]
        create_tasks(self.three_task_ids)

        services = [ServiceBuilder(self.organization).create() for i in range(3)]
        self.three_service_ids = [service.id for service in services]

    def test_deletes_existing_records(self):
        task_id = a_string()
        Task(id=task_id, name=a_string(), description=a_string()).save()
        service = ServiceBuilder(self.organization).create()
        record = TaskServiceSimilarityScore(task_id=task_id,
                                            service=service,
                                            similarity_score=a_float())
        record.save()

        save_task_service_similarity_scores([], [], [], 0)

        self.assertEqual(TaskServiceSimilarityScore.objects.count(), 0)

    def test_saves_required_number_of_records_for_each_row(self):
        scores = scipy.sparse.csr_matrix([[a_float() for i in range(6)] for j in range(6)])

        scores_to_save_per_row = 2
        save_task_service_similarity_scores(self.three_task_ids, self.three_service_ids, scores, scores_to_save_per_row)

        scores_saved_in_all = 3 * 2
        self.assertEqual(TaskServiceSimilarityScore.objects.count(), scores_saved_in_all)

    def test_saves_all_scores_if_number_of_scores_to_save_is_large(self):
        scores = scipy.sparse.csr_matrix([[a_float() for i in range(6)] for j in range(6)])

        too_many_records_to_save = 2000
        save_task_service_similarity_scores(
            self.three_task_ids, self.three_service_ids, scores, too_many_records_to_save)

        scores_saved_in_all = 3 * 3
        self.assertEqual(TaskServiceSimilarityScore.objects.count(), scores_saved_in_all)

    def test_saves_elements_with_the_highest_scores_in_each_row(self):
        scores = scipy.sparse.csr_matrix([[0, 0, 0, 1, 2, 3],
                                          [0, 0, 0, 4, 5, 6],
                                          [0, 0, 0, 7, 8, 9],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0]])
        records_to_save_per_row = 2
        save_task_service_similarity_scores(
            self.three_task_ids, self.three_service_ids, scores, records_to_save_per_row)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 6)
        self.assertEqual(records[0].similarity_score, 2.0)
        self.assertEqual(records[1].similarity_score, 3.0)
        self.assertEqual(records[2].similarity_score, 5.0)
        self.assertEqual(records[3].similarity_score, 6.0)
        self.assertEqual(records[4].similarity_score, 8.0)
        self.assertEqual(records[5].similarity_score, 9.0)

    def test_saves_elements_with_task_ids(self):
        scores = scipy.sparse.csr_matrix([[0, 0, 0, 1, 2, 3],
                                          [0, 0, 0, 4, 5, 6],
                                          [0, 0, 0, 7, 8, 9],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0]])
        records_to_save_per_row = 2
        save_task_service_similarity_scores(
            self.three_task_ids, self.three_service_ids, scores, records_to_save_per_row)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 6)
        self.assertEqual(records[0].task_id, self.three_task_ids[0])
        self.assertEqual(records[1].task_id, self.three_task_ids[0])
        self.assertEqual(records[2].task_id, self.three_task_ids[1])
        self.assertEqual(records[3].task_id, self.three_task_ids[1])
        self.assertEqual(records[4].task_id, self.three_task_ids[2])
        self.assertEqual(records[5].task_id, self.three_task_ids[2])

    def test_saves_elements_with_service_ids(self):
        scores = scipy.sparse.csr_matrix([[0, 0, 0, 1, 2, 3],
                                          [0, 0, 0, 4, 5, 6],
                                          [0, 0, 0, 7, 8, 9],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0],
                                          [0, 0, 0, 0, 0, 0]])
        records_to_save_per_row = 2
        save_task_service_similarity_scores(
            self.three_task_ids, self.three_service_ids, scores, records_to_save_per_row)

        records = TaskServiceSimilarityScore.objects.order_by('similarity_score')
        self.assertEqual(len(records), 6)
        self.assertEqual(records[0].service_id, self.three_service_ids[1])
        self.assertEqual(records[1].service_id, self.three_service_ids[2])
        self.assertEqual(records[2].service_id, self.three_service_ids[1])
        self.assertEqual(records[3].service_id, self.three_service_ids[2])
        self.assertEqual(records[4].service_id, self.three_service_ids[1])
        self.assertEqual(records[5].service_id, self.three_service_ids[2])
