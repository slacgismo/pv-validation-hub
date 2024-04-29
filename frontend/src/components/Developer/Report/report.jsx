import * as React from 'react';
import { useEffect, useState } from 'react';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Proptypes from 'prop-types';
import SubmissionService from '../../../services/submission_service.js';

export default function SubmissionReport({ submissionId }) {
  const [imageUrls, setImageUrls] = useState([]);
  const [errorData, setErrorData] = useState([]);
  const [displayErrorDetails, setDisplayErrorDetails] = useState(false);

  useEffect(() => {
    const fetchSubmissionErrors = async () => {
      try {
        const errors = await SubmissionService.getSubmissionErrors(submissionId);
        console.log('Error data:', errors);
        if (errors.length === 0) {
          setErrorData({ error_rate: '0%' });
          setDisplayErrorDetails(false);
        } else if (errors.length > 0) {
          let tempErrorData = errors[0];
          if (tempErrorData.error_type.toLowerCase().includes('operation'.toLowerCase())
            || tempErrorData.error_type.toLowerCase().includes('wrapper'.toLowerCase())
            || tempErrorData.error_type.toLowerCase().includes('worker'.toLowerCase())) {
            tempErrorData = { ...tempErrorData, error_rate: 'N/A' };
          }
          setErrorData(tempErrorData);
          setDisplayErrorDetails(true);
        }
      } catch (error) {
        console.error('Error fetching submission results:', error);
      }
    };

    const fetchSubmissionResults = async () => {
      try {
        const result = await SubmissionService.getSubmissionResults(submissionId);
        setImageUrls(result.file_urls);
      } catch (error) {
        console.error('Error fetching submission results:', error);
      }
    };

    fetchSubmissionResults();
    fetchSubmissionErrors();
  }, [submissionId]);

  return (
    <div>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Error Rate:
            {' '}
            {errorData.error_rate}
          </Typography>
          {displayErrorDetails && (
          <>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Error Code:
              {' '}
              {errorData.error_code}
            </Typography>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Error Type:
              {' '}
              {errorData.error_type}
            </Typography>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Error Message:
              {' '}
              {errorData.error_message}
            </Typography>
          </>
          )}
        </AppBar>
      </Box>

      <List>
        <ListItem disablePadding sx={{ margin: '3%' }}>
          <ImageList sx={{ width: '100%', bgcolor: 'background.paper' }}>
            {imageUrls.map((url, index) => {
              const notIndex = index + 1;
              return (
                <ImageListItem key={`img${notIndex}`}>
                  <img
                    src={url}
                    alt={`img${index}`}
                    loading="lazy"
                  />
                  <Typography variant="subtitle1">
                    Plot
                    {index + 1}
                  </Typography>
                </ImageListItem>
              );
            })}
          </ImageList>
        </ListItem>
      </List>
    </div>

  );
}

SubmissionReport.propTypes = {
  submissionId: Proptypes.number.isRequired,
};
