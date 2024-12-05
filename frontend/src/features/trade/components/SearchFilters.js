import React from 'react';
import { Grid, TextField, Button } from '@material-ui/core';
import { Search as SearchIcon } from '@material-ui/icons';

export const SearchFilters = ({ filters, onChange, onSearch, onReset }) => {
  return (
   <Grid container spacing={3} alignItems="flex-end">
     <Grid item xs={12} md={3}>
       <TextField
         fullWidth
         variant="outlined"
         name="inst_id"
         label="Instrument ID"
         value={filters.inst_id}
         onChange={onChange}
       />
     </Grid>
     <Grid item xs={12} md={3}>
       <TextField
         fullWidth
         variant="outlined"
         type="datetime-local"
         name="fill_start_time"
         label="Start Time"
         value={filters.fill_start_time}
         onChange={onChange}
         InputLabelProps={{ shrink: true }}
       />
     </Grid>
     <Grid item xs={12} md={3}>
       <TextField
         fullWidth
         variant="outlined"
         type="datetime-local"
         name="fill_end_time"
         label="End Time"
         value={filters.fill_end_time}
         onChange={onChange}
         InputLabelProps={{ shrink: true }}
       />
     </Grid>
     <Grid item xs={12} md={3}>
       <Box display="flex" gap={1}>
         <Button
           fullWidth
           variant="contained"
           color="primary"
           onClick={onSearch}
           startIcon={<SearchIcon />}
         >
           Search
         </Button>
         <Button
           fullWidth
           variant="outlined"
           onClick={onReset}
         >
           Reset
         </Button>
       </Box>
     </Grid>
   </Grid>
 );
};