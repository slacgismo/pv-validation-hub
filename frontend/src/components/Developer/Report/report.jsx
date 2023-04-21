import * as React from 'react';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Divider from '@mui/material/Divider';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';


export default function SubmissionReport() {
  const rows = [
    {
      name: 'Full DST',
      value: '13.77',
    },
    {
      name: 'Partial DST',
      value: '12.76',
    },
    {
      name: 'Wrong time zone',
      value: '17.84',
    },
    {
      name: 'Baseline (no issues)',
      value: '0.39',
    },
    {
      name: 'Random time shifts',
      value: '5.8'
    }
  ];

  return (
    <List>
      <ListItem disablePadding>
        <TableContainer component={Paper}>
          <Table aria-label="simple table">
            <TableHead>
              <TableRow>
                <TableCell colSpan={3} align="center">
                  <Typography variant="h6" style={{ fontWeight: 'bold' }}>Table: average error by data issue</Typography>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Data set label</TableCell>
                <TableCell align="right">Average MAE</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow
                  key={row.name}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    {row.name}
                  </TableCell>
                  <TableCell align="right">{row.value}</TableCell> 
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </ListItem>

      <Divider sx={{margin: '5%'}}/>

      <ListItem disablePadding sx={{margin: '3%'}}>
        <ImageList sx={{ width: '100%', bgcolor: 'background.paper' }}>
          <ImageListItem key='img0'>
              <img
                src='https://cdn.discordapp.com/attachments/1082129393784193034/1096567880818110575/histo-dsf.png'
                alt='img0'
                loading="lazy"
              />
              <Typography variant="subtitle1">Plot: histogram of errors by data issue</Typography>
            </ImageListItem>
          <ImageListItem key='img1'>
              <img
                src='https://cdn.discordapp.com/attachments/1082129393784193034/1096567941182537758/histo-di.png'
                alt='img1'
                loading="lazy"
              />
              <Typography variant="subtitle1">Plot: histogram of errors by data set frequency</Typography>
            </ImageListItem>
        </ImageList>
      </ListItem>
    </List>

  )
}
