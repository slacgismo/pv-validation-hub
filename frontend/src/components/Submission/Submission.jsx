import React from 'react';
import { Grid } from '@mui/material';
import Cookies from 'universal-cookie';
import { Box } from '@mui/system';
import { useParams } from 'react-router-dom';
import BarChart from './BarChart.jsx';
import CardBar from './CardBar.jsx';
import CardSummary from './CardSummary.jsx';
import SubmissionService from '../../services/submission_service.js';
import BlurryPage from '../GlobalComponents/BlurryPage/blurryPage.jsx';

export default function Submission() {
  const cookies = new Cookies();
  const user = cookies.get('user');
  const { submission_id } = useParams();
  const submissionData = SubmissionService.getSubmissionDetails(user, submission_id);
  return (
    <Box sx={{ marginTop: 5, marginLeft: 4, marginRight: 4 }}>
      {
        user === undefined || user == null
          ? <BlurryPage />
          : (
            <Grid container spacing={3}>
              <Grid item xl={3} lg={3} md={4} sm={6} xs={12}>
                <CardSummary
                  title="Data from Submissions"
                  value={submissionData.total_submissions}
                  footer={(
                    <div>
                      {' '}
                      {Math.abs(submissionData.total_submissions_change)}
                      {submissionData.total_submissions_change > 0 ? '% increase' : '% decrease'}
                      {' '}
                      from yesterday
                      {' '}
                    </div>
)}
                />
              </Grid>
              <Grid item xl={3} lg={3} md={4} sm={6} xs={12}>
                <CardSummary
                  title="Successfull Submissions"
                  value={submissionData.successful_submissions}
                  footer={(
                    <div>
                      {' '}
                      {Math.abs(submissionData.successful_submissions_change)}
                      {submissionData.successful_submissions_change > 0 ? '% increase' : '% decrease'}
                      {' '}
                      from yesterday
                      {' '}
                    </div>
)}
                />
              </Grid>
              <Grid item xl={3} lg={3} md={4} sm={6} xs={12}>
                <CardSummary
                  title="Errored Submission"
                  value={submissionData.errored_submissions}
                  footer={(
                    <div>
                      {' '}
                      {Math.abs(submissionData.errored_submissions_change)}
                      {submissionData.errored_submissions_change > 0 ? '% increase' : '% decrease'}
                      {' '}
                      from last week
                      {' '}
                    </div>
)}
                />
              </Grid>
              <Grid item xl={3} lg={3} md={4} sm={6} xs={12}>
                <CardSummary
                  title="Total Points"
                  value={submissionData.score}
                  footer={(
                    <div>
                      {' '}
                      {Math.abs(submissionData.score_change)}
                      {submissionData.score_change > 0 ? '% increase' : '% decrease'}
                      {' '}
                      from last week
                      {' '}
                    </div>
)}
                />
              </Grid>
              <Grid item xl={12} lg={12} md={12} sm={12} xs={12}>
                <CardBar title="Activity" chart={<BarChart user_id={user} />} />
              </Grid>
            </Grid>
          )
      }
    </Box>
  );
}
