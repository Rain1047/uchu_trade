import { makeStyles } from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  root: {
    marginTop: theme.spacing(3),
  },
  paper: {
    backgroundColor: '#222',
    padding: theme.spacing(3),
    marginBottom: theme.spacing(3),
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
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: theme.spacing(3),
    marginTop: theme.spacing(3),
    padding: theme.spacing(2),
    backgroundColor: '#1a1a1a',
    borderRadius: theme.shape.borderRadius,
  },
  statItem: {
    textAlign: 'center',
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
  height: 400,
  margin: theme.spacing(4),
  backgroundColor: '#1a1a1a',
  borderRadius: theme.shape.borderRadius,
},
axisContainer: {
  position: 'absolute',
  left: 60,
  right: 20,
  top: 20,
  bottom: 40,
  borderLeft: '1px solid #444',
  borderBottom: '1px solid #444',
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
  backgroundColor: '#333',
  border: '1px solid #444',
  padding: theme.spacing(1),
  borderRadius: 4,
  fontSize: 12,
  pointerEvents: 'none',
  zIndex: 1000,
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
  left: 0,
  right: 0,
  bottom: -30,
  display: 'flex',
  justifyContent: 'space-between',
  color: '#888',
  fontSize: 12,
},
centerLine: {
  position: 'absolute',
  left: 0,
  right: 0,
  top: '50%',
  borderTop: '1px dashed #444',
}
}));