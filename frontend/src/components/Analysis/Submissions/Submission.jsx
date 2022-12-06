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

    const get_score_from_result = (value) => {
        if (value == null && value == undefined) return null;
        let value_obj = JSON.parse(value);
        if (value_obj == null && value_obj == undefined) return null;
        let result = value_obj["result"];
        if (result == null && result == undefined) return null;
        let final_score = 0;
        let count = 1;
        for (var split of result) {
            final_score += split["split" + count]["score"]
            console.log(final_score);
            count += 1;
        }
        return final_score;
    }

    const get_evaluation_time = (value) => {
        if (value == null && value == undefined) return null;
        let value_obj = JSON.parse(value);
        if (value_obj == null && value_obj == undefined) return null;
        let time = value_obj["execution_time"];
        if (time == null && time == undefined) return null;
        return time;
    }

    const columns = [
        {
            id: 'analysis',
            label: 'Analysis ID',
            minWidth: 50,
            aligh: 'center',
            format: (value) => {
                return value != null ? value.analysis_id : null
            }
        },
        {
            id: 'result',
            label: 'Score',
            minWidth: 50,
            align: 'left',
            format: (value) => {
                return get_score_from_result(value)
            },
        },
        {
            id: 'submitted_at',
            label: 'Submitted Date',
            minWidth: 100,
            aligh: 'left'
        },
        {
            id: 'execution_time',
            label: 'Execution Time',
            minWidth: 100,
            aligh: 'center',
            key: 'result',
            format: (value) => {
                return get_evaluation_time(value);
            }
        },
        {
            id: 'status',
            label: 'Status',
            minWidth: 50,
            align: 'left',
            format: (value) => {
                return (status_to_icon[value])
            }
        },
        {
            id: 'algorithm',
            label: 'Algorithm',
            minWidth: 50,
            align: 'center',
            format: (value) => {
                value = value.replace("/media/", "//");
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