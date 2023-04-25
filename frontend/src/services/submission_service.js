import {
    fake_date_between_output,
    fake_number_of_submission,
    fake_submission_details
} from "./fake_data_service"
import client from "./api_service";

export const SubmissionService = {
    getSubmissionDateRangeSet(user_id) {
        return fake_date_between_output(20);
    },
    getSubmissionsSet(user_id) {
        return fake_number_of_submission(20);
    },
    getSubmissionDetails(user_id, submission_id) {
        return fake_submission_details();
    },
    getAllSubmissionsForUser(user_id) {
        return client.get(`/submissions/user/${user_id}/submissions`)
          .then(response => {
            return response.data;
          });
      },
}