import React, { Component } from 'react';
import Chart from 'react-apexcharts';
import PropTypes from 'prop-types';
import SubmissionService from '../../services/submission_service.js';

export default class BarChart extends Component {
  constructor({ userId }) {
    super({ userId });

    this.state = {
      options: {
        chart: {
          id: 'submission-bar',
        },
        xaxis: {
          categories: SubmissionService.getSubmissionDateRangeSet(userId),
        },
      },
      series: [
        {
          name: 'submissions',
          data: SubmissionService.getSubmissionsSet(userId),
        },
      ],
    };
  }

  render() {
    const { options, series } = this.state;

    return (
      <div className="app">
        <div className="row">
          <div className="mixed-chart">
            <Chart
              options={options}
              series={series}
              type="bar"
            />
          </div>
        </div>
      </div>
    );
  }
}

BarChart.propTypes = {
  userId: PropTypes.string.isRequired,
};
