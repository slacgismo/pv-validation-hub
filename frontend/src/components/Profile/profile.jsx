import { Avatar, Card, CardContent, CardMedia, CircularProgress, Grid, Typography, TextField, Button, CardActions } from "@mui/material";
import { Box } from "@mui/system";
import Cookies from 'universal-cookie';
import BlurryPage from "../GlobalComponents/BlurryPage/blurryPage";
import { UserService } from "../../services/user_service"
import { faker } from "@faker-js/faker";

export default function Profile() {
    const cookies = new Cookies();
    const userInfo = cookies.get("user");

    // TODO: check userInfo existence by token instead of plain text password
    let url = userInfo !== null && userInfo !== undefined ?
                       "/account/?username=" + userInfo["username"] + "&&" + "password=" + userInfo["password"]
                       : "";

    const [isLoading, error, userResponse] = UserService.useGetUserDetails(url);

    console.log("reqponse: ", userResponse)
    return (
        <Box sx={{ marginTop: 5, marginLeft: 4, marginRight: 4 }}>
            {
                userInfo !== undefined ?
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
                                                 disabled={false}
                                        />
                                        <InfoRow title="Email"
                                                 defaultValue={userResponse.email}
                                                 disabled={false}
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
                                                 defaultValue={""}
                                                 disabled={false}
                                        />
                                    </CardContent>
                                    <CardActions>
                                        <Button variant="contained">
                                            <Typography textTransform="none">Update Profile</Typography>
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

function InfoRow({ title, defaultValue, disabled }) {
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
                    />
                </Grid>
            </Grid>
        </Box> 
    )
}
