import React from 'react';
import { Typography } from '@mui/material';
import { Box, Container } from '@mui/system';
import PropTypes from 'prop-types';
import Markdown from 'markdown-to-jsx';

export default function Rules({ title, description }) {
  return (
    <Container>
      <Box sx={{ flexGrow: 1, border: '1px black' }}>
        <Typography variant="h5">
          {`Rules for ${title}`}
        </Typography>
        { /* eslint-disable-next-line */}
          <Markdown children={description} />
      </Box>
    </Container>
  );
}

Rules.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
};
