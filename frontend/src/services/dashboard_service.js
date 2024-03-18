import { useEffect, useState } from 'react';
import {
  createFakeImageArrayList,
  fakeDiscussionOutput,
} from './fake_data_service.js';
import client from './api_service.js';

const DashboardService = {
  formatResponse(response) {
    const finalResponse = [];
    let id = 0;
    console.log('Printing response');
    console.log(response);
    if (response.length > 0) {
      for (let i = 0; i < response.length; i += 1) {
        const element = {
          id,
          algorithm: response[i].algorithm_s3_path,
          created_by: response[i].created_by.username,
          execution_time: response[i].mrt,
          status: response[i].status,
          metrics: response[i].data_requirements,
          error: response[i].mae,
        };
        id += 1;
        finalResponse.push(element);
      }
    }
    console.log(finalResponse);
    return finalResponse;
  },
  useGetAnalysisSet(analysisUrl) {
    const [analysesDetails, setAnalysesDetails] = useState([]);
    const [isAnalysesLoading, setAnalysesIsLoading] = useState(true);
    const [analysesError, setAnalysesError] = useState(null);

    useEffect(() => {
      client.get(analysisUrl)
        .then((analysisResponse) => {
          setAnalysesIsLoading(false);
          setAnalysesDetails(analysisResponse.data);
        })
        .catch((error) => {
          if (window.location.hostname.includes('localhost') && (analysesDetails.length === 0
                        || analysesDetails.analysis_id === 'development')) {
            setAnalysesDetails([{
              analysis_id: 'development',
              analysis_name: 'Dev Analysis',
            }]);
            setAnalysesIsLoading(false);
            console.log('Using development analysis');
          } else {
            setAnalysesError(error);
            setAnalysesDetails([]);
            setAnalysesIsLoading(false);
          }
        });
      // eslint-disable-next-line
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
        .then((leaderboardResponse) => {
          setLeaderboardIsLoading(false);
          setLeaderboardDetails(this.formatResponse(leaderboardResponse.data));
        })
        .catch((error) => {
          setLeaderboardError(error);
          setLeaderboardDetails([]);
          setLeaderboardIsLoading(false);
        });
    }, [leaderBoardUrl]);
    return [isLeaderboardLoading, leaderboardError, leaderboardDetails];
  },
  useGetSubmissions(submissionUrl, token) {
    const [isSubmissionLoading, setSubmissionLoading] = useState(true);
    const [submissionError, setSubmissionError] = useState(null);
    const [submissionData, setSubmissionData] = useState(null);

    // set authorization token
    client.defaults.headers.common.Authorization = `Token ${token}`;

    useEffect(() => {
      client.get(submissionUrl)
        .then((submissionResponse) => {
          setSubmissionLoading(false);
          const response = JSON.parse(JSON.stringify(submissionResponse.data));
          setSubmissionData(response);
        })
        .catch((error) => {
          setSubmissionLoading(true);
          setSubmissionError(error);
        });
    }, [submissionUrl]);
    return [isSubmissionLoading, submissionError, submissionData];
  },
  // eslint-disable-next-line no-unused-vars
  getImageObjects(analysisId) {
    return createFakeImageArrayList(4);
  },
  getDiscussionComments(analysisId, userId) {
    return fakeDiscussionOutput(analysisId, userId, 10);
  },
};

export default DashboardService;
