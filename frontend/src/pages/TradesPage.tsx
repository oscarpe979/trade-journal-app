import React, { useEffect, useState } from 'react';
import { getTrades } from '../services/tradeService';
import { useAuth } from '../contexts/AuthContext';
import { DataGrid, GridToolbar } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import { Box, Paper, Typography, Button, ThemeProvider, createTheme } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import AddIcon from '@mui/icons-material/Add';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3',
      light: '#64b5f6',
      dark: '#1976d2',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#4caf50',
      light: '#81c784',
      dark: '#388e3c',
      contrastText: '#ffffff',
    },
    background: {
      default: '#051423',
      paper: '#051423',
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
    },
    success: {
      main: '#4caf50',
      dark: '#388e3c',
    },
    error: {
      main: '#f44336',
      dark: '#d32f2f',
    },
    divider: 'rgba(255, 255, 255, 0.08)',
  },
  typography: {
    fontFamily: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h5: {
      fontWeight: 500,
      letterSpacing: 0.5,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
});

interface Trade {
  id: number;
  execution_time: string;
  spread?: string;
  side: string;
  quantity: number;
  position_effect: string;
  symbol: string;
  expiration_date?: string;
  strike_price?: number;
  option_type?: string;
  price: number;
  net_price: number;
  order_type?: string;
}

const TradesPage: React.FC = () => {
  const { user, token } = useAuth();
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrades = async () => {
      if (user && token) {
        try {
          setLoading(true);
          const response = await getTrades(token);
          //console.log('Raw response from backend:', response);
          response.forEach((trade: Trade) => {
            //console.log(`Trade ID: ${trade.id}, Price Type: ${typeof trade.price}, Price Value:`, trade.price);
          });
          // Transform dates to proper format for display
          const formattedTrades = response.map((trade: Trade) => ({
            ...trade,
            execution_time: new Date(trade.execution_time).toLocaleString(),
            expiration_date: trade.expiration_date ? new Date(trade.expiration_date).toLocaleDateString() : '',
            price: typeof trade.price === 'string' ? parseFloat(trade.price) : trade.price,
            net_price: typeof trade.net_price === 'string' ? parseFloat(trade.net_price) : trade.net_price,
          }));
          setTrades(formattedTrades);
        } catch (error) {
          console.error('Error fetching trades:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    fetchTrades();
  }, [user, token]);

  const columns: GridColDef[] = [
    { 
      field: 'execution_time', 
      headerName: 'Exec Time', 
      width: 200,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'side', 
      headerName: 'Side',
      width: 100,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'quantity', 
      headerName: 'Qty',
      type: 'number',
      width: 100,
      align: 'right',
      headerAlign: 'right',
      renderCell: (params) => (
        <Typography variant="body2" sx={{ width: '100%', textAlign: 'right', fontFamily: 'monospace' }}>
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'position_effect', 
      headerName: 'Pos Effect',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'symbol', 
      headerName: 'Symbol',
      width: 100,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'option_type', 
      headerName: 'Type',
      width: 100,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'price', 
      headerName: 'Price',
      width: 100,
      align: 'right',
      headerAlign: 'right',
      renderCell: (params) => (
        <Typography variant="body2" sx={{ width: '100%', textAlign: 'right', fontFamily: 'monospace' }}>
          ${params.row.price.toFixed(2)}
        </Typography>
      )
    }
  ];

  return (
    <ThemeProvider theme={darkTheme}>
      <Box sx={{ 
        flexGrow: 1,
        overflow: 'auto', 
        p: 3,
        bgcolor: 'background.default'
      }}>
        {/* Title section with actions */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          mb: 3 
        }}>
          <Typography
            component="h1"
            variant="h5"
            sx={{ 
              flexGrow: 1,
              color: 'primary.light',
              fontWeight: 500
            }}
          >
            Trading Activity
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<DownloadIcon />}
              sx={{ 
                borderColor: 'primary.light',
                color: 'primary.light',
                '&:hover': {
                  borderColor: 'primary.main',
                  bgcolor: 'rgba(144, 202, 249, 0.08)'
                }
              }}
            >
              Export
            </Button>
            <Button
              variant="contained"
              size="small"
              startIcon={<AddIcon />}
              sx={{ 
                bgcolor: 'primary.dark',
                '&:hover': {
                  bgcolor: 'primary.main'
                }
              }}
            >
              New Trade
            </Button>
          </Box>
        </Box>

        {/* Main content */}
        <Paper 
          elevation={0}
          sx={{ 
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 0,
            overflow: 'hidden',
            bgcolor: 'background.paper',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}
        >
          <DataGrid
            rows={trades}
            columns={columns}
            loading={loading}
            pageSizeOptions={[10, 25, 50, 100]}
            initialState={{
              pagination: { paginationModel: { pageSize: 25 } },
            }}
            sx={{
              border: 'none',
              color: 'text.primary',
              backgroundColor: 'transparent',
              '& .MuiDataGrid-main': {
                backgroundColor: 'transparent',
              },
              '& .MuiDataGrid-cell': {
                borderColor: 'rgba(255, 255, 255, 0.08)',
                py: 1.5,
                px: 2,
                '&:focus': {
                  outline: 'none',
                },
                '&:first-of-type': {
                  pl: 2,
                },
                '&:last-of-type': {
                  pr: 2,
                }
              },
              '& .MuiDataGrid-columnHeaders': {
                borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                minHeight: '60px !important',
                maxHeight: '60px !important',
                '& .MuiDataGrid-columnHeader': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  fontWeight: 600,
                  fontSize: '0.875rem',
                  '&:focus': {
                    outline: 'none',
                  },
                  '& .MuiDataGrid-columnHeaderTitle': {
                    fontWeight: 600,
                  }
                }
              },
              '& .MuiDataGrid-row': {
                backgroundColor: 'transparent',
                minHeight: '52px !important',
                maxHeight: '52px !important',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.04)',
                },
                '&.Mui-selected': {
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.12)',
                  }
                }
              },
              '& .MuiDataGrid-virtualScroller': {
                backgroundColor: 'transparent',
              },
              '& .MuiDataGrid-footerContainer': {
                borderTop: '1px solid rgba(255, 255, 255, 0.08)',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                minHeight: '52px !important',
                maxHeight: '52px !important',
              },
              '& .MuiTablePagination-root': {
                color: 'rgba(255, 255, 255, 0.7)',
              },
              '& .MuiDataGrid-toolbarContainer': {
                padding: '8px 24px',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                '& .MuiButton-root': {
                  color: 'primary.light',
                  textTransform: 'none',
                  fontSize: '0.875rem',
                },
                '& .MuiInputBase-root': {
                  borderRadius: 1,
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  '& .MuiInputBase-input': {
                    color: 'text.primary',
                    fontSize: '0.875rem',
                  }
                }
              }
            }}
            autoHeight
            density="comfortable"
            disableRowSelectionOnClick
            getRowId={(row) => row.id}
            slots={{
              toolbar: GridToolbar,
            }}
            slotProps={{
              toolbar: {
                showQuickFilter: true,
                quickFilterProps: { debounceMs: 500 },
              },
            }}
          />
        </Paper>
      </Box>
    </ThemeProvider>
  );
};

export default TradesPage;
