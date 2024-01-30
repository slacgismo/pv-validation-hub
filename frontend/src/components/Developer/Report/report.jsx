import * as React from 'react';
import { useEffect, useState } from 'react';
import { SubmissionService } from '../../../services/submission_service';
import { CookieService } from '../../../services/cookie_service';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';


export default function SubmissionReport(props) {
  const [imageUrls, setImageUrls] = useState([]);
  console.log(props)

  useEffect(() => {
    const fetchSubmissionResults = async () => {
      try {
        const result = await SubmissionService.getSubmissionResults(props.submissionId);
        const cloudfront_cookie = result.cloudfront_cookie;

        CookieService.setPrivateReportCookies(props.submissionId, 
          cloudfront_cookie['CloudFront-Policy'], 
          cloudfront_cookie['CloudFront-Signature'], 
          cloudfront_cookie['CloudFront-Key-Pair-Id']);

        setImageUrls(result.file_urls);
        
      } catch (error) {
        console.error('Error fetching submission results:', error);
      }
    };

    fetchSubmissionResults();
  }, [props.submissionId]);

  return (
    <List>
      <ListItem disablePadding sx={{margin: '3%'}}>
        <ImageList sx={{ width: '100%', bgcolor: 'background.paper' }}>
          {imageUrls.map((url, index) => (
            <ImageListItem key={`img${index}`}>
              <img
                src={url}
                alt={`img${index}`}
                loading="lazy"
              />
              <Typography variant="subtitle1">Plot {index + 1}</Typography>
            </ImageListItem>
          ))}
        </ImageList>
      </ListItem>
{/*
      <Divider sx={{margin: '5%'}}/>

      <ListItem disablePadding sx={{margin: '3%'}}>
        <ImageList sx={{ width: '100%', bgcolor: 'background.paper' }}>
          <ImageListItem key='img0'>
              <img
                src='https://cdn.discordapp.com/attachments/1082129393784193034/1096567880818110575/histo-dsf.png'
                alt='img0'
                loading="lazy"
              />
              <Typography variant="subtitle1">Plot: histogram of errors by data issue</Typography>
            </ImageListItem>
          <ImageListItem key='img1'>
              <img
                src='https://cdn.discordapp.com/attachments/1082129393784193034/1096567941182537758/histo-di.png'
                alt='img1'
                loading="lazy"
              />
              <Typography variant="subtitle1">Plot: histogram of errors by data set frequency</Typography>
            </ImageListItem>
        </ImageList>
      </ListItem>
          */}
    </List>

  )
}
