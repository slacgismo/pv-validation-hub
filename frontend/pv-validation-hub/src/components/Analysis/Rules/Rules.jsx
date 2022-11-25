import { Typography } from '@mui/material';
import { Box, Container } from '@mui/system';
import PropTypes from 'prop-types';
import { DashboardService } from '../../../services/dashboard_service';

export default function Rules(props) {

    const overviewData = DashboardService.getAnalysisOverview(props.analysis_id);

    return (
        <Container>
            <Box sx={{ flexGrow: 1, border: '1px black' }}>
                <Typography variant='h5'>
                    {overviewData.title}
                </Typography>
                <Typography variant='body2'>
                    {overviewData.description}
                </Typography>
            </Box>
        </Container >
    )
}

Rules.props = {
    analysis_id: PropTypes.string
}