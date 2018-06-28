from django.core.management.base import BaseCommand
from newcomers_guide.generate_fixtures import (generate_task_fixture, generate_taxonomy_fixture,
                                               set_taxonomies_on_tasks)
from newcomers_guide.read_data import read_task_data, read_taxonomy_data
from newcomers_guide.parse_data import parse_task_files, parse_taxonomy_files
from newcomers_guide.log_data import log_taxonomies, log_locales


# invoke as follows:
# python manage.py import_newcomers_guide path/to/newcomers/root/directory


class Command(BaseCommand):
    help = 'Import Newcomers Guide from folder structure'

    def add_arguments(self, parser):
        parser.add_argument('path',
                            metavar='path',
                            help='path to root of Newcomers Guide folder structure')

    def handle(self, *args, **options):
        root_folder = options['path']

        self.stdout.write('Reading Newcomers Guide data from {}'.format(root_folder))

        task_data = read_task_data(root_folder)
        tasks = parse_task_files(task_data)

        taxonomy_data = read_taxonomy_data(root_folder)
        taxonomies = parse_taxonomy_files(taxonomy_data)

        set_taxonomies_on_tasks(taxonomies, tasks['taskMap'])

        log_taxonomies(self.stdout, tasks['taskMap'])
        log_locales(self.stdout, tasks['taskMap'])

        with open('tasks.ts', 'w') as file:
            file.write(generate_task_fixture(tasks))

        with open('taxonomies.ts', 'w') as file:
            file.write(generate_taxonomy_fixture(taxonomies))
