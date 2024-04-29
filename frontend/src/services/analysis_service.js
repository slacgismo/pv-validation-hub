import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import client from './api_service.js';

const AnalysisService = {
  useGetCardDetails() {
    const { analysisId } = useParams();
    const [analysisDetails, setAnalysisDetails] = useState({});
    const [isAnalysisLoading, setAnalysisIsLoading] = useState(true);
    const [analysiserror, setAnalysisError] = useState(null);
    useEffect(() => {
      client.get(`analysis/${analysisId}`)
        .then((response) => {
          setAnalysisIsLoading(false);
          console.log(response.data);
          setAnalysisDetails(response.data);
        })
        .catch((error) => {
          if (window.location.hostname.includes('localhost') && (analysisId === 'development')) {
            setAnalysisDetails({
              analysisId: 'development',
              analysis_name: 'Dev Analysis',
            });
            setAnalysisIsLoading(false);
            console.log('Loading development analysis');
          } else {
            setAnalysisError(error);
            setAnalysisIsLoading(false);
          }
        });
    }, [analysisId]);
    return [isAnalysisLoading, analysiserror, analysisDetails, analysisId];
  },
  uploadAlgorithm(analysisId, token, file) {
    if (analysisId !== null && analysisId !== undefined
          && file !== null && file !== undefined) {
      const url = `/submissions/analysis/${analysisId}/submission`;
      const formData = new FormData();

      // set authorization token
      client.defaults.headers.common.Authorization = `Token ${token}`;

      // analysis_id is the expected format on the backend
      formData.append('algorithm', file);
      formData.append('analysis_id', analysisId);

      // Return the Promise from client.post
      return client.post(url, formData, {
        Accept: '*/*',
        'content-type': 'multipart/form-data',
      });
    }

    // If analysisId or file is null or undefined, return a rejected Promise
    return Promise.reject(new Error('analysisId and file cannot be null or undefined'));
  },
};

export default AnalysisService;
