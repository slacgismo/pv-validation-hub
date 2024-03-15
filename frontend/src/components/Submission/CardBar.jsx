import {
  Card,
  CardContent,
  Typography,
  Divider,
} from '@mui/material';
import PropTypes from 'prop-types';

import React from 'react';

function CardBar({ title, chart }) {
  return (
    <Card>
      <CardContent>
        <Typography className="cardbar123" color="textPrimary">
          {title}
        </Typography>
        <Divider />
        {chart}
      </CardContent>
    </Card>
  );
}

CardBar.propTypes = {
  title: PropTypes.string.isRequired,
  chart: PropTypes.element.isRequired,
};

export default CardBar;
