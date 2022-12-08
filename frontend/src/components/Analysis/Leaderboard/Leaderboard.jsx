import { DashboardService } from "../../../services/dashboard_service";
import AppTable from "../../GlobalComponents/AppTable/AppTable";
import PropTypes from 'prop-types';
import { Box, CircularProgress, Link } from "@mui/material";
import { DataGrid } from '@mui/x-data-grid';
import DownloadIcon from '@mui/icons-material/Download';
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
                let value = params.value;
                return value != null || value != undefined ?
                    <Link href={`/profile/${value.id}`} underline="hover" > {value.username}</Link>
                    : null
            }
        },
        {
            field: 'algorithm',
            headerName: 'Submission',
            filterable: false,
            sortable: false,
            groupable: false,
            width: 150,
            align: 'center',
            renderCell: (params) => {
                let value = params.row.algorithm;
                value = value.replace("/media/", "//");
                return (<a href={value} download><DownloadIcon /></a>);
            }
        },
        {
            field: 'error',
            headerName: 'Error',
            width: 150,
            align: 'center',
            valueGetter: (params) => {
                let value = params.row.error;
                return value != null && value != undefined ? value : null;
            }
        },
        {
            field: 'execution_time',
            headerName: 'Execution Time',
            type: 'dateTime',
            width: 190,
            align: 'center',
            valueGetter: (params) => {
                let value = params.row.execution_time;
                return value != null && value != undefined ? new Date(value.split("T")[0]) : null;
            }
        },
        {
            field: 'data_requirement',
            headerName: 'Data Requirement',
            filterable: false,
            sortable: false,
            groupable: false,
            width: 190,
            align: 'center'
        },
        {
            field: 'metrics',
            headerName: 'Metrics',
            filterable: false,
            sortable: false,
            groupable: false,
            width: 180,
            align: 'center'
        }
    ]
    let url = "/analysis/" + props.analysis_id + "/leaderboard";
    const [isLoading, error, rows] = DashboardService.useGetLeaderBoard(url);
    return (
        isLoading || rows === undefined ? <CircularProgress /> :
            <Box sx={{ height: 600 }}>
                <DataGrid
                    columns={columns}
                    rows={rows}
                />
            </Box>
    )
}

Leaderboard.props = {
    analysis_id: PropTypes.string
}

