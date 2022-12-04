import { DashboardService } from "../../../services/dashboard_service";
import AppTable from "../../GlobalComponents/AppTable/AppTable";
import PropTypes from 'prop-types';
import { CircularProgress, Tooltip } from "@mui/material";
import DownloadIcon from '@mui/icons-material/Download';
import PublishedWithChangesIcon from '@mui/icons-material/PublishedWithChanges';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import RunCircleIcon from '@mui/icons-material/RunCircle';
import SmsFailedIcon from '@mui/icons-material/SmsFailed';
import CloudDoneIcon from '@mui/icons-material/CloudDone';
export default function Submission(props) {

    const status_to_icon = {
        "submitted": <Tooltip title="Submitted"><PublishedWithChangesIcon /></Tooltip>,
        "submitting": <Tooltip title="Submitting"><AccessTimeIcon /></Tooltip>,
        "running": <Tooltip title="Running"><RunCircleIcon /></Tooltip>,
        "failed": <Tooltip title="Failed"><SmsFailedIcon /></Tooltip>,
        "finished": <Tooltip title="Finished"><CloudDoneIcon /></Tooltip>
    }

    const columns = [
        {
            id: 'analysis',
            label: 'Analysis ID',
            minWidth: 100,
            aligh: 'center',
            format: (value) => {
                return value != null ? value.analysis_id : null
            }
        },
        // { id: 'ranking_id', label: 'Ranking', minWidth: 170 },
        {
            id: 'result',
            label: 'Result',
            minWidth: 120,
            align: 'left',
            format: (value) => {
                return value != null ? value.split1.score : null
            },
        },
        {
            id: 'status',
            label: 'Status',
            minWidth: 120,
            align: 'right',
            format: (value) => {
                return (status_to_icon[value])
            }
        },
        {
            id: 'algorithm',
            label: 'Algorithm',
            minWidth: 200,
            align: 'center',
            format: (value) => {
                value = value.replace("/media/","//");
                return (<a href={value} download><DownloadIcon /></a>);
            }
        },
    ]
    let url = "jobs/analysis/" + props.analysis_id + "/user_submission/" + props.user_id;
    const [isLoading, error, rows] = DashboardService.useGetSubmissions(url);
    return (
        isLoading ? <CircularProgress /> :
            <AppTable
                columns={columns}
                rows={rows}
            />
    )
}

Submission.props = {
    analysis_id: PropTypes.string,
    user_id: PropTypes.string
}