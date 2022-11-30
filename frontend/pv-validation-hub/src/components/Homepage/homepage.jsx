import { Button, Grid, Typography } from "@mui/material";
import { Box } from "@mui/system";
import { useNavigate } from "react-router-dom";
import { HomepageService } from "../../services/homepage_service";
import Footer from "../GlobalComponents/Footer/footer";
export default function Homepage() {

    const navigate = useNavigate();

    const handleJoinToday = () => {
        navigate("/register");
    }
    const handleContactUs = () => {
        window.location = "mailto:aanandak@andrew.cmu.edu";
    }

    const highlight_data = HomepageService.getHighlights();
    const hub_gist = HomepageService.getValidationHubGist();
    return (
        <Box>
            <Grid container spacing={2} alignItems="center">
                <Grid item xs={6} md={5}>
                    <Box sx={{ marginTop: 10, marginLeft: 4 }}>
                        <Typography color={"#007FFF"} variant="h3">
                            PV Validation HUB
                        </Typography>
                        <Typography variant="body1" gutterBottom>
                            The Validation Hub is intended to be a clearinghouse for the transfer of novel algorithms and software from the
                            research community to industry. The primary function of the Hub will be for developers to submit executable code which
                            will run on hosted data sets.
                        </Typography>
                    </Box>
                    <Box sx={{ marginTop: 17, marginLeft: 20 }}>
                        <Button variant="contained" onClick={() => handleJoinToday()}>Join Today</Button>
                    </Box>
                </Grid>
                <Grid item xs={6} md={7}>
                    <Box sx={{
                        margin: 3
                    }}>
                        <Box
                            component="img"
                            sx={{
                                width: "100%",
                            }}
                            alt="PV Validation Hub"
                            src="https://www.sigmapisigma.org/sites/default/files/images/congress/2016/slac-01.jpg"
                        />
                    </Box>
                </Grid>
            </Grid>
            <Grid container spacing={2} sx={{ marginTop: 5 }}>
                <Grid item xs={6}>
                    <Box m={10}>
                        <Typography variant="h4">
                            {highlight_data[0].heading}
                        </Typography>
                        <Typography sx={{ marginTop: 1 }} variant="body1">
                            {highlight_data[0].description}
                        </Typography>
                        <Button sx={{ marginTop: 5 }} variant="outlined">Learn More</Button>
                    </Box>
                </Grid>
                <Grid item xs={6}>
                    <Box m={10}>
                        <Typography variant="h4">
                            {highlight_data[1].heading}
                        </Typography>
                        <Typography sx={{ marginTop: 1 }} variant="body1">
                            {highlight_data[1].description}
                        </Typography>
                        <Button sx={{ marginTop: 5 }} variant="outlined">Learn More</Button>
                    </Box>
                </Grid>
                <Grid item xs={6}>
                    <Box m={10}>
                        <Typography variant="h4">
                            {highlight_data[2].heading}
                        </Typography>
                        <Typography sx={{ marginTop: 1 }} variant="body1">
                            {highlight_data[2].description}
                        </Typography>
                        <Button sx={{ marginTop: 5 }} variant="outlined">Learn More</Button>
                    </Box>
                </Grid>
                <Grid item xs={6}>
                    <Box m={10}>
                        <Typography variant="h4">
                            {highlight_data[3].heading}
                        </Typography>
                        <Typography sx={{ marginTop: 1 }} variant="body1">
                            {highlight_data[3].description}
                        </Typography>
                        <Button sx={{ marginTop: 5 }} variant="outlined">Learn More</Button>
                    </Box>
                </Grid>
            </Grid>
            <Box sx={{
                backgroundColor: "#F5F5F5",
                height: 150,
                maxHeight: 300,
                minHeight: 150,
            }}>
                <Grid container spacing={2}>
                    <Grid item xs={7}>
                        <Typography sx={{ marginLeft: 4, marginTop: 5 }} variant="body1">
                            {hub_gist}
                        </Typography>
                    </Grid>
                    <Grid item xs={5}>
                        <Grid container spacing={2} sx={{ marginTop: 5 }}>
                            <Grid item xs={6}>
                                <Button
                                    variant="contained"
                                    sx={{ marginLeft: 14 }}
                                    onClick={() => handleJoinToday()}>
                                    Join Today
                                </Button>
                            </Grid>
                            <Grid item xs={6}>
                                <Button variant="outlined" sx={{ marginRight: 4 }} onClick={() => handleContactUs()}>Contact Us</Button>
                            </Grid>
                        </Grid>
                    </Grid>
                </Grid>
            </Box>
            <Footer />
        </Box>
    )
}