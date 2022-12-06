import {
    create_fake_image_array_list,
    fake_discussion_output
} from './fake_data_service';
import client from './api_service';
import { useEffect, useState } from 'react';


export const DashboardService = {

    useGetAnalysisSet(analysisUrl) {
        const [analysesDetails, setAnalysesDetails] = useState();
        const [isAnalysesLoading, setAnalysesIsLoading] = useState(true);
        const [analysesError, setAnalysesError] = useState(null);

        useEffect(() => {
            client.get(analysisUrl)
                .then(analysisResponse => {
                    setAnalysesIsLoading(false);
                    setAnalysesDetails(analysisResponse.data);
                })
                .catch(error => {
                    setAnalysesError(error);
                    setAnalysesDetails([]);
                    setAnalysesIsLoading(false);
                })
        }, [analysisUrl]);
        return [isAnalysesLoading, analysesError, analysesDetails];

    },
    useGetLeaderBoard(leaderBoardUrl) {
        const [leaderboardDetails, setLeaderboardDetails] = useState();
        const [isLeaderboardLoading, setLeaderboardIsLoading] = useState(true);
        const [leaderboardError, setLeaderboardError] = useState(null);

        useEffect(() => {
            client.get(leaderBoardUrl)
                .then(leaderboardResponse => {
                    setLeaderboardIsLoading(false);
                    console.log(leaderboardResponse);
                    setLeaderboardDetails(leaderboardResponse.data);
                })
                .catch(error => {
                    setLeaderboardError(error);
                    setLeaderboardDetails([]);
                    setLeaderboardIsLoading(false);
                })
        }, [leaderBoardUrl]);
        return [isLeaderboardLoading, leaderboardError, leaderboardDetails];
    },
    useGetSubmissions(submissionUrl) {
        const [submissionDetails, setSubmissionDetails] = useState();
        const [isSubmissionLoading, setSubmissionIsLoading] = useState(true);
        const [submissionError, setSubmissionError] = useState(null);

        useEffect(() => {
            client.get(submissionUrl)
                .then(submissionResponse => {
                    setSubmissionIsLoading(false);
                    console.log(submissionResponse.data);
                    setSubmissionDetails(submissionResponse.data);
                })
                .catch(error => {
                    setSubmissionError(error);
                    setSubmissionDetails([]);
                    setSubmissionIsLoading(false);
                })
        }, [submissionUrl]);
        return [isSubmissionLoading, submissionError, submissionDetails];
    },
    uploadAnalysis(user_id, analysis_name, description, short_description, file, rule_set, dataset_description) {
        let uploadAnalysisUrl = "/analysis/upload";
        let form_data = new FormData();
        form_data.append("evaluation_script", file);
        form_data.append("user_id", user_id);
        form_data.append("analysis_name", analysis_name);
        form_data.append("short_description ", short_description);
        form_data.append("ruleset ", rule_set);
        form_data.append("dataset_description", dataset_description);
        form_data.append("description", description);
        client.post(uploadAnalysisUrl, form_data, {
            Accept: '*/*',
            "content-type": 'multipart/form-data'
        });
    },
    getImageObjects(analysis_id) {
        return create_fake_image_array_list(4);
    },
    getDiscussionComments(analysis_id, user_id) {
        return fake_discussion_output(analysis_id, user_id, 10);
    }
}