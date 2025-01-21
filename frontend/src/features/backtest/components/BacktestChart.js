import React, { useState, useRef } from 'react';
import { Box, Typography } from '@material-ui/core';
import { useStyles } from '../utils/styles';

export const BacktestChart = ({ records }) => {
  const classes = useStyles();
  const [tooltipData, setTooltipData] = useState(null);
  const chartRef = useRef(null);

  if (!records?.length) return null;

  // Calculate chart boundaries
  const maxValue = Math.max(...records.map(r => Math.abs(r.transaction_pnl))) * 1.2;
  const dates = records.map(r => new Date(r.transaction_time));
  const minDate = Math.min(...dates);
  const maxDate = Math.max(...dates);

  const getXPosition = (date) => {
    return ((new Date(date).getTime() - minDate) / (maxDate - minDate)) * 100 + '%';
  };

  const getYPosition = (value) => {
    return (50 - (value / maxValue) * 50) + '%';
  };

  const handleMouseEnter = (e, record) => {
    const chartRect = chartRef.current.getBoundingClientRect();
    const pointRect = e.target.getBoundingClientRect();

    const tooltipX = pointRect.left - chartRect.left;
    const tooltipY = pointRect.top - chartRect.top;

    setTooltipData({
      x: tooltipX,
      y: tooltipY,
      data: record
    });
  };


  return (
    <div className={classes.plotContainer} ref={chartRef}>
      <div className={classes.yAxisLabels}>
        <span className={classes.yAxisLabel}>${maxValue.toFixed(0)}</span>
        <span className={classes.yAxisLabel}>0</span>
        <span className={classes.yAxisLabel}>-${maxValue.toFixed(0)}</span>
      </div>

      <div className={classes.axisContainer}>
        <div className={classes.centerLine} />
        <div className={classes.gridLines}>
          <div className={classes.gridLine} style={{ top: '0%' }} />
          <div className={classes.gridLine} style={{ top: '50%' }} />
          <div className={classes.gridLine} style={{ top: '100%' }} />
        </div>

        {records.map((record, index) => (
          <div
            key={index}
            className={`${classes.point} ${record.transaction_pnl >= 0 ? classes.profitPoint : classes.lossPoint}`}
            style={{
              left: getXPosition(record.transaction_time),
              top: getYPosition(record.transaction_pnl),
            }}
            onMouseEnter={(e) => handleMouseEnter(e, record)}
            onMouseLeave={() => setTooltipData(null)}
          />
        ))}

        <div className={classes.xAxis}>
          <span>{new Date(minDate).toLocaleDateString()}</span>
          <span>{new Date(maxDate).toLocaleDateString()}</span>
        </div>

        {tooltipData && (
          <div
            className={classes.tooltip}
            style={{
              left: tooltipData.x + 10,
              top: tooltipData.y - 60
            }}
          >
            <div>日期: {new Date(tooltipData.data.transaction_time).toLocaleDateString()}</div>
            <div>收益: ${tooltipData.data.transaction_pnl.toFixed(2)}</div>
            <div>{tooltipData.data.transaction_result}</div>
          </div>
        )}
      </div>
    </div>
  );
};