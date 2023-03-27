import * as React from 'react';
import { Container } from "@mui/system";
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import AssessmentIcon from '@mui/icons-material/Assessment';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Checkbox from '@mui/material/Checkbox';
import MailIcon from '@mui/icons-material/Mail';
import ArticleIcon from '@mui/icons-material/Article';
import CommentIcon from '@mui/icons-material/Comment'
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';

const drawerWidth = 240;

export default function DeveloperHome() {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // const container = window !== undefined ? () => window().document.body : undefined;

  return (
    <Container sx={{ position: 'fixed', top: '10%' }}>
          <Grid container alignItems="center" spacing={2}>
            <Grid item xs = {3}>
              <Box component="Nav" aria-label="mailbox folders" sx={{display: 'flex'}}>
                <Drawer variant="permanent"  sx={{ top: '10%', border: '1px solid rgba(0, 0, 0, 0.12)', }} open>
                  <Toolbar />
                  <Divider />
                  <List>
                    {['Submissions', 'Participated Analyses', 'Used Datasets'].map((text, index) => (
                      <ListItem
                        key={text}
                        disablePadding>
                        <ListItemButton>
                          <ListItemIcon>
                            {index % 2 === 0 ? <ArticleIcon /> : <AssessmentIcon />}
                          </ListItemIcon>
                          <ListItemText primary={text} />
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </List>
                  <Divider />
                  <List>
                    {['All mail'].map((text, index) => (
                      <ListItem key={text} disablePadding>
                        <ListItemButton>
                          <ListItemIcon>
                            {index % 2 === 0 ? <InboxIcon /> : <MailIcon />}
                          </ListItemIcon>
                          <ListItemText primary={text} />
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </List>
                </Drawer>
              </Box>
            </Grid>

            <Grid item xs = {9}>
                <Box
                  component="main"
                  display="flex"
                  justifyContent="center"
                  alignItems="center"
                  sx={{
                    overflow: 'auto',
                    border: '1px solid rgba(0, 0, 0, 0.12)',
                    }}
                >
                  <Toolbar />
                    <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
                      {[0, 1, 2, 3].map((value) => {
                        const labelId = `checkbox-list-label-${value}`;
                        return (
                          <ListItem
                            key={value}
                            disablePadding
                          >
                            <ListItemButton role={undefined} dense>
                              <ListItemText id={labelId} primary={`Submission record ${value + 1}`} />
                              <ListItemIcon>
                                <CommentIcon />
                                <Checkbox
                                  edge="start"
                                  // checked={checked.indexOf(value) !== -1}
                                  tabIndex={-1}
                                  disableRipple
                                  inputProps={{ 'aria-labelledby': labelId }}
                                />
                              </ListItemIcon>
                            </ListItemButton>
                          </ListItem>
                        );
                      })}
                  </List>
                </Box>
            </Grid>
          </Grid>

    </Container>
  );
}
