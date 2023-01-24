import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import client from "./api_service";

export const AnalysisService = {

    useGetCardDetails() {
        const { analysis_id } = useParams();
        const [analysisDetails, setAnalysisDetails] = useState();
        const [isAnalysisLoading, setAnalysisIsLoading] = useState(true);
        const [analysiserror, setAnalysisError] = useState(null);
        useEffect(() => {
            client.get("analysis/" + analysis_id)
                .then(response => {
                    setAnalysisIsLoading(false);
                    console.log(response.data);
                    setAnalysisDetails(response.data);
                })
                .catch(error => {
                    setAnalysisError(error);
                    setAnalysisIsLoading(false);
                })
        }, [analysis_id]);
        return [isAnalysisLoading, analysiserror, analysisDetails, analysis_id];
    },
    async uploadAlgorithm(analysis_id, user_id, file) {
        if (analysis_id != null && analysis_id != undefined && 
            user_id != null && user_id != undefined &&
            file != null && file != undefined
            ) {
            let url = "/jobs/analysis/" + analysis_id + "/submission";
            let form_data = new FormData();
            form_data.append("algorithm", file);
            form_data.append("user_id", user_id);
            form_data.append("analysis_id", analysis_id);
            client.post(url, form_data, {
                Accept: '*/*',
                "content-type": 'multipart/form-data'
            });
            await client.post(url, {
                analysis_id: analysis_id,
                user_id: user_id,
                file: file
            });
        }
    },
}