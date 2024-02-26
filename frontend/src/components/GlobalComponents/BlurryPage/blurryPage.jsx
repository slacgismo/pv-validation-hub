import React from 'react';
import { Button, Grid } from '@mui/material';
import { Box } from '@mui/system';
import { useNavigate } from 'react-router-dom';

export default function BlurryPage() {
  const navigate = useNavigate();

  const handleCloseNavMenu = (location) => {
    navigate(`/${location}`);
  };
  return (
    <Box sx={{ backgroundColor: '#C0C0C0', backdropFilter: 'blur(6px)' }}>
      <Grid
        container
        spacing={0}
        direction="column"
        alignItems="center"
        justifyContent="center"
        style={{ minHeight: '100vh' }}
      >

        <Grid item xs={3}>
          <Box sx={{ flexGrow: 0, '& button': { m: 1, maxWidth: '8em', minWidth: '8em' } }}>
            <Button onClick={() => handleCloseNavMenu('login')} variant="outlined">Login</Button>

            <Button onClick={() => handleCloseNavMenu('register')} variant="contained">Register</Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
