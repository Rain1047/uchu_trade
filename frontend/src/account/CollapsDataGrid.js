import React, { useState } from 'react';
import { DataGrid, GridToolbar } from '@mui/x-data-grid';
import IconButton from '@mui/material/IconButton';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import Box from '@mui/material/Box';
import Collapse from '@mui/material/Collapse';
import Typography from '@mui/material/Typography';

const columns = [
    { field: 'id', headerName: 'ID', width: 90 },
    { field: 'name', headerName: 'Dessert (100g serving)', width: 200 },
    { field: 'calories', headerName: 'Calories', type: 'number', width: 130 },
    { field: 'fat', headerName: 'Fat (g)', type: 'number', width: 120 },
    { field: 'carbs', headerName: 'Carbs (g)', type: 'number', width: 130 },
    { field: 'protein', headerName: 'Protein (g)', type: 'number', width: 140 },
];

const rows = [
    { id: 1, name: 'Frozen yoghurt', calories: 159, fat: 6.0, carbs: 24, protein: 4.0 },
    { id: 2, name: 'Ice cream sandwich', calories: 237, fat: 9.0, carbs: 37, protein: 4.3 },
    { id: 3, name: 'Eclair', calories: 262, fat: 16.0, carbs: 24, protein: 6.0 },
    { id: 4, name: 'Cupcake', calories: 305, fat: 3.7, carbs: 67, protein: 4.3 },
    { id: 5, name: 'Gingerbread', calories: 356, fat: 16.0, carbs: 49, protein: 3.9 },
];

const CollapsibleDataGrid = () => {
    const [expandedRowIds, setExpandedRowIds] = useState([]);

    const handleToggleCollapse = (id) => {
        setExpandedRowIds((prevExpandedRowIds) =>
            prevExpandedRowIds.includes(id)
                ? prevExpandedRowIds.filter((rowId) => rowId !== id)
                : [...prevExpandedRowIds, id]
        );
    };

    return (
        <div style={{ height: 400, width: '100%' }}>
            <DataGrid
                rows={rows}
                columns={columns}
                pageSize={5}
                components={{
                    Toolbar: () => <GridToolbar />,
                }}
                isRowSelectable={(params) => false}
                onRowClick={(params) => handleToggleCollapse(params.id)}
                componentsProps={{
                    toolbar: { showColumnSelector: false },
                }}
                disableColumnSelector
                disableColumnMenu
                autoHeight
                checkboxSelection={false}
                getRowId={(row) => row.id}
                expandedRowIds={expandedRowIds}
                onExpandedRowsChange={(newExpandedRowIds) => setExpandedRowIds(newExpandedRowIds)}
                hideFooter
            />
            {rows.map((row) => (
                <Collapse key={row.id} in={expandedRowIds.includes(row.id)} timeout="auto" unmountOnExit>
                    <Box margin={1}>
                        <Typography variant="h6" gutterBottom component="div">
                            History
                        </Typography>
                        {/* Add your additional content for each row here */}
                    </Box>
                </Collapse>
            ))}
        </div>
    );
};

export default CollapsibleDataGrid;
