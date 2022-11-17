import { Box, Button, Grid, Typography } from "@mui/material";
import { DashboardService } from "../../../services/dashboard_service";
import PropTypes from 'prop-types';

export default function Data(props) {

    const datasetDetails = DashboardService.getAnalysisDataset(props.analysis_id);

    const handleDownloadClick = (url) => {
        const a = document.createElement('a')
        a.href = url
        a.download = url.split('/').pop()
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
    }

    return (
        <Grid container spacing={2}>
            <Grid item md={8}>
                <Box>
                    <Typography variant="h3">
                        Dataset Description
                    </Typography>
                    <Typography variant="body2">
                        {datasetDetails.description}
                    </Typography>
                    <Typography variant="body2">
                        <b>Test Data: </b> {datasetDetails.train_data}
                    </Typography>
                    <Typography variant="body2">
                        <b>Train Data: </b> {datasetDetails.test_data}
                    </Typography>
                    <Typography variant="body2">
                        <b>Final Note: </b> {datasetDetails.final_note}
                    </Typography>
                </Box>
            </Grid>
            <Grid item md={4}>
                <Box sx={{ marginTop: 7, marginLeft: 10 }}>
                    <Typography variant="h6">
                        Files
                    </Typography>
                    <Typography variant="body2">
                        {datasetDetails.number_of_files}
                    </Typography>
                    <Typography variant="h6">
                        Type
                    </Typography>
                    <Typography variant="body2">
                        {datasetDetails.type_of_files}
                    </Typography>
                    <Button align="right" onClick={() => { handleDownloadClick(datasetDetails.file) }} variant="contained" sx={{ backgroundColor: "black", width: "100%", height: "75%", fontSize: "small", marginTop: 3}}>
                        Download Files
                    </Button>
                </Box>
            </Grid>
        </Grid>
    );
}

Data.props = {
    analysis_id: PropTypes.string
}