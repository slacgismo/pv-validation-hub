import {
  Card, CardContent, Typography, Divider,
} from '@mui/material';
import React from 'react';

function CardSummary({ title, value, footer }) {
  return (
    <Card>
      <CardContent>
        <Typography
          gutterBottom
          className="abcdef"
          color="textPrimary"
        >
          {title}
        </Typography>
        <Divider />
        <Typography variant="h3" color="textPrimary">
          {value}
        </Typography>
        <div>{footer}</div>
      </CardContent>
    </Card>
  );
}

export default CardSummary;
