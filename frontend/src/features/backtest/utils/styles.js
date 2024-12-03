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
  }
}));