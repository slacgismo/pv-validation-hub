import { Avatar, Card, CardContent, CardMedia, Grid, Typography } from "@mui/material";
import { Box } from "@mui/system";
import Cookies from 'universal-cookie';
import { DashboardService } from "../../services/dashboard_service";
export default function Profile() {
    const cookies = new Cookies();
    let user = cookies.get("user")
    user = user === undefined || user === null ? "joemama" : user;
    const userDetails = DashboardService.getUserProfile(user);
    return (
        <Box sx={{ marginTop: 5, marginLeft: 4, marginRight: 4}}>
            <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                    <Card
                        variant="outlined"
                    >
                        <CardMedia align="center" sx={{ marginTop: 1, marginBottom: 2 }}>
                            <Avatar
                                sx={{ height: 170, width: 174 }}
                                alt={userDetails.firstName}
                                src={userDetails.avatar}
                            />

                        </CardMedia>
                        <CardContent align="center">
                            <Typography variant="h5">
                                {userDetails.firstName + " " + userDetails.lastName}
                            </Typography>
                            <Typography variant="overline" color={"gray"}>
                                {userDetails.subscriptionTier}
                            </Typography>
                            <br />
                            <Typography variant="overline" color={"gray"}>
                                {userDetails.location}
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
                                        {userDetails.firstName + " " + userDetails.lastName}
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
                                        {userDetails.email}
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
                                        {userDetails.location}
                                    </Typography>
                                </Grid>
                            </Grid>
                        </Box>
                        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                            <Grid container spacing={10}>
                                <Grid item xs={2}>
                                    <Typography variant="body1">
                                        User ID
                                    </Typography>
                                </Grid>
                                <Grid item xs={8}>
                                    <Typography variant="body2">
                                        {userDetails._id}
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
                                        <a href={userDetails.github}>{userDetails.github}</a>
                                    </Typography>
                                </Grid>
                            </Grid>
                        </Box>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
        </Box >
    )
}