import React from 'react';
import {
  Box, Button, Grid, Typography,
} from '@mui/material';
import PropTypes from 'prop-types';
import ReactMarkdown from 'react-markdown';

export default function Data({ dataDescription, downloadableLink }) {
  const handleDownloadClick = (url) => {
    const a = document.createElement('a');
    a.href = url;
    a.download = url.split('/').pop();
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <Grid container spacing={2}>
      <Grid item md={8}>
        <Box>
          <Typography variant="h3">
            Dataset Description
          </Typography>
          <Typography variant="body2">
            { /* eslint-disable-next-line */ }
            <ReactMarkdown children={dataDescription} />
          </Typography>
        </Box>
      </Grid>
      <Grid item md={4}>
        <Box sx={{ marginTop: 7, marginLeft: 10 }}>
          <Typography variant="h6">
            Files
          </Typography>
          <Typography variant="body2">
            {3}
          </Typography>
          <Typography variant="h6">
            Type
          </Typography>
          <Typography variant="body2">
            ZIP
          </Typography>
          <Button
            align="right"
            onClick={() => { handleDownloadClick(downloadableLink); }}
            variant="contained"
            disabled={(downloadableLink === undefined) || (downloadableLink === null)}
            sx={{
              backgroundColor: 'black', width: '100%', height: '75%', fontSize: 'small', marginTop: 3,
            }}
          >
            Download Files
          </Button>
        </Box>
      </Grid>
    </Grid>
  );
}

Data.propTypes = {
  dataDescription: PropTypes.string.isRequired,
  downloadableLink: PropTypes.string,
};

Data.defaultProps = {
  downloadableLink: null,
};
