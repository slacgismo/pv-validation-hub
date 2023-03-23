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
import MailIcon from '@mui/icons-material/Mail';
import ArticleIcon from '@mui/icons-material/Article';
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
          {/* <Toolbar> */}
            {/* <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton> */}
            {/* <Typography variant="h6" noWrap component="div">
              Responsive drawer
            </Typography>
          </Toolbar> */}

          {/* <Box
            component="nav"
            // sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
            aria-label="mailbox folders"
          > */}
            {/* The implementation can be swapped with js to avoid SEO duplication of links. */}
            {/* <Drawer
              // container={container}
              variant="temporary"
              open={false}
              onClose={handleDrawerToggle}
              ModalProps={{
                keepMounted: true, // Better open performance on mobile.
              }}
              sx={{
                display: { xs: 'block', sm: 'none' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
            >
              {drawer}
            </Drawer> */}

            {/* <Drawer
              variant="permanent"
              sx={{
                flexShrink: 0,
                display: { xs: 'none', sm: 'block' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
              open
            >
              {drawer}
            </Drawer>
          </Box> */}
          <Grid container alignItems="center" spacing={2}>
            <Grid item xs = {3}>
              <Box component="Nav" aria-label="mailbox folders" sx={{display: 'flex'}}>
                <Drawer variant="permanent"  sx={{ top: '10%', border: '1px solid rgba(0, 0, 0, 0.12)', }} open>
                  <Toolbar />
                  <Divider />
                  <List>
                    {['Submissions', 'Participated Analyses', 'Used Datasets'].map((text, index) => (
                      <ListItem key={text} disablePadding>
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
                  sx={{
                    overflow: 'auto',
                    border: '1px solid rgba(0, 0, 0, 0.12)',
                    }}
                >
                  <Toolbar />
                  <Typography paragraph>
                    Lorem ipsum dolor sit amet. asdfasfd
                  </Typography>
                  <Typography paragraph>
                    Consequat mauris nunc congue nisi vitae suscipit.
                  </Typography>
                  <Typography paragraph>
                    Consequat mauris nunc congue nisi vitae suscipit.
                  </Typography>
                  <Typography paragraph>
                    Consequat mauris nunc congue nisi vitae suscipit.
                  </Typography>
                  <Typography paragraph>
                    Consequat mauris nunc congue nisi vitae suscipit.
                  </Typography>
                  <Typography paragraph>
                    Consequat mauris nunc congue nisi vitae suscipit.
                  </Typography>
                  <Typography paragraph>
                    Consequat mauris nunc congue nisi vitae suscipit.
                  </Typography>
                </Box>
            </Grid>
          </Grid>

    </Container>
  );
}
