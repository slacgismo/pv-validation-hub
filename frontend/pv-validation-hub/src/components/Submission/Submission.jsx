import BarChart from "./BarChart";
import React from "react";
import { CardBar } from "./CardBar"
import { CardSummary } from "./CardSummary";
import { Grid } from "@mui/material";
import { SubmissionService } from "../../services/submission_service";
import Cookies from 'universal-cookie';

export default function Submission() {
  const cookies = new Cookies();
  var user = cookies.get("user");
  user = user === undefined || user == null ? "juliusomo" : user;
  const submissionData = SubmissionService.getSubmissionDetails(user);

  return (
    <Grid sx={{ marginTop: 4 }}>
      <Grid container spacing={3}>
        <Grid item xl={3} lg={3} md={4} sm={6} xs={12}>
          <CardSummary
            title="Solution Submitted this week"
            value={submissionData.total_submissions}
            footer={<div> {Math.abs(submissionData.total_submissions_change)}
              {submissionData.total_submissions_change > 0 ? "% increase" : "% decrease"
              } from yesterday </div>}
          />
        </Grid>
        <Grid item xl={3} lg={3} md={4} sm={6} xs={12}>
          <CardSummary
            title="Successfull Submissions"
            value={submissionData.successful_submissions}
            footer={<div> {Math.abs(submissionData.successful_submissions_change)}
              {submissionData.successful_submissions_change > 0 ? "% increase" : "% decrease"
              } from yesterday </div>}
          />
        </Grid>
        <Grid item xl={3} lg={3} md={4} sm={6} xs={12}>
          <CardSummary
            title="Errored Submission"
            value={submissionData.errored_submissions}
            footer={<div> {Math.abs(submissionData.errored_submissions_change)}
              {submissionData.errored_submissions_change > 0 ? "% increase" : "% decrease"
              } from last week </div>}
          />
        </Grid>
        <Grid item xl={3} lg={3} md={4} sm={6} xs={12}>
          <CardSummary
            title="Total Points"
            value={submissionData.score}
            footer={<div> {Math.abs(submissionData.score_change)}
              {submissionData.score_change > 0 ? "% increase" : "% decrease"
              } from last week </div>}
          />
        </Grid>
        <Grid item xl={12} lg={12} md={12} sm={12} xs={12}>
          <CardBar title="Activity" chart={<BarChart user_id={user} />} />
        </Grid>
      </Grid>
    </Grid>
  );
}
