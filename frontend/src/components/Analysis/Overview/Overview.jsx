import { Grid, Typography } from '@mui/material';
import { Box, Container } from '@mui/system';
import PropTypes from 'prop-types';
import { DashboardService } from '../../../services/dashboard_service';
import { ReactMarkdown } from 'react-markdown/lib/react-markdown';

export default function Overview(props) {

    return (
        <Container>
            <Box sx={{ flexGrow: 1, border: '1px black'}}>
                <Typography variant='h5'>
                    {props.title}
                </Typography>
                <Typography variant='body2'>
                    <ReactMarkdown source={props.description} />
                </Typography>
            </Box>
            <Grid container spacing={2} sx={{marginTop: 6}}>
                <Grid item xs={10} md={6}>
                    <Box sx={{ flexGrow: 1, border: '1px solid gray', borderRadius: '5px' }}>
                        <Grid container spacing={2}>
                            <Grid item xs={7} md={6}>
                                <Typography align="center" variant='h4'>
                                    {100}
                                </Typography>
                                <Typography align="center" variant='h6' sx={{color: "gray"}}>
                                    Entries
                                </Typography>
                            </Grid>
                            <Grid item xs={7} md={6}>
                                <Typography align="center" variant='h4'>
                                    {20}
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
                                    {200}
                                </Typography>
                                <Typography align="center" variant='h6' sx={{color: "gray"}}>
                                    Score
                                </Typography>
                            </Grid>
                            <Grid item xs={7} md={6}>
                                <Typography align="center" variant='h4'>
                                    {10}
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