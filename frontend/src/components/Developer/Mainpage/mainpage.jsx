import * as React from 'react';
import { Container } from "@mui/system";
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import AssessmentIcon from '@mui/icons-material/Assessment';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Checkbox from '@mui/material/Checkbox';
import ArticleIcon from '@mui/icons-material/Article';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import Toolbar from '@mui/material/Toolbar';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import Grid from '@mui/material/Grid';
import SubmissionReport from '../Report/report';
import SummarizeIcon from '@mui/icons-material/Summarize';
import QueryBuilderIcon from '@mui/icons-material/QueryBuilder';
import DoneIcon from '@mui/icons-material/Done';
import { useState } from "react";

export default function DeveloperHome() {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const [showComponent, setShowComponent] = useState('home');

  // const container = window !== undefined ? () => window().document.body : undefined;

  const handleNavClick = (component) => {
    setShowComponent(component);
  }

  const renderComponent = () => {
    if (showComponent === 'home') {
      return <Home onClick={() => handleNavClick('report')}/>;
    } else if (showComponent === 'report') {
      return <SubmissionReport />;
    }
  }

  const navs = [
    {
      title: 'Submissions',
      icon: <AccessTimeIcon />,
      handler: () => { handleNavClick("home") },
    },
    {
      title: 'Participanted Analyses',
      icon: <AssessmentIcon />,
      handler: () => {},
    },
    {
      title: 'Used Datasets',
      icon: <ArticleIcon />,
      handler: () => {},
    }
  ];

  return (
    <Container sx={{position: 'absolute'}}>
      <Grid container alignItems="center" spacing={2}>
        <Grid item xs = {3}>
          <Box component="Nav" aria-label="mailbox folders" sx={{ position: 'fixed', display: 'flex'}}>
            <Drawer variant="permanent"  sx={{ top: '10%', border: '1px solid rgba(0, 0, 0, 0.12)', }} open>
              <Toolbar />
              <Divider />
              <List>
                {navs.map((item) => (
                  <ListItem key={item.title} disablePadding>
                    <ListItemButton onClick={item.handler}>
                      <ListItemIcon>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText primary={item.title} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
              <Divider />
              <List>
                {['Bookmark'].map((text, index) => (
                  <ListItem key={text} disablePadding>
                    <ListItemButton>
                      <ListItemIcon>
                        <BookmarkIcon />
                      </ListItemIcon>
                      <ListItemText primary={text} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Drawer>
          </Box>
        </Grid>

        <Grid item xs = {9} style={{ marginTop: '2%' }}>
            <Box
              component="main"
              display="flex"
              // justifyContent="center"
              // alignItems="center"
            >
              <Toolbar />
              {renderComponent()}
            </Box>
        </Grid>
      </Grid>
    </Container>
  );
}

function Home({ onClick }) {
  return (
    <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
      {[1, 2, 3, 4].map((value, index) => {
        const labelId = `checkbox-list-label-${value}`;
        return (
          <ListItem key={value} disablePadding>
            <ListItemButton dense>
              <ListItemIcon>
                <Checkbox
                  edge="start"
                  // checked={checked.indexOf(value) !== -1}
                  tabIndex={-1}
                  disableRipple
                  inputProps={{ 'aria-labelledby': labelId }}
                />
              </ListItemIcon>
              <ListItemIcon>
                { index % 2 === 0? <DoneIcon /> : <QueryBuilderIcon/>}
              </ListItemIcon>
              <ListItemText id={labelId} primary={`Submission ${value}`} />
              <ListItemIcon onClick={onClick}>
                <SummarizeIcon />
              </ListItemIcon>
            </ListItemButton>
          </ListItem>
        );
      })}
    </List>
  )
}
