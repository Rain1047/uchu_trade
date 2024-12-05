import { makeStyles } from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  paginationContainer: {
    display: 'flex',
    justifyContent: 'flex-end',
    alignItems: 'center',
    padding: theme.spacing(2),
    gap: theme.spacing(2)
  },
  buyChip: {
    backgroundColor: '#1b5e20',
    color: '#fff'
  },
  sellChip: {
    backgroundColor: '#b71c1c',
    color: '#fff'
  },
  pageControl: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1)
  },
  searchContainer: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: theme.spacing(2)
  },
  noteField: {
    minWidth: '200px',
    '& .MuiOutlinedInput-root': {
      '& fieldset': {
        borderColor: 'rgba(255, 255, 255, 0.23)',
      }
    }
  }
}));