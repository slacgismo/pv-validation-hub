import { faker } from "@faker-js/faker";
import { Alert, Box, Button, TextField, Typography } from "@mui/material";
import { Container } from "@mui/system";
import { useState } from "react";
import { DashboardService } from "../../../services/dashboard_service";
import { FileUploader } from "react-drag-drop-files";

const defaultValues = {
    name: "Analysis " + faker.word.noun(),
    short_description: "",
    long_description: "",
    image: faker.image.food(),
    rules: "",
    dataset_description: ""
}

export function UploadAnalysis(props) {

    const [analysisFormValues, setAnalysisFormValues] = useState(defaultValues);
    const [errored, setErrored] = useState("none");
    const [success, setSuccess] = useState("none");
    const fileTypes = ["ZIP"];
    const [evaluationScript, setEvaluationScript] = useState(null);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setAnalysisFormValues({
            ...analysisFormValues,
            [name]: value,
        });
    };

    const uploadFile = (evaluationScript) => {
        setEvaluationScript(evaluationScript);
    };

    const handleSubmit = () => {
        let response = DashboardService.uploadAnalysis(
            props.user_id,
            analysisFormValues.name,
            analysisFormValues.long_description,
            analysisFormValues.short_description,
            evaluationScript,
            analysisFormValues.rules,
            analysisFormValues.dataset_description
        );
        if (response == null) {
            setErrored("block");
            setTimeout(() => { setErrored("none") }, 10)
            setAnalysisFormValues(defaultValues);
            setEvaluationScript(null);
        }
        else {
            setSuccess("block");
            setTimeout(() => { setSuccess("none") }, 10)
            setAnalysisFormValues(defaultValues);
            setEvaluationScript(null);
        }
    }
    return (
        <Container>
            <Alert sx={{ display: errored }} severity="error">Failed to create analysis - {analysisFormValues.name}</Alert>
            <Alert sx={{ display: success }} severity="success">Successfully created analysis - {analysisFormValues.names}</Alert>
            <form onSubmit={handleSubmit}>
                <Container sx={{
                    marginTop: 5,
                    marginLeft: 30,
                    '& .MuiTextField-root': {
                        m: 1,
                        width: '60ch'
                    }
                }}>
                    <Box sx={{ marginTop: 2 }}>
                        <TextField
                            id="anaylsis_name"
                            name="name"
                            label="Name"
                            type="text"
                            value={analysisFormValues.name}
                            onChange={handleInputChange}
                        />

                    </Box>
                    <Box sx={{ marginTop: 2 }}>
                        <TextField
                            id="summary"
                            name="short_description"
                            label="Summary"
                            type="text"
                            multiline
                            minRows={4}
                            maxRows={10}
                            value={analysisFormValues.short_description}
                            onChange={handleInputChange}
                        />
                    </Box>
                    <Box sx={{ marginTop: 2 }}>
                        <TextField
                            id="description"
                            name="long_description"
                            label="Overview"
                            type="text"
                            multiline
                            minRows={7}
                            maxRows={20}
                            value={analysisFormValues.long_description}
                            onChange={handleInputChange}
                        />
                    </Box>
                    <Box sx={{ marginTop: 2 }}>
                        <TextField
                            id="dataset_description"
                            name="dataset_description"
                            label="Dataset Description"
                            type="text"
                            multiline
                            minRows={7}
                            maxRows={20}
                            value={analysisFormValues.dataset_description}
                            onChange={handleInputChange}
                        />
                    </Box>
                    <Box sx={{ marginTop: 2 }}>
                        <TextField
                            id="rules"
                            name="rules"
                            label="Rule Set"
                            type="text"
                            multiline
                            minRows={7}
                            maxRows={20}
                            value={analysisFormValues.rules}
                            onChange={handleInputChange}
                        />
                    </Box>
                    <Box sx={{ marginTop: 2 }}>
                        <Box sx={{ marginBottom: 2 }}>
                            <FileUploader
                                multiple={false}
                                handleChange={uploadFile}
                                name="file"
                                types={fileTypes}
                            />
                        </Box>
                        <Typography color="gray" variant="body1">
                            {
                                evaluationScript != null
                                    ? `File name: ${evaluationScript.name}`
                                    : "No files uploaded yet."
                            }
                        </Typography>
                    </Box>
                    <Box sx={{ marginTop: 2 }}>
                        <Button variant="contained" type="submit">
                            Submit
                        </Button>
                    </Box>
                </Container>
            </form>
        </Container>
    )
}