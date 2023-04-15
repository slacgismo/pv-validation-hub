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
            console.log(response, response["result"]);
            if (response["result"] !== null && response["result"] !== undefined) {
                let result = JSON.parse(response["result"]);
                let details = result["details"];
                for (const [key, value] of Object.entries(details)) {
                    let element = {
                        id: id,
                        algorithm: resp["algorithm"],
                        created_by: resp["created_by"]["username"],
                        execution_time: details[key]["execution_time"],
                        status: resp["status"],
                        metrics: details[key]["outputs"],
                        error: result["error"],
                        data_requirement: null
                    }
                    id += 1;
                    finalResponse.push(element);
                }
            }
            else{
                let element = {
                    id: id,
                    algorithm: resp["algorithm"],
                    created_by: resp["created_by"],
                    execution_time: faker.helpers.arrayElement([66.19317770004272,100.97519278526306]),
                    status: null,
                    metrics: null,
                    error: faker.helpers.arrayElement([23.137764944250826,4.846236274675835]),
                    data_requirement: null
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
                    // setLeaderboardDetails(this.formatResponse(leaderboardResponse.data));
                    setLeaderboardDetails(this.formatResponse(create_fake_leaderboard_array(10)));
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
    getImageObjects(analysis_id) {
        return create_fake_image_array_list(4);
    },
    getDiscussionComments(analysis_id, user_id) {
        return fake_discussion_output(analysis_id, user_id, 10);
    }
}
