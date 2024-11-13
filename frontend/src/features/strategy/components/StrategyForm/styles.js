import { makeStyles } from '@material-ui/core/styles';

export const useStyles = makeStyles((theme) => ({
  drawer: {
    width: '50%',
    minWidth: 600,
    maxWidth: 800,
  },
  drawerPaper: {
    width: '50%',
    minWidth: 600,
    maxWidth: 800,
    padding: theme.spacing(3),
  },
  title: {
    marginBottom: theme.spacing(3),
  },
  formControl: {
    marginBottom: theme.spacing(3),
  },

  divider: {
    margin: theme.spacing(4, 0),
  },
  weekDayChip: {
    margin: theme.spacing(0.5),
  },
  stopLossItem: {
    marginBottom: theme.spacing(2),
    padding: theme.spacing(2),
    backgroundColor: theme.palette.background.default,
  },
  addButton: {
    marginBottom: theme.spacing(3),
  },
  wrapper: {
    position: 'relative',
  },
  buttonProgress: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    marginTop: -12,
    marginLeft: -12,
  },
  error: {
    color: theme.palette.error.main,
    fontSize: '0.75rem',
    marginTop: theme.spacing(0.5),
  },
}));