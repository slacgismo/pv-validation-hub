import { Typography } from '@mui/material';
import { Box, Container } from '@mui/system';
import PropTypes from 'prop-types';

export default function Rules(props) {

    return (
        <Container>
            <Box sx={{ flexGrow: 1, border: '1px black' }}>
                <Typography variant='h5'>
                    {"Rules for " + props.title}
                </Typography>
                <Typography variant='body2' sx={{marginTop: 2}}>
                    {props.description}
                </Typography>
            </Box>
        </Container >
    )
}

Rules.props = {
    analysis_id: PropTypes.string
}