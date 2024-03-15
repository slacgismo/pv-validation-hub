import * as React from 'react';
import { useEffect, useState } from 'react';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Typography from '@mui/material/Typography';
import Proptypes from 'prop-types';
import SubmissionService from '../../../services/submission_service.js';

export default function SubmissionReport({ submissionId }) {
  const [imageUrls, setImageUrls] = useState([]);

  useEffect(() => {
    const fetchSubmissionResults = async () => {
      try {
        const result = await SubmissionService.getSubmissionResults(submissionId);
        setImageUrls(result.file_urls);
      } catch (error) {
        console.error('Error fetching submission results:', error);
      }
    };

    fetchSubmissionResults();
  }, [submissionId]);

  return (
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

  );
}

SubmissionReport.propTypes = {
  submissionId: Proptypes.number.isRequired,
};
