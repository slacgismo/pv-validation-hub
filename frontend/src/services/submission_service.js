import {
    fake_date_between_output,
    fake_number_of_submission,
    fake_submissio_details
} from "./fake_data_service"

export const SubmissionService = {
    getSubmissionDateRangeSet(user_id) {
        return fake_date_between_output(20);
    },
    getSubmissionsSet(user_id) {
        return fake_number_of_submission(20);
    },
    getSubmissionDetails(user_id, submission_id) {
        return fake_submissio_details();
    }
}