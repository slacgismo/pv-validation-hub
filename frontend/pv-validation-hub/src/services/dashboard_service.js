import { create_fake_analysis_big_image_data, create_fake_analysis_data_array, create_fake_dataset_descrption, create_fake_leaderboard_array, create_fake_overview } from './fake_data_service';

export const DashboardService = {
    
    getAnalysisSet() {
        return create_fake_analysis_data_array(10);
    },
    getLeaderBoard(analysis_id) {
        return create_fake_leaderboard_array(20);
    },
    getCardDetails(analysis_id) {
        return create_fake_analysis_big_image_data();
    },
    getAnalysisDataset(analysis_id) {
        return create_fake_dataset_descrption();
    },
    getAnalysisOverview(analysis_id) {
        return create_fake_overview();
    }
}