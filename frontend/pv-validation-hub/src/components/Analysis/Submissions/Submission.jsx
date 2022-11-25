import { DashboardService } from "../../../services/dashboard_service";
import AppTable from "../../GlobalComponents/AppTable/AppTable";
import PropTypes from 'prop-types';
export default function Submission(props) {

    const columns = [
        { id: 'analysis_id', label: 'Analysis ID', minWidth: 100 },
        { id: 'ranking_id', label: 'Ranking', minWidth: 170 },
        {
            id: 'score',
            label: 'Score',
            minWidth: 120,
            align: 'left',
            format: (value) => value.toLocaleString('en-US'),
        },
        {
            id: 'submit_time',
            label: 'Submit Time',
            minWidth: 120,
            align: 'left'
        },
        {
            id: 'execution_time',
            label: 'Time to Execute',
            minWidth: 120,
            align: 'center'
        },
        {
            id: 'error',
            label: 'Error',
            minWidth: 120,
            align: 'right'
        },
        {
            id: 'algorithm_url',
            label: 'Algorithm',
            minWidth: 200,
            align: 'center'
        },
    ]
    const rows = DashboardService.getSubmission(props.analysis_id);
    return (
        <AppTable
            columns={columns}
            rows={rows}
        />
    )
}

Submission.props = {
    analysis_id: PropTypes.string
}