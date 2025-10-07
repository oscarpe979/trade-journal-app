import React from 'react';
import { Box, Typography, Modal, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton, Grid, Chip } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import type { Trade, Order } from '../../types';
import { formatToNY } from '../../utils/dateUtils';

interface OrdersModalProps {
  trade: Trade | null;
  onClose: () => void;
}

const style = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: '40%',
  minWidth: '700px',
  maxWidth: '1200px',
  height: '80%',
  maxHeight: '800px',
  bgcolor: '#1E293B',
  border: '1px solid #334155',
  borderRadius: '8px',
  boxShadow: 24,
  p: 4,
  color: '#F8FAFC',
};

const OrdersModal: React.FC<OrdersModalProps> = ({ trade, onClose }) => {
  if (!trade) {
    return null;
  }

  return (
    <Modal
      open={!!trade}
      onClose={onClose}
      aria-labelledby="trade-orders-modal-title"
      aria-describedby="trade-orders-modal-description"
    >
      <Box sx={{ ...style, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography id="trade-orders-modal-title" variant="h6" component="h2">
            Trade Details
          </Typography>
          <IconButton onClick={onClose} sx={{ color: '#94A3B8' }}>
            <CloseIcon />
          </IconButton>
        </Box>

        <Box sx={{ mb: 2, p: 2, backgroundColor: '#0F172A', borderRadius: '4px' }}>
          <Typography variant="h6" sx={{ mb: 2, color: '#94A3B8' }}>Trade Summary</Typography>
          <Grid container spacing={2}>
            <Grid>
              <Typography variant="body2" sx={{ color: '#94A3B8' }}>Symbol</Typography>
              <Typography variant="body1">{trade.symbol}</Typography>
            </Grid>
            <Grid>
              <Typography variant="body2" sx={{ color: '#94A3B8' }}>Direction</Typography>
              <Typography variant="body1">{trade.direction}</Typography>
            </Grid>
            <Grid>
              <Typography variant="body2" sx={{ color: '#94A3B8' }}>Status</Typography>
              <Chip variant='outlined' label={trade.status} color={trade.status == 'CLOSED' ? 'info' : "warning"} size="small" sx={{ mt: 0.5 }}/>
            </Grid>
            <Grid>
              <Typography variant="body2" sx={{ color: '#94A3B8' }}>Volume</Typography>
              <Typography variant="body1">{trade.volume}</Typography>
            </Grid>
            <Grid>
              <Typography variant="body2" sx={{ color: '#94A3B8' }}>Avg Entry Price</Typography>
              <Typography variant="body1">${trade.avg_entry_price.toFixed(2)}</Typography>
            </Grid>
            <Grid>
              <Typography variant="body2" sx={{ color: '#94A3B8' }}>Avg Exit Price</Typography>
              <Typography variant="body1">{trade.avg_exit_price ? `${trade.avg_exit_price.toFixed(2)}` : '-'}</Typography>
            </Grid>
            <Grid>
              <Typography variant="body2" sx={{ color: '#94A3B8' }}>PNL</Typography>
              <Typography variant="body1" sx={{ color: trade.pnl == null ? 'inherit' : trade.pnl >= 0 ? '#4caf50' : '#f44336' }}>
                {trade.pnl != null ? `${trade.pnl.toFixed(2)}` : '-'}
              </Typography>
            </Grid>
          </Grid>
        </Box>

        <Typography variant="h6" sx={{ mb: 2, color: '#94A3B8' }}>Associated Orders</Typography>
        <TableContainer component={Paper} sx={{ overflowY: 'auto', backgroundColor: '#0F172A', color: '#F8FAFC' }}>
          <Table sx={{ minWidth: 650 }} aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell sx={{ color: '#94A3B8' }}>Execution Time</TableCell>
                <TableCell sx={{ color: '#94A3B8' }}>Side</TableCell>
                <TableCell sx={{ color: '#94A3B8' }}>Quantity</TableCell>
                <TableCell sx={{ color: '#94A3B8' }}>Position Effect</TableCell>
                <TableCell sx={{ color: '#94A3B8' }}>Price</TableCell>
                <TableCell sx={{ color: '#94A3B8' }}>Net Price</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {trade.orders.map((order: Order) => (
                <TableRow 
                  key={order.id}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.04)',
                    },
                  }}
                >
                  <TableCell sx={{ color: '#F8FAFC' }}>{formatToNY(order.execution_time)}</TableCell>
                  <TableCell sx={{ color: '#F8FAFC' }}>{order.side}</TableCell>
                  <TableCell sx={{ color: '#F8FAFC' }}>{order.quantity}</TableCell>
                  <TableCell sx={{ color: '#F8FAFC' }}>{order.position_effect}</TableCell>
                  <TableCell sx={{ color: '#F8FAFC' }}>${order.price.toFixed(2)}</TableCell>
                  <TableCell sx={{ color: '#F8FAFC' }}>${order.net_price.toFixed(2)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Modal>
  );
};

export default OrdersModal;