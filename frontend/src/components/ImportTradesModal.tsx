import React, { useState } from 'react';
import { Box, Typography, Modal, Select, MenuItem, Button, IconButton, FormControl, InputLabel, CircularProgress } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '../contexts/AuthContext';
import { uploadOrders } from '../services/orderService';

interface ImportTradesModalProps {
  open: boolean;
  onClose: () => void;
}

const style = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: '30%',
  minWidth: '500px',
  bgcolor: '#1E293B',
  border: '1px solid #334155',
  borderRadius: '8px',
  boxShadow: 24,
  p: 4,
  color: '#F8FAFC',
};

const timezones = [
  'America/Bogota',
  'Australia/Brisbane',
];

const ImportTradesModal: React.FC<ImportTradesModalProps> = ({ open, onClose }) => {
  const { token } = useAuth();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedTimezone, setSelectedTimezone] = useState<string>(timezones[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
      setError(null);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv'],
    },
    multiple: false,
  });

  const handleTimezoneChange = (event: any) => {
    setSelectedTimezone(event.target.value as string);
  };

  const handleUpload = async () => {
    if (!selectedFile || !token) return;

    setLoading(true);
    setError(null);

    try {
      await uploadOrders(selectedFile, selectedTimezone, token);
      onClose(); // Close modal on success
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    setError(null);
    setLoading(false);
    onClose();
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      aria-labelledby="import-trades-modal-title"
    >
      <Box sx={style}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography id="import-trades-modal-title" variant="h6" component="h2" sx={{ color: '#64b5f6' }}>
            Import Trades
          </Typography>
          <IconButton onClick={handleClose} sx={{ color: '#94A3B8' }}>
            <CloseIcon />
          </IconButton>
        </Box>

        <Box
          {...getRootProps()}
          sx={{
            border: `2px dashed ${isDragActive ? '#60A5FA' : '#334155'}`,
            borderRadius: '4px',
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            mb: 2,
          }}
        >
          <input {...getInputProps()} />
          {selectedFile ? (
            <Typography>{selectedFile.name}</Typography>
          ) : (
            <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Drag & drop a .xlsx or .csv file here, or click to select a file</Typography>
          )}
        </Box>

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel id="timezone-select-label" sx={{ color: '#94A3B8' }}>Timezone</InputLabel>
          <Select
            labelId="timezone-select-label"
            value={selectedTimezone}
            label="Timezone"
            onChange={handleTimezoneChange}
            sx={{ color: '#F8FAFC', '.MuiOutlinedInput-notchedOutline': { borderColor: '#334155' } }}
          >
            {timezones.map(tz => (
              <MenuItem key={tz} value={tz}>{tz}</MenuItem>
            ))}
          </Select>
        </FormControl>

        {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}

        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!selectedFile || loading}
          fullWidth
          sx={{
            '&.Mui-disabled': {
              backgroundColor: 'rgba(255, 255, 255, 0.12)',
              color: 'rgba(255, 255, 255, 0.5)',
            },
          }}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : 'Upload'}
        </Button>
      </Box>
    </Modal>
  );
};

export default ImportTradesModal;