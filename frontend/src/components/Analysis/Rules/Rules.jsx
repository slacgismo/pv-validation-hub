import React from 'react';
import { Typography } from '@mui/material';
import { Box, Container } from '@mui/system';
import PropTypes from 'prop-types';
import ReactMarkdown from 'react-markdown';

export default function Rules({ title, description }) {
  return (
    <Container>
      <Box sx={{ flexGrow: 1, border: '1px black' }}>
        <Typography variant="h5">
          {`Rules for ${title}`}
        </Typography>
        <Typography variant="body2" sx={{ marginTop: 2 }}>
          { /* eslint-disable-next-line */}
          <ReactMarkdown children={description} />
        </Typography>
      </Box>
    </Container>
  );
}

Rules.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
};
