import { DashboardService } from "../../../services/dashboard_service";
import AppTable from "../../GlobalComponents/AppTable/AppTable";
import PropTypes from 'prop-types';
export default function Leaderboard(props) {

    const columns = [
        { id: 'ranking_number', label: 'Ranking', minWidth: 100 },
        { id: 'developer_name', label: 'Developer', minWidth: 170 },
        {
            id: 'score',
            label: 'Score',
            minWidth: 120,
            align: 'right',
            format: (value) => value.toLocaleString('en-US'),
        },
        {
            id: 'entries',
            label: 'Entries',
            minWidth: 120,
            align: 'right',
            format: (value) => value.toLocaleString('en-US'),
        },
        {
            id: 'last_updated',
            label: 'Last Updated',
            minWidth: 120,
            align: 'right'
        },
        {
            id: 'code_url',
            label: 'Code',
            minWidth: 200,
            align: 'center'
        },
    ]
    const rows = DashboardService.getLeaderBoard(props.analysis_id);
    console.log(rows);
    return (
        <AppTable
            columns={columns}
            rows={rows}
        />
    )
}

Leaderboard.props = {
    analysis_id: PropTypes.string
}

