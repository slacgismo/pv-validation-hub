import * as React from 'react';
import { Container } from '@mui/system';
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
import SummarizeIcon from '@mui/icons-material/Summarize';
import QueryBuilderIcon from '@mui/icons-material/QueryBuilder';
import DoneIcon from '@mui/icons-material/Done';
import { useState, useEffect } from 'react';
import SubmissionReport from '../Report/report.jsx';
import SubmissionService from '../../../services/submission_service.js';
import UserService from '../../../services/user_service.js';

export default function DeveloperHome() {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const [showComponent, setShowComponent] = useState({ name: 'home' });

  // const container = window !== undefined ? () => window().document.body : undefined;

  const handleNavClick = (component, submissionId) => {
    setShowComponent({ name: component, submissionId });
  };

  const renderComponent = () => {
    if (showComponent.name === 'home') {
      return <Home onClick={(submissionId) => handleNavClick('report', submissionId)} />;
    } if (showComponent.name === 'report') {
      return <SubmissionReport submissionId={showComponent.submissionId} />;
    }
  };

  const navs = [
    {
      title: 'Submissions',
      icon: <AccessTimeIcon />,
      handler: () => { handleNavClick('home'); },
    },
    {
      title: 'Available Analyses',
      icon: <AssessmentIcon />,
      handler: () => {},
    },
  ];

  return (
    <Container sx={{ position: 'absolute' }}>
      <Grid container alignItems="center" spacing={2}>
        <Grid item xs={3}>
          <Box component="Nav" aria-label="mailbox folders" sx={{ position: 'fixed', display: 'flex' }}>
            <Drawer variant="permanent" sx={{ top: '10%', border: '1px solid rgba(0, 0, 0, 0.12)' }} open>
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
            </Drawer>
          </Box>
        </Grid>

        <Grid item xs={9} style={{ marginTop: '2%' }}>
          <Box
            component="main"
            display="flex"
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
  const [submissions, setSubmissions] = useState([]);

  useEffect(() => {
    const fetchSubmissions = async () => {
      const user = UserService.getUserCookie();
      const user_id = await UserService.getUserId(user.token);
      SubmissionService.getAllSubmissionsForUser(user_id)
        .then((fetchedSubmissions) => {
          setSubmissions(fetchedSubmissions);
        });
    };

    fetchSubmissions();
  }, []);

  return (
    <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
      {submissions.sort(
        (a, b) => new Date(b.submitted_at) - new Date(a.submitted_at),
      ).map((submission, index) => {
        const labelId = `checkbox-list-label-${submission.submission_id}`;
        return (
          <ListItem key={submission.submission_id} disablePadding>
            <ListItemButton dense>
              <ListItemIcon>
                <Checkbox
                  edge="start"
                  tabIndex={-1}
                  disableRipple
                  inputProps={{ 'aria-labelledby': labelId }}
                />
              </ListItemIcon>
              <ListItemIcon>
                {submission.status === 'finished' ? <DoneIcon /> : <QueryBuilderIcon />}
              </ListItemIcon>
              <ListItemText id={labelId} primary={`Submission ${submission.submission_id}`} />
              <ListItemIcon onClick={() => onClick(submission.submission_id)}>
                {' '}
                {/* Pass the submission id directly */}
                <SummarizeIcon />
              </ListItemIcon>
            </ListItemButton>
          </ListItem>
        );
      })}
    </List>
  );
}
