
import React from 'react';
import { Box, Typography, Modal, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import type { Trade, Order } from '../../types';

interface OrdersModalProps {
  trade: Trade | null;
  onClose: () => void;
}

const style = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: '80%',
  maxWidth: '1200px',
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
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
      <Box sx={style}>
        <Typography id="trade-orders-modal-title" variant="h6" component="h2">
          Orders for Trade #{trade.id}
        </Typography>
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }} aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell>Execution Time</TableCell>
                <TableCell>Side</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Position Effect</TableCell>
                <TableCell>Price</TableCell>
                <TableCell>Net Price</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {trade.orders.map((order: Order) => (
                <TableRow key={order.id}>
                  <TableCell>{new Date(order.execution_time).toLocaleString()}</TableCell>
                  <TableCell>{order.side}</TableCell>
                  <TableCell>{order.quantity}</TableCell>
                  <TableCell>{order.position_effect}</TableCell>
                  <TableCell>${order.price.toFixed(2)}</TableCell>
                  <TableCell>${order.net_price.toFixed(2)}</TableCell>
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
