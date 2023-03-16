import { Avatar, Card, CardContent, CardMedia, CircularProgress, Grid, Typography, TextField, Button, CardActions } from "@mui/material";
import { Box } from "@mui/system";
import Cookies from 'universal-cookie';
import BlurryPage from "../GlobalComponents/BlurryPage/blurryPage";
import { UserService } from "../../services/user_service"
import { faker } from "@faker-js/faker";
import { useState } from "react";

export default function Profile() {
    // todo(jrl): abstract user cookie information
    const cookies = new Cookies();
    const user = cookies.get("user");

    // todo(jrl): check userInfo existence by token instead of plain uuid
    // todo(jrl): abstract user information request and response
    let url = user !== null && user !== undefined ?
                       "/account/" + user.uuid : "";
    
    console.log("url to be sent: ", url);
    const [isLoading, error, userResponse] = UserService.useGetUserDetails(url);
    console.log("user response: ", userResponse);

    // prepare for user profile fields update
    const [githubLink, setUserGithubLink] = useState('');
    const [emailLink, setUserEmailLink] = useState('');

    const handleTextChange = (setState) => (event) => {
        setState(event.target.value);
    };

    const handleProfileUpdateClick = (_) => {
        const updatedProfile = {
            "email": emailLink,
            "githubLink": githubLink,
        };
        const ret = UserService.updateUserProfile(user.uuid, updatedProfile);
        console.log("ret value: ", ret);
        // window.location.reload();
    };

    console.log("response: ", userResponse)
    return (
        <Box sx={{ marginTop: 5, marginLeft: 4, marginRight: 4 }}>
            {
                user !== undefined ?
                    isLoading ? <CircularProgress /> :
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
                                            {userResponse.firstName + " " + userResponse.lastName}
                                        </Typography>
                                        <Typography variant="overline" color={"gray"}>
                                            {faker.helpers.arrayElement(['admin', 'developer', 'viewer'])}
                                        </Typography>
                                        <br />
                                        <Typography variant="overline" color={"gray"}>
                                            {faker.address.city() + ", " + faker.address.stateAbbr()}
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Grid>
                            <Grid item xs={12} md={9}>
                                <Card variant="outlined">
                                    <CardContent sx={{
                                        '& .MuiTypography-root': {
                                            marginTop: 2,
                                            marginBottom: 2
                                        },
                                        '& .MuiTypography-body1': {
                                            align: 'center',
                                            justifyContent: 'flex-end'
                                        },
                                        marginBottom: 0.5,
                                        marginTop: 0.5
                                    }}>
                                        <InfoRow title="Full Name"
                                                 defaultValue={userResponse.firstName + " " + userResponse.lastName}
                                                 disabled={true}
                                        />
                                        <InfoRow title="Email"
                                                 defaultValue={userResponse.email}
                                                 disabled={false}
                                                 onChange={handleTextChange(setUserEmailLink)}
                                        />
                                        <InfoRow title="Address"
                                                 defaultValue={faker.address.city() + ", " + faker.address.stateAbbr()}
                                                 disabled={false}
                                        />
                                        <InfoRow title="Username"
                                                 defaultValue={userResponse.username}
                                                 disabled={true}
                                        />
                                        <InfoRow title="Github"
                                                 defaultValue={userResponse.githubLink}
                                                 disabled={false}
                                                 onChange={handleTextChange(setUserGithubLink)}
                                        />
                                    </CardContent>
                                    <CardActions>
                                        <Button variant="contained" onClick={handleProfileUpdateClick}>
                                            <Typography textTransform="none">Update profile</Typography>
                                        </Button>
                                    </CardActions>
                                </Card>
                            </Grid>
                        </Grid>
                    :
                    <BlurryPage />
            }
        </Box >
    )
}

function InfoRow({ title, defaultValue, disabled, onChange }) {
    return (
        <Box>
            <Grid container spacing={5}>
                <Grid item xs={2} alignItems="center" justifyContent="center">
                    <Typography variant="body1">
                        {title}
                    </Typography>
                </Grid>
                <Grid item xs={8}>
                    <TextField fullWidth
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
    )
}
