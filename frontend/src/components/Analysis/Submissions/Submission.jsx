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

// eslint-disable-next-line no-unused-vars
export default function Submission({ analysisId, userId }) {
  const statusToIcon = {
    submitted: <Tooltip title="Submitted"><PublishedWithChangesIcon /></Tooltip>,
    submitting: <Tooltip title="Submitting"><AccessTimeIcon /></Tooltip>,
    running: <Tooltip title="Running"><RunCircleIcon /></Tooltip>,
    failed: <Tooltip title="Failed"><SmsFailedIcon /></Tooltip>,
    finished: <Tooltip title="Finished"><CloudDoneIcon /></Tooltip>,
  };

  const getEvaluationTime = (time) => {
    if (time === null && time === undefined) return null;
    return time;
  };

  const downloadLink = (value) => (
    <a href={value} download aria-label="Download">
      <DownloadIcon />
    </a>
  );

  const linkIcon = (value) => (
    <a href={`/submission/${value}`} aria-label="More Information">
      <LinkIcon />
    </a>
  );

  const columns = [
    {
      id: 'analysis',
      label: 'Analysis ID',
      minWidth: 50,
      align: 'center',
      format: (value) => (value !== null ? value.analysis_id : null),
    },
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
      format: (value) => downloadLink(value),
    },
    {
      id: 'submission_id',
      label: 'More Information',
      minWidth: 50,
      align: 'center',
      format: (value) => linkIcon(value),
    },
  ];

  const cookies = new Cookies();
  const user = cookies.get('user');
  const url = `submissions/analysis/${analysisId}/user_submission`;
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

Submission.propTypes = {
  analysisId: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
  ]).isRequired,
  userId: PropTypes.number.isRequired,
};
