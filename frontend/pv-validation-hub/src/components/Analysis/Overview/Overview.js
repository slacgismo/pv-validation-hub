import { Grid, Typography } from '@mui/material';
import { Box, Container } from '@mui/system';
import PropTypes from 'prop-types';
import { DashboardService } from '../../../services/dashboard_service';

export default function Overview(props) {

    const overviewData = DashboardService.getAnalysisOverview(props.analysis_id);

    return (
        <Container>
            <Box sx={{ flexGrow: 1, border: '1px black'}}>
                <Typography variant='h5'>
                    {overviewData.title}
                </Typography>
                <Typography variant='body2'>
                    {overviewData.description}
                </Typography>
            </Box>
            <Grid container spacing={2} sx={{marginTop: 6}}>
                <Grid item xs={10} md={6}>
                    <Box sx={{ flexGrow: 1, border: '1px solid gray', borderRadius: '5px' }}>
                        <Grid container spacing={2}>
                            <Grid item xs={7} md={6}>
                                <Typography align="center" variant='h4'>
                                    {overviewData.number_of_submission}
                                </Typography>
                                <Typography align="center" variant='h6' sx={{color: "gray"}}>
                                    Entries
                                </Typography>
                            </Grid>
                            <Grid item xs={7} md={6}>
                                <Typography align="center" variant='h4'>
                                    {overviewData.number_of_developers}
                                </Typography>
                                <Typography align="center" variant='h6' sx={{color: "gray"}}>
                                    People
                                </Typography>
                            </Grid>
                        </Grid>
                    </Box>
                </Grid>
                <Grid item xs={10} md={6}>
                    <Box sx={{ flexGrow: 1, border: '1px solid gray', borderRadius: '5px' }}>
                        <Grid container spacing={2}>
                            <Grid item xs={7} md={6}>
                                <Typography align="center" variant='h4'>
                                    {overviewData.users_points}
                                </Typography>
                                <Typography align="center" variant='h6' sx={{color: "gray"}}>
                                    Score
                                </Typography>
                            </Grid>
                            <Grid item xs={7} md={6}>
                                <Typography align="center" variant='h4'>
                                    {overviewData.users_ranking}
                                </Typography>
                                <Typography align="center" variant='h6' sx={{color: "gray"}}>
                                    Rank
                                </Typography>
                            </Grid>
                        </Grid>
                    </Box>
                </Grid>
            </Grid>
        </Container >
    )
}

Overview.props = {
    analysis_id: PropTypes.string
}