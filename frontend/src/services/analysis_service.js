import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import client from './api_service.js';

const AnalysisService = {
  useGetCardDetails() {
    const { analysis_id } = useParams();
    const [analysisDetails, setAnalysisDetails] = useState({});
    const [isAnalysisLoading, setAnalysisIsLoading] = useState(true);
    const [analysiserror, setAnalysisError] = useState(null);
    useEffect(() => {
      client.get(`analysis/${analysis_id}`)
        .then((response) => {
          setAnalysisIsLoading(false);
          console.log(response.data);
          setAnalysisDetails(response.data);
        })
        .catch((error) => {
          if (window.location.hostname.includes('localhost') && (analysis_id === 'development')) {
            setAnalysisDetails({
              analysis_id: 'development',
              analysis_name: 'Dev Analysis',
            });
            setAnalysisIsLoading(false);
            console.log('Loading development analysis');
          } else {
            setAnalysisError(error);
            setAnalysisIsLoading(false);
          }
        });
    }, [analysis_id]);
    return [isAnalysisLoading, analysiserror, analysisDetails, analysis_id];
  },
  uploadAlgorithm(analysis_id, token, file) {
    if (analysis_id !== null && analysis_id !== undefined
            && file !== null && file !== undefined) {
      const url = `/submissions/analysis/${analysis_id}/submission`;
      const formData = new FormData();

      // set authorization token
      client.defaults.headers.common.Authorization = `Token ${token}`;

      formData.append('algorithm', file);
      formData.append('analysis_id', analysis_id);

      client.post(url, formData, {
        Accept: '*/*',
        'content-type': 'multipart/form-data',
      }).then((response) => {
        console.log(response);
      });
    }
  },
};

export default AnalysisService;
