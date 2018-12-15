import datetime
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from . import models
from .factories import RoundPageFactory, InternSelectionFactory


# don't try to use the static files manifest during tests
@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class InternSelectionTestCase(TestCase):
    def test_mentor_can_resign(self):
        for mentors_count in (1, 2):
            with self.subTest(mentors_count=mentors_count):
                internselection = InternSelectionFactory(
                    active=True,
                    mentors=mentors_count,
                )
                mentors = list(internselection.mentors.all())
                mentor = mentors.pop()

                path = reverse('resign-as-mentor', kwargs={
                    'round_slug': internselection.round().slug,
                    'community_slug': internselection.project.project_round.community.slug,
                    'project_slug': internselection.project.slug,
                    'applicant_username': internselection.applicant.applicant.account.username,
                })

                self.client.force_login(mentor.mentor.account)
                response = self.client.post(path)
                self.assertEqual(response.status_code, 302)

                self.assertQuerysetEqual(internselection.mentors.all(), mentors, transform=lambda x: x)

    @staticmethod
    def _mentor_feedback_form(internselection, **kwargs):
        defaults = {
            'in_contact': True,
            'asking_questions': True,
            'active_in_public': True,
            'provided_onboarding': True,
            'checkin_frequency': models.InitialMentorFeedback.ONCE_WEEKLY,
            'last_contact': internselection.initial_feedback_opens,
            'intern_response_time': models.InitialMentorFeedback.HOURS_12,
            'mentor_response_time': models.InitialMentorFeedback.HOURS_12,
            'payment_approved': True,
            'full_time_effort': True,
            'progress_report': 'Everything is fine.',
            'request_extension': None,
            'extension_date': None,
        }
        defaults.update(kwargs)
        return defaults

    def _submit_mentor_feedback_form(self, internselection, answers):
        mentor = internselection.mentors.get()
        self.client.force_login(mentor.mentor.account)

        path = reverse('initial-mentor-feedback', kwargs={
            'username': internselection.applicant.applicant.account.username,
        })

        return self.client.post(path, {
            # This is a dictionary comprehension that converts model-level
            # values to form/POST values. It assumes all form widgets accept
            # the str() representation of their type when the form is POSTed.
            # Values which are supposed to be unspecified can be provided as
            # None, in which case we don't POST that key at all.
            key: str(value)
            for key, value in answers.items()
            if value is not None
        })

    def test_mentor_can_give_initial_feedback(self):
        for request_extension in (False, True):
            with self.subTest(request_extension=request_extension):
                internselection = InternSelectionFactory(
                    active=True,
                    round__start_from='initialfeedback',
                )

                extension_date = None
                if request_extension:
                    extension_date = internselection.round().initialfeedback + datetime.timedelta(weeks=5)

                answers = self._mentor_feedback_form(internselection,
                    request_extension=request_extension,
                    extension_date=extension_date,
                )
                response = self._submit_mentor_feedback_form(internselection, answers)
                self.assertEqual(response.status_code, 302)

                # will raise DoesNotExist if the view didn't create this
                feedback = internselection.initialmentorfeedback

                for key, expected in answers.items():
                    self.assertEqual(getattr(feedback, key), expected)

                # only allow submitting once
                self.assertFalse(feedback.allow_edits)

    def test_invalid_mentor_extension_request(self):
        round = RoundPageFactory(start_from='initialfeedback')

        range_error = "Extension date must be between {} and {}".format(
            round.initialfeedback,
            round.initialfeedback + datetime.timedelta(weeks=5),
        )
        extension_deltas = (
            (None, "If you're requesting an extension, this field is required."),
            (datetime.timedelta(days=-1), range_error),
            (datetime.timedelta(weeks=5, days=1), range_error),
        )
        for extension_delta, expected_error in extension_deltas:
            with self.subTest(extension_delta=extension_delta):
                internselection = InternSelectionFactory(
                    active=True,
                    round=round,
                )

                extension_date = None
                if extension_delta:
                    extension_date = round.initialfeedback + extension_delta

                answers = self._mentor_feedback_form(internselection,
                    request_extension=True,
                    extension_date=extension_date,
                )
                response = self._submit_mentor_feedback_form(internselection, answers)
                self.assertEqual(response.status_code, 200)

                # view should not have created a feedback object
                with self.assertRaises(models.InitialMentorFeedback.DoesNotExist):
                    internselection.initialmentorfeedback

                self.assertFormError(response, "form", "extension_date", expected_error)