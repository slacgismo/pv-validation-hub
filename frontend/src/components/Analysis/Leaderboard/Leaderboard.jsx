import { DashboardService } from "../../../services/dashboard_service";
import AppTable from "../../GlobalComponents/AppTable/AppTable";
import PropTypes from 'prop-types';
import { CircularProgress } from "@mui/material";
import DownloadIcon from '@mui/icons-material/Download';
export default function Leaderboard(props) {

    const columns = [
        {
            id: 'ranking_number',
            label: 'Ranking',
            minWidth: 100,
            key: "index"
        },
        {
            id: 'created_by',
            label: 'Developer Group',
            minWidth: 350,
            format: (value) => {
                return value != null || value != undefined ? value.username : null
            }
        },
        {
            id: 'algorithm',
            label: 'Submission',
            minWidth: 100,
            align: 'center',
            format: (value) => {
                value = value.replace("/media/", "//");
                return (<a href={value} download><DownloadIcon /></a>);
            }
        },
    ]
    let url = "/analysis/" + props.analysis_id + "/leaderboard";
    const [isLoading, error, rows] = DashboardService.useGetLeaderBoard(url);

    return (
        isLoading ? <CircularProgress /> :
            <AppTable
                columns={columns}
                rows={rows}
            />
    )
}

Leaderboard.props = {
    analysis_id: PropTypes.string
}

