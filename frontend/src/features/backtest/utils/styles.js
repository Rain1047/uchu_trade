import { makeStyles } from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
    padding: theme.spacing(3),
  },
  paper: {
    padding: theme.spacing(3),
    width: '100%',
    backgroundColor: '#1E1E1E',
  },
  controls: {
    display: 'flex',
    gap: theme.spacing(2),
    marginBottom: theme.spacing(3),
    alignItems: 'center',
    flexWrap: 'wrap',
  },
  formControl: {
    minWidth: 200,
    '& .MuiOutlinedInput-root': {
      '& fieldset': {
        borderColor: '#444',
      },
      '&:hover fieldset': {
        borderColor: '#666',
      },
    },
  },
  statsContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(6, 1fr)',
    gap: theme.spacing(2),
    padding: theme.spacing(2),
    marginBottom: theme.spacing(3),
    backgroundColor: '#141414',
    borderRadius: theme.shape.borderRadius,
    width: '100%',
  },
  statItem: {
    textAlign: 'center',
    padding: theme.spacing(2),
  },
  recordPaper: {
    padding: theme.spacing(2),
    backgroundColor: '#1a1a1a',
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
    padding: theme.spacing(4)
  },
  // Add these to your existing styles
plotContainer: {
    position: 'relative',
    width: '100%',
    height: '400px',
    marginTop: theme.spacing(3),
    marginBottom: theme.spacing(3),
    backgroundColor: '#141414',
    borderRadius: theme.shape.borderRadius,
    padding: theme.spacing(3),
    display: 'flex',
  },
  yAxisLabels: {
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    padding: theme.spacing(2),
    paddingTop: '20px',
    paddingBottom: '20px',
    color: 'rgba(255, 255, 255, 0.6)',
    width: '80px',
  },
  yAxisLabel: {
    fontSize: '0.875rem',
    textAlign: 'right',
  },
axisContainer: {
    position: 'relative',
    flex: 1,
    height: '100%',
    marginLeft: theme.spacing(2),
  },
point: {
  position: 'absolute',
  width: 6,
  height: 6,
  borderRadius: '50%',
  transform: 'translate(-50%, -50%)',
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  '&:hover': {
    width: 8,
    height: 8,
    zIndex: 2,
  },
},
profitPoint: {
  backgroundColor: '#5eddac',
},
lossPoint: {
  backgroundColor: '#f57ad0',
},
tooltip: {
    position: 'absolute',
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    color: 'white',
    padding: theme.spacing(1),
    borderRadius: theme.spacing(1),
    fontSize: '0.875rem',
    pointerEvents: 'none',
    zIndex: 1000,
    whiteSpace: 'nowrap',
  },
yAxis: {
  position: 'absolute',
  left: -50,
  top: 0,
  bottom: 0,
  width: 40,
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'space-between',
  color: '#888',
  fontSize: 12,
},
xAxis: {
    position: 'absolute',
    bottom: '-20px',
    left: 0,
    right: 0,
    display: 'flex',
    justifyContent: 'space-between',
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: '0.875rem',
  },
centerLine: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: '50%',
    borderBottom: '1px dashed rgba(255, 255, 255, 0.1)',
  },
  gridLines: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
  },
  gridLine: {
    position: 'absolute',
    left: 0,
    right: 0,
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
  },

runButton: {
  minWidth: 120,
  marginRight: theme.spacing(2)
}
}));