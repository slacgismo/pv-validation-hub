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

    const handleNavigate = (url) => {
        const a = document.createElement('a')
        a.target = '_blank'
        a.href = url
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
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
                            Research
                        </Typography>
                        <Typography sx={{ marginTop: 1 }} variant="body1">
                            SLAC research explores nature on all scales, from the unseen realms of fundamental
                            particles and unbelievably fast processes to astrophysical phenomena of cosmic dimensions.
                            Our research opens new windows to the natural world and builds a brighter future through
                            scientific discovery.
                        </Typography>
                        <Button
                            sx={{ marginTop: 5 }}
                            variant="outlined"
                            onClick={() => handleNavigate("https://www6.slac.stanford.edu/research")}
                        >
                            Learn More
                        </Button>
                    </Box>
                </Grid>
                <Grid item xs={6}>
                    <Box m={10}>
                        <Typography variant="h4">
                            Our Story
                        </Typography>
                        <Typography sx={{ marginTop: 1 }} variant="body1">
                            SLAC began in 1962 with construction of a 2-mile-long electron accelerator that
                            would take particle physics to new heights. Today we are known for conducting
                            a broad range of research, leading large-scale science projects,
                            and welcoming scientists around the world
                        </Typography>
                        <Button
                            sx={{ marginTop: 5 }}
                            variant="outlined"
                            onClick={() => handleNavigate("https://www6.slac.stanford.edu/about/our-story")}>
                            Learn More
                        </Button>
                    </Box>
                </Grid>
                <Grid item xs={6}>
                    <Box m={10}>
                        <Typography variant="h4">
                            News & Events
                        </Typography>
                        <Typography sx={{ marginTop: 1 }} variant="body1">
                            Get the latest news about the lab, our science and discoveries. Explore SLAC events and learn how to participate.
                            Stay up to date on our latest scientific advances and research tools.
                        </Typography>
                        <Button
                            sx={{ marginTop: 5 }}
                            variant="outlined"
                            onClick={() => handleNavigate("https://www6.slac.stanford.edu/news-and-events/news-center")}>
                            Learn More
                        </Button>
                    </Box>
                </Grid>
                <Grid item xs={6}>
                    <Box m={10}>
                        <Typography variant="h4">
                            Resources
                        </Typography>
                        <Typography sx={{ marginTop: 1 }} variant="body1">
                            Explore our research through graphics, videos and photographs selected by our staff.
                            Visit our public Flickr albums and YouTube videos for more.
                        </Typography>
                        <Button
                            sx={{ marginTop: 5 }}
                            variant="outlined"
                            onClick={() => handleNavigate("https://www6.slac.stanford.edu/about/resources/images-and-videos")}>
                            Learn More
                        </Button>
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
                        <Typography sx={{ marginLeft: 4 }} variant="body1">
                            Our goal is to develop an open-source toolkit written in Python, which automates
                            the analysis of performance and reliability for fleets of photovoltaic (PV) systems.
                            All our algorithms use unlabled PV system production data, that is, measurements of
                            real power production over time without reference meteorological data or system configuration
                            information, which allows for the algorithms to work with the minimal possible data requirements.
                        </Typography>
                    </Grid>
                    <Grid item xs={5}>
                        <Grid container spacing={2} sx={{ marginTop: 1 }}>
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