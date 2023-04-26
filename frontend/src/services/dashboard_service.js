import {
    create_fake_image_array_list,
    fake_discussion_output,
    create_fake_leaderboard_array
} from './fake_data_service';
import client from './api_service';
import { useEffect, useState } from 'react';
import { faker } from '@faker-js/faker';


export const DashboardService = {
    formatResponse(response) {
        let finalResponse = []
        let id = 0;
        response.forEach(resp => {
            console.log("Printing response");
            console.log(response);
            if (response[0].data_requirements !== null && response[0].data_requirements !== undefined) {

                for (let i=0; i < response.length; i++) {
                    let element = {
                        id: id,
                        algorithm: resp["algorithm"],
                        created_by: resp["created_by"].username,
                        execution_time: resp["mrt"],
                        status: resp["status"],
                        metrics: resp["data_requirements"],
                        error: resp["mae"],
                        data_requirement: null
                    }
                    id += 1;
                    finalResponse.push(element);
                }
            }
            else{
                let element = {
                    id: id,
                    developer_group: resp["developer_group"],
                    algorithm: resp["algorithm"],
                    created_by: resp["created_by"],
                    execution_time: faker.helpers.arrayElement([66.19317770004272,100.97519278526306]),
                    status: null,
                    metrics: null,
                    error: faker.helpers.arrayElement([23.137764944250826,4.846236274675835]),
                    data_requirement: "MAE"
                }
                id += 1;
                finalResponse.push(element);
            }
        });
        console.log(finalResponse);
        return finalResponse;
    },
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
        console.log(leaderBoardUrl);
        const [leaderboardDetails, setLeaderboardDetails] = useState();
        const [isLeaderboardLoading, setLeaderboardIsLoading] = useState(true);
        const [leaderboardError, setLeaderboardError] = useState(null);

        useEffect(() => {
            client.get(leaderBoardUrl)
                .then(leaderboardResponse => {
                    setLeaderboardIsLoading(false);
                    setLeaderboardDetails(this.formatResponse(leaderboardResponse.data));
                })
                .catch(error => {
                    setLeaderboardError(error);
                    setLeaderboardDetails([]);
                    setLeaderboardIsLoading(false);
                })
        }, [leaderBoardUrl]);
        return [isLeaderboardLoading, leaderboardError, leaderboardDetails];
    },
    useGetSubmissions(submissionUrl, token) {
        const [isSubmissionLoading, setSubmissionLoading] = useState(true);
        const [submissionError, setSubmissionError] = useState(null);
        const [submissionData, setSubmissionData] = useState(null);

        // set authorization token
        client.defaults.headers.common['Authorization'] = "Token " + token;

        useEffect(() => {
            client.get(submissionUrl)
                .then(submissionResponse => {
                    setSubmissionLoading(false);
                    const response = JSON.parse(JSON.stringify(submissionResponse.data));
                    setSubmissionData(response);
                })
                .catch(error => {
                    setSubmissionLoading(true);
                    setSubmissionError(error);
                })
        }, [submissionUrl]);
        return [isSubmissionLoading, submissionError, submissionData];
    },
    getImageObjects(analysis_id) {
        return create_fake_image_array_list(4);
    },
    getDiscussionComments(analysis_id, user_id) {
        return fake_discussion_output(analysis_id, user_id, 10);
    }
}
