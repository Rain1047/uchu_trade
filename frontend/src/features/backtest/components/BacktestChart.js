import React, { useState } from 'react';
import { Box, Typography } from '@material-ui/core';
import { useStyles } from '../utils/styles';

export const BacktestChart = ({ records }) => {
  const classes = useStyles();
  const [tooltipData, setTooltipData] = useState(null);

  if (!records?.length) return null;

  // Calculate chart boundaries
  const maxValue = Math.max(...records.map(r => Math.abs(r.transaction_pnl))) * 1.2;
  const dates = records.map(r => new Date(r.transaction_time));
  const minDate = Math.min(...dates);
  const maxDate = Math.max(...dates);

  const getXPosition = (date) => {
    const timestamp = new Date(date).getTime();
    return ((timestamp - minDate) / (maxDate - minDate)) * 100 + '%';
  };

  const getYPosition = (value) => {
    return (50 - (value / maxValue) * 50) + '%';
  };

  return (
    <div className={classes.plotContainer}>
      <div className={classes.axisContainer}>
        <div className={classes.centerLine} />

        {records.map((record, index) => (
          <div
            key={index}
            className={`${classes.point} ${record.transaction_pnl >= 0 ? classes.profitPoint : classes.lossPoint}`}
            style={{
              left: getXPosition(record.transaction_time),
              top: getYPosition(record.transaction_pnl),
            }}
            onMouseEnter={(e) => setTooltipData({
              x: e.clientX,
              y: e.clientY,
              data: record
            })}
            onMouseLeave={() => setTooltipData(null)}
          />
        ))}

        <div className={classes.yAxis}>
          <span>${maxValue.toFixed(0)}</span>
          <span>0</span>
          <span>-${maxValue.toFixed(0)}</span>
        </div>

        <div className={classes.xAxis}>
          <span>{new Date(minDate).toLocaleDateString()}</span>
          <span>{new Date(maxDate).toLocaleDateString()}</span>
        </div>
      </div>

      {tooltipData && (
        <div className={classes.tooltip} style={{
          left: tooltipData.x + 10,
          top: tooltipData.y - 40
        }}>
          <div>日期: {new Date(tooltipData.data.transaction_time).toLocaleDateString()}</div>
          <div>收益: ${tooltipData.data.transaction_pnl.toFixed(2)}</div>
          <div>{tooltipData.data.transaction_result}</div>
        </div>
      )}
    </div>
  );
};