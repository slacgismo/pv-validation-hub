import React, { Component } from 'react';
import Chart from 'react-apexcharts';
import SubmissionService from '../../services/submission_service.js';

export default class BarChart extends Component {
  constructor(props) {
    super(props);

    this.state = {
      options: {
        chart: {
          id: 'submission-bar',
        },
        xaxis: {
          categories: SubmissionService.getSubmissionDateRangeSet(props.user_id),
        },
      },
      series: [
        {
          name: 'submissions',
          data: SubmissionService.getSubmissionsSet(props.user_id),
        },
      ],
    };
  }

  render() {
    return (
      <div className="app">
        <div className="row">
          <div className="mixed-chart">
            <Chart
              options={this.state.options}
              series={this.state.series}
              type="bar"
            />
          </div>
        </div>
      </div>
    );
  }
}
