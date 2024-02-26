import React from 'react';
import PropTypes from 'prop-types';
import { Box, CircularProgress, Link } from '@mui/material';
import { DataGrid, GridToolbar } from '@mui/x-data-grid';
import DownloadIcon from '@mui/icons-material/Download';
import { DashboardService } from '../../../services/dashboard_service.js';

export default function Leaderboard(props) {
  const columns = [
    {
      field: 'created_by',
      headerName: 'Developer Group',
      width: 250,
      filterable: false,
      sortable: false,
      groupable: false,
      renderCell: (params) => {
        const { value } = params;
        return params.row.developer_group; /* value !== null || value !== undefined ?
                    <Link href={`/profile/${value.id}`} underline="hover" > {value.username}</Link>
                    : null */
      },
    },
    {
      field: 'algorithm',
      headerName: 'Submission File',
      filterable: false,
      sortable: false,
      groupable: false,
      width: 100,
      renderCell: (params) => {
        let value = params.row.algorithm;
        if (value !== undefined && value !== null) {
          // for demo purpose
          value = value.replace('http://s3', 'http://localhost');
        }
        return (
          <a href={value} download>
            {value}
            <DownloadIcon />
          </a>
        );
      },
    },
    {
      field: 'error',
      headerName: 'Error',
      headerAlign: 'center',
      align: 'center',
      width: 200,
      type: 'number',
      valueGetter: (params) => {
        const value = params.row.error;
        return value !== null && value !== undefined ? value : null;
      },
    },
    {
      field: 'execution_time',
      headerName: 'Execution Time',
      headerAlign: 'center',
      align: 'center',
      type: 'number',
      width: 200,
      valueGetter: (params) => {
        const value = params.row.execution_time;
        return value !== null && value !== undefined ? value : null;
      },
    },
    {
      field: 'metrics',
      headerName: 'Metrics',
      filterable: false,
      sortable: false,
      groupable: false,
      width: 360,
    },
  ];
  const url = `/analysis/${props.analysis_id}/leaderboard`;
  const [isLoading, error, rows] = DashboardService.useGetLeaderBoard(url);
  return (
    isLoading || rows === undefined ? <CircularProgress />
      : (
        <Box sx={{ height: 600 }}>
          <DataGrid
            columns={columns}
            rows={rows}
            components={{
              Toolbar: GridToolbar,
            }}
          />
        </Box>
      )
  );
}

Leaderboard.props = {
  analysis_id: PropTypes.string,
};
