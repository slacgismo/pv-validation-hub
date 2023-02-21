import { Avatar, Card, CardContent, CardMedia, CircularProgress, Grid, Typography } from "@mui/material";
import { Box } from "@mui/system";
import Cookies from 'universal-cookie';
import BlurryPage from "../GlobalComponents/BlurryPage/blurryPage";
import { UserService } from "../../services/user_service"
import { faker } from "@faker-js/faker";

export default function Profile() {
    const cookies = new Cookies();
    const userInfo = cookies.get("user");

    // TODO: check userInfo existence
    let url = userInfo !== null && userInfo !== undefined ?
                       "/account/?username=" + userInfo["username"] + "&&" + "password=" + userInfo["password"]
                       : "";

    const [isLoading, error, userResponse] = UserService.useGetUserDetails(url);

    console.log("reqponse: ", userResponse)
    // console.log("firstName: ", userResponse.firstName)
    // console.log("firstName: ", userResponse["firstName"])
    return (
        <Box sx={{ marginTop: 5, marginLeft: 4, marginRight: 4 }}>
            {
                userInfo !== undefined ?
                    isLoading ? <CircularProgress /> :
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={3}>
                                <Card
                                    variant="outlined"
                                >
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
                                        '& .MuiTypography-body2': {
                                            color: "gray",
                                            align: "right"
                                        },
                                        '& .MuiTypography-body1': {
                                            align: "right",
                                            justifyContent: 'flex-end'
                                        },
                                        marginBottom: 0.5
                                    }}>
                                        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                                            <Grid container spacing={10}>
                                                <Grid item xs={2}>
                                                    <Typography variant="body1">
                                                        Full Name
                                                    </Typography>
                                                </Grid>
                                                <Grid item xs={8}>
                                                    <Typography variant="body2">
                                                        {userResponse.firstName + " " + userResponse.lastName}
                                                    </Typography>
                                                </Grid>
                                            </Grid>
                                        </Box>
                                        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                                            <Grid container spacing={10}>
                                                <Grid item xs={2}>
                                                    <Typography variant="body1">
                                                        Email
                                                    </Typography>
                                                </Grid>
                                                <Grid item xs={8}>
                                                    <Typography variant="body2">
                                                        {userResponse.email}
                                                    </Typography>
                                                </Grid>
                                            </Grid>
                                        </Box>
                                        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                                            <Grid container spacing={10}>
                                                <Grid item xs={2}>
                                                    <Typography variant="body1">
                                                        Address
                                                    </Typography>
                                                </Grid>
                                                <Grid item xs={8}>
                                                    <Typography variant="body2">
                                                        {faker.address.city() + ", " + faker.address.stateAbbr()}
                                                    </Typography>
                                                </Grid>
                                            </Grid>
                                        </Box>
                                        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                                            <Grid container spacing={10}>
                                                <Grid item xs={2}>
                                                    <Typography variant="body1">
                                                        Username
                                                    </Typography>
                                                </Grid>
                                                <Grid item xs={8}>
                                                    <Typography variant="body2">
                                                        {userResponse.username}
                                                    </Typography>
                                                </Grid>
                                            </Grid>
                                        </Box>
                                        <Box>
                                            <Grid container spacing={10}>
                                                <Grid item xs={2}>
                                                    <Typography variant="body1">
                                                        Github
                                                    </Typography>
                                                </Grid>
                                                <Grid item xs={8}>
                                                    <Typography variant="body2">
                                                        <a href={userResponse.github}>{userResponse.github}</a>
                                                    </Typography>
                                                </Grid>
                                            </Grid>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    :
                    <BlurryPage />
            }
        </Box >
    )
}
