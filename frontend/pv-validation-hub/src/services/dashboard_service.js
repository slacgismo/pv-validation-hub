const axios = require('axios');
import { create_fake_analysis_data_array } from './fake_data_service';

const DashboardService = {
    
    getAnalysisSet() {
        return create_fake_analysis_data_array(10);
    }
}