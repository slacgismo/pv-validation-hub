import {
    create_fake_analysis_big_image_data,
    create_fake_analysis_data_array,
    create_fake_dataset_descrption,
    create_fake_image_array_list,
    create_fake_leaderboard_array,
    create_fake_overview,
    create_fake_ruleset,
    create_fake_submission_array,
    create_fake_user_data,
    fake_discussion_output
} from './fake_data_service';

export const DashboardService = {

    getAnalysisSet() {
        return create_fake_analysis_data_array(10);
    },
    getLeaderBoard(analysis_id) {
        return create_fake_leaderboard_array(50);
    },
    getSubmission(analysis_id) {
        return create_fake_submission_array(20);
    },
    getCardDetails(analysis_id) {
        return create_fake_analysis_big_image_data();
    },
    getAnalysisDataset(analysis_id) {
        return create_fake_dataset_descrption();
    },
    getAnalysisOverview(analysis_id) {
        return create_fake_overview();
    },
    getRuleSet(analysis_id) {
        return create_fake_ruleset();
    },
    getImageObjects(analysis_id) {
        return create_fake_image_array_list(4);
    },
    getDiscussionComments(analysis_id, user_id) {
        return fake_discussion_output(analysis_id, user_id, 10);
    },
    getUserProfile(user_id) {
        return create_fake_user_data();
    }
}