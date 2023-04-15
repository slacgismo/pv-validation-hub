import { DashboardService } from "../../../services/dashboard_service";
import AppTable from "../../GlobalComponents/AppTable/AppTable";
import PropTypes from 'prop-types';
import { Box, CircularProgress, Link } from "@mui/material";
import { DataGrid, GridToolbar } from '@mui/x-data-grid';
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
                return params.row.developer_group /* value != null || value != undefined ?
                    <Link href={`/profile/${value.id}`} underline="hover" > {value.username}</Link>
                    : null */
            }
        },
        {
            field: 'algorithm',
            headerName: 'Submission',
            filterable: false,
            sortable: false,
            groupable: false,
            width: 100,
            renderCell: (params) => {
                let value = params.row.algorithm;
                // value = value.replace("/media/", "//");
                return (<a href={value} download><DownloadIcon /></a>);
            }
        },
        {
            field: 'error',
            headerName: 'Error',
            headerAlign: 'center',
            align: 'center',
            width: 200,
            type: 'number',
            valueGetter: (params) => {
                let value = params.row.error;
                return value != null && value != undefined ? value : null;
            }
        },
        {
            field: 'execution_time',
            headerName: 'Execution Time',
            headerAlign: 'center',
            align: 'center',
            type: 'number',
            width: 200,
            valueGetter: (params) => {
                let value = params.row.execution_time;
                return value != null && value != undefined ? value : null;
            }
        },
        {
            field: 'data_requirement',
            headerName: 'Data Requirement',
            filterable: false,
            sortable: false,
            groupable: false,
            width: 190,
        },
        {
            field: 'metrics',
            headerName: 'Metrics',
            filterable: false,
            sortable: false,
            groupable: false,
            width: 180,
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
                    components={{
                        Toolbar: GridToolbar,
                    }}
                />
            </Box>
    )
}

Leaderboard.props = {
    analysis_id: PropTypes.string
}

