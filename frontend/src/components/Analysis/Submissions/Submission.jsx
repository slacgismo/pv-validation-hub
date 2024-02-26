import React from 'react';
import PropTypes from 'prop-types';
import { CircularProgress, Tooltip } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import PublishedWithChangesIcon from '@mui/icons-material/PublishedWithChanges';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import RunCircleIcon from '@mui/icons-material/RunCircle';
import SmsFailedIcon from '@mui/icons-material/SmsFailed';
import CloudDoneIcon from '@mui/icons-material/CloudDone';
import LinkIcon from '@mui/icons-material/Link';
import Cookies from 'universal-cookie';
import AppTable from '../../GlobalComponents/AppTable/AppTable.js';
import DashboardService from '../../../services/dashboard_service.js';

export default function Submission(props) {
  const statusToIcon = {
    submitted: <Tooltip title="Submitted"><PublishedWithChangesIcon /></Tooltip>,
    submitting: <Tooltip title="Submitting"><AccessTimeIcon /></Tooltip>,
    running: <Tooltip title="Running"><RunCircleIcon /></Tooltip>,
    failed: <Tooltip title="Failed"><SmsFailedIcon /></Tooltip>,
    finished: <Tooltip title="Finished"><CloudDoneIcon /></Tooltip>,
  };

  // const get_score_from_result = (result) => {
  //     if (result == null && result == undefined) return null;
  //     let final_score = 0;
  //     let count = 1;
  //     for (var split of result) {
  //         final_score += split["split" + count]["score"]
  //         console.log(final_score);
  //         count += 1;
  //     }
  //     return final_score;
  // }

  const getEvaluationTime = (time) => {
    if (time === null && time === undefined) return null;
    return time;
  };

  const columns = [
    {
      id: 'analysis',
      label: 'Analysis ID',
      minWidth: 50,
      align: 'center',
      format: (value) => (value !== null ? value.analysis_id : null),
    },
    // {
    //     id: 'result',
    //     label: 'Score',
    //     minWidth: 50,
    //     align: 'left',
    //     format: (value) => {
    //         return get_score_from_result(value)
    //     },
    // },
    {
      id: 'submitted_at',
      label: 'Submitted Date',
      minWidth: 100,
      align: 'left',
      format: (value) => (value !== undefined || value !== null ? value.split('T')[0] : null),
    },
    {
      id: 'execution_time',
      label: 'Execution Time',
      minWidth: 100,
      align: 'center',
      key: 'result',
      format: (value) => getEvaluationTime(value),
    },
    {
      id: 'status',
      label: 'Status',
      minWidth: 50,
      align: 'left',
      format: (value) => (statusToIcon[value]),
    },
    {
      id: 'algorithm',
      label: 'Algorithm',
      minWidth: 50,
      align: 'center',
      format: (value) =>
      // value = value.replace("/media/", "//");
        (<a href={value} download><DownloadIcon /></a>),

    },
    {
      id: 'submission_id',
      label: 'More Information',
      minWidth: 50,
      align: 'center',
      format: (value) => (<a href={`/submission/${value}`}><LinkIcon /></a>),
    },
  ];

  const cookies = new Cookies();
  const user = cookies.get('user');
  const url = `submissions/analysis/${props.analysis_id}/user_submission`;
  const [isLoading, error, rows] = DashboardService.useGetSubmissions(url, user.token);

  console.log('isLoading before appTable: ', isLoading);
  console.log('rows before appTable: ', rows);
  console.log('error: ', error);

  return (
    isLoading ? <CircularProgress />
      : (
        <AppTable
          cols={columns}
          rows={rows}
        />
      )
  );
}

Submission.props = {
  analysis_id: PropTypes.string,
  user_id: PropTypes.string,
};
