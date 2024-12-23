import { makeStyles } from '@material-ui/core/styles';

export const useBalanceTableStyles = makeStyles((theme) => ({
  clickableRow: {
    cursor: 'pointer',
    '&:hover': {
      backgroundColor: theme.palette.action.hover,
    },
  },
  expandedCell: {
    padding: 0,
    backgroundColor: theme.palette.background.default,
  },
  expandedContent: {
    padding: theme.spacing(3),
  },
  profit: {
    color: theme.palette.success.main,
  },
  loss: {
    color: theme.palette.error.main,
  },
  orderTypeChip: {
    marginRight: theme.spacing(1),
  },
  stopLoss: {
    backgroundColor: theme.palette.error.main,
    color: theme.palette.error.contrastText,
  },
  limitOrder: {
    backgroundColor: theme.palette.success.main,
    color: theme.palette.success.contrastText,
  }
}));