import {
  fakeDateBetweenOutput,
  fakeNumberOfSubmission,
  fakeSubmissionDetails,
} from './fake_data_service.js';
import client from './api_service.js';

const SubmissionService = {
  // eslint-disable-next-line no-unused-vars
  getSubmissionDateRangeSet(userId) {
    return fakeDateBetweenOutput(20);
  },
  // eslint-disable-next-line no-unused-vars
  getSubmissionsSet(userId) {
    return fakeNumberOfSubmission(20);
  },
  // eslint-disable-next-line no-unused-vars
  getSubmissionDetails(userId, submissionId) {
    return fakeSubmissionDetails();
  },
  getAllSubmissionsForUser(userId) {
    return client.get(`/submissions/user/${userId}/submissions`)
      .then((response) => response.data);
  },
  getSubmissionResults(submissionId) {
    return client.get(`/submissions/submission_results/${submissionId}`)
      .then((response) => response.data);
  },
  getSubmissionErrors(submissionId) {
    return client.get(`/error/error_report/private/${submissionId}`)
      .then((response) => response.data);
  },
};

export default SubmissionService;
