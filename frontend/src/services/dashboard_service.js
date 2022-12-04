import {
    create_fake_image_array_list,
    create_fake_leaderboard_array,
    fake_discussion_output
} from './fake_data_service';
import client from './api_service';
import { useEffect, useState } from 'react';
const protocol = "http";
const host = "localhost:8000";

function get_base_url() {
    return protocol + "://" + host;
}


export const DashboardService = {

    useGetAnalysisSet(url) {
        const [analysesDetails, setAnalysesDetails] = useState();
        const [isAnalysesLoading, setAnalysesIsLoading] = useState(true);
        const [analysesError, setAnalysesError] = useState(null);

        useEffect(() => {
            client.get(url)
                .then(response => {
                    setAnalysesIsLoading(false);
                    setAnalysesDetails(response.data);
                })
                .catch(error => {
                    setAnalysesError(error);
                    setAnalysesIsLoading(false);
                })
        }, [url]);
        return [isAnalysesLoading, analysesError, analysesDetails];

    },
    getLeaderBoard(analysis_id) {
        // let url = get_base_url() + "/analysis/" + analysis_id + "/leaderboard";
        // return url;
        return create_fake_leaderboard_array(50);
    },
    useGetSubmissions(url) {
        const [submissionDetails, setSubmissionDetails] = useState();
        const [isSubmissionLoading, setSubmissionIsLoading] = useState(true);
        const [SubmissionError, setSubmissionError] = useState(null);

        useEffect(() => {
            client.get(url)
                .then(response => {
                    setSubmissionIsLoading(false);
                    setSubmissionDetails(response.data);
                })
                .catch(error => {
                    setSubmissionError(error);
                    setSubmissionIsLoading(false);
                })
        }, [url]);
        return [isSubmissionLoading, SubmissionError, submissionDetails];
    },
    uploadAnalysis(user_id, analysis_name, description, short_description, file, rule_set, dataset_description) {
        let url = "/analysis/upload";
        let form_data = new FormData();
        form_data.append("evaluation_script", file);
        form_data.append("user_id", user_id);
        form_data.append("analysis_name", analysis_name);
        form_data.append("short_description ", short_description);
        form_data.append("ruleset ", rule_set);
        form_data.append("dataset_description", dataset_description);
        form_data.append("description", description);
        client.post(url, form_data, {
            Accept: '*/*',
            "content-type": 'multipart/form-data'
        });
    },
    // getAnalysisDataset(analysis_id) {
    //     let url = get_base_url() + "/analysis/" + analysis_id;
    //     return url;
    // },
    // getAnalysisOverview(analysis_id) {
    //     return create_fake_overview();
    // },
    // getRuleSet(analysis_id) {
    //     return create_fake_ruleset();
    // },
    getImageObjects(analysis_id) {
        return create_fake_image_array_list(4);
    },
    getDiscussionComments(analysis_id, user_id) {
        return fake_discussion_output(analysis_id, user_id, 10);
    }
}