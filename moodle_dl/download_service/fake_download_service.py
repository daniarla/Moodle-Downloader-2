import logging
import os
import platform

from pathlib import Path
from typing import List

from moodle_dl.download_service.download_service import DownloadService
from moodle_dl.moodle_connector.moodle_service import MoodleService
from moodle_dl.types import Course
from moodle_dl.utils import PathTools as PT


class FakeDownloadService:
    """
    FakeDownloadService fakes a DownloadService.
    This way a local database of Moodle's current files
    can be created without actually downloading the files.
    """

    def __init__(self, courses: List[Course], moodle_service: MoodleService, opts):
        """
        Initiates the FakeDownloadService with all files that
        need to be downloaded (saved in the database).
        @param courses: A list of courses that contains all modified files.
        @param moodle_service: A reference to the moodle_service, currently
                               only to get to the state_recorder.
        @param opts: Moodle-dl options
        """

        self.courses = courses
        self.state_recorder = moodle_service.recorder
        self.opts = opts

        # delete files, that should be deleted
        self.state_recorder.batch_delete_files(self.courses)

        # Prepopulate queue with any files that were given
        for course in self.courses:
            for file in course.files:
                if file.deleted is False:
                    save_destination = DownloadService.gen_path(opts.path, course, file)

                    filename = PT.to_valid_name(file.content_filename)

                    file.saved_to = str(Path(save_destination) / filename)

                    if file.content_type == 'description':
                        file.saved_to = str(Path(save_destination) / (filename + '.md'))

                    elif file.content_type == 'html':
                        file.saved_to = str(Path(save_destination) / (filename + '.html'))

                    elif file.module_modname.startswith('url'):
                        file.saved_to = str(Path(save_destination) / (filename + '.desktop'))
                        if os.name == 'nt' or platform.system() == "Darwin":
                            file.saved_to = str(Path(save_destination) / (filename + '.URL'))

                    self.state_recorder.save_file(file, course.id, course.fullname)

    def get_failed_url_targets(self):
        """
        Return a list of failed Downloads, as a list of URLTargets.
        No download can fail, so this is only a dummy function.
        """
        return []

    def run(self):
        """Dummy function"""
        logging.success('All files stored in the Database!')
