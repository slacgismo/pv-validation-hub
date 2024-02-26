import {
  Avatar, Card, CardContent, CardMedia, CircularProgress, Grid, Typography, TextField, Button, CardActions,
} from '@mui/material';
import { Box } from '@mui/system';
import { styled } from '@mui/material/styles';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogAction from '@mui/material/DialogActions';
import Cookies from 'universal-cookie';
import { faker } from '@faker-js/faker';
import React, { useState } from 'react';
import BlurryPage from '../GlobalComponents/BlurryPage/blurryPage.jsx';
import UserService from '../../services/user_service.js';

const UpdateDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialogContent-root': {
    padding: theme.spacing(2),
  },
  '& .MuiDialogActions-root': {
    padding: theme.spacing(1),
  },
}));

// Dialog that shows whether user profile successfully updated or not.
function ProfileUpdateDialog({ open, onClose }) {
  return (
    <UpdateDialog open={open}>
      <DialogContent dividers>
        <Typography gutterBottom>
          Update Succeed!
        </Typography>
      </DialogContent>
      <DialogAction>
        <Button autoFocus onClick={onClose}>
          <Typography variant="body2">
            Done
          </Typography>
        </Button>
      </DialogAction>
    </UpdateDialog>
  );
}

const ProfileCardContent = styled(CardContent)(({ theme }) => ({
  '& .MuiTypography-root': {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  '& .MuiTypography-body1': {
    align: 'center',
    justifyContent: 'flex-end',
  },
  marginBottom: 0.5,
  marginTop: 0.5,
}));

export default function Profile() {
  // todo(jrl): abstract user cookie and token information to a separate service
  const cookies = new Cookies();
  const user = cookies.get('user');
  const url = user !== null && user !== undefined ? '/account' : '';
  const [isLoading, error, userResponse] = UserService.useGetUserDetails(url, user.token);

  // prepare for user profile fields update
  const [githubLink, setUserGithubLink] = useState('');
  const [emailLink, setUserEmailLink] = useState('');
  const [updateDialogOpen, setUpdateDialogOpen] = useState(false);

  const handleTextChange = (setState) => (event) => {
    setState(event.target.value);
  };

  const handleProfileUpdateClick = (_) => {
    const updatedProfile = {
      email: emailLink === '' ? userResponse.email : emailLink,
      githubLink: githubLink === '' ? userResponse.githubLink : githubLink,
    };
    // todo: check return value
    const ret = UserService.updateUserProfile(user.token, updatedProfile);
    setUpdateDialogOpen(true);
  };

  console.log('response: ', userResponse);
  return (
    <Box sx={{ marginTop: 5, marginLeft: 4, marginRight: 4 }}>
      {
                user !== undefined
                  ? isLoading ? <CircularProgress />
                    : (
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={3}>
                          <Card variant="outlined">
                            <CardMedia align="center" sx={{ marginTop: 1, marginBottom: 2 }}>
                              <Avatar
                                sx={{ height: 170, width: 174 }}
                                alt={userResponse.firstName}
                                src={faker.image.avatar()}
                              />
                            </CardMedia>
                            <CardContent align="center">
                              <Typography variant="h5">
                                {`${userResponse.firstName} ${userResponse.lastName}`}
                              </Typography>
                              <Typography variant="overline" color="gray">
                                {faker.helpers.arrayElement(['admin', 'developer', 'viewer'])}
                              </Typography>
                              <br />
                              <Typography variant="overline" color="gray">
                                {`${faker.address.city()}, ${faker.address.stateAbbr()}`}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                        <Grid item xs={12} md={9}>
                          <Card variant="outlined">
                            <ProfileCardContent>
                              <InfoRow
                                title="Full Name"
                                defaultValue={`${userResponse.firstName} ${userResponse.lastName}`}
                                disabled
                              />
                              <InfoRow
                                title="Email"
                                defaultValue={userResponse.email}
                                disabled={false}
                                onChange={handleTextChange(setUserEmailLink)}
                              />
                              <InfoRow
                                title="Address"
                                defaultValue={`${faker.address.city()}, ${faker.address.stateAbbr()}`}
                                disabled={false}
                              />
                              <InfoRow
                                title="Username"
                                defaultValue={userResponse.username}
                                disabled
                              />
                              <InfoRow
                                title="Github"
                                defaultValue={userResponse.githubLink}
                                disabled={false}
                                onChange={handleTextChange(setUserGithubLink)}
                              />
                            </ProfileCardContent>
                            <CardActions>
                              <Button variant="contained" onClick={handleProfileUpdateClick}>
                                <Typography textTransform="none">Update profile</Typography>
                              </Button>
                            </CardActions>
                          </Card>
                        </Grid>
                        <ProfileUpdateDialog
                          open={updateDialogOpen}
                          onClose={() => { setUpdateDialogOpen(false); }}
                        />
                      </Grid>
                    )
                  : <BlurryPage />
            }
    </Box>
  );
}

// InfoRow represents a single row of specific user profile information with a title.
// It can be specified to whether editable or not.
function InfoRow({
  title, defaultValue, disabled, onChange,
}) {
  return (
    <Box>
      <Grid container spacing={5}>
        <Grid item xs={2} alignItems="center" justifyContent="center">
          <Typography variant="body1">
            {title}
          </Typography>
        </Grid>
        <Grid item xs={8}>
          <TextField
            fullWidth
            hiddenLabel
            size="small"
            defaultValue={defaultValue}
            disabled={disabled}
            variant="filled"
            onChange={onChange}
          />
        </Grid>
      </Grid>
    </Box>
  );
}
