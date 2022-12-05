import { DashboardService } from "../../../services/dashboard_service";
import AppTable from "../../GlobalComponents/AppTable/AppTable";
import PropTypes from 'prop-types';
import { CircularProgress } from "@mui/material";
export default function Leaderboard(props) {

    const columns = [
        { id: 'ranking_number', label: 'Ranking', minWidth: 100 },
        { id: 'developer_group', label: 'Developer Group', minWidth: 350 },
        {
            id: 'submission',
            label: 'Submission',
            minWidth: 100,
            align: 'center'
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

