import { Grid, Link, Typography } from "@mui/material";
import { Box } from "@mui/system";
import DiamondIcon from '@mui/icons-material/Diamond';

import {
    FacebookIcon,
    FacebookShareButton,
    LinkedinIcon,
    LinkedinShareButton,
    TwitterIcon,
    TwitterShareButton,
    WhatsappIcon,
    WhatsappShareButton,
} from "react-share";
const Footer = () => {
    const shareUrl = "http://localhost:3000";
    const title = "PV Validation Hub"
    return (
        <Box sx={{
            height: 200,
            minHeight: 200,
            maxHeight: 300,
        }}>
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <Box sx={{ borderBottom: 1, borderColor: 'divider', marginTop: 4 }}>
                        <Box sx={{ marginLeft: 9 }}>
                            <Grid container spacing={2}>
                                <Grid item xs={2}>
                                    <Link href="https://www6.slac.stanford.edu/news-and-events/connect-with-us" underline="hover" color="inherit">
                                        Community
                                    </Link>
                                </Grid>
                                <Grid item xs={2}>
                                    <Link href="https://www6.slac.stanford.edu/about" underline="hover" color="inherit">
                                        Company
                                    </Link>

                                </Grid>
                                <Grid item xs={4}>
                                    <Box sx={{ justifyContent: 'center', marginLeft: 17 }}>
                                        <DiamondIcon sx={{ display: { xs: 'none', md: 'flex', color: "black", marginLeft: 15 }, mr: 1 }} />
                                        <Typography
                                            variant="h6"
                                            noWrap
                                            component="a"
                                            href="/"
                                            sx={{
                                                mr: 2,
                                                display: { xs: 'none', md: 'flex' },
                                                fontFamily: 'monospace',
                                                fontWeight: 700,
                                                letterSpacing: '.3rem',
                                                color: 'black',
                                                textDecoration: 'none',
                                            }}
                                        >
                                            LOGO
                                        </Typography>
                                    </Box>
                                </Grid>
                                <Grid item xs={2}>
                                    <Link href="https://www6.slac.stanford.edu/news-and-events/news-center" underline="hover" color="inherit">
                                        Blog
                                    </Link>
                                </Grid>
                                <Grid item xs={2}>
                                    <Link href="https://www6.slac.stanford.edu/about/resources" underline="hover" color="inherit">
                                        Resources
                                    </Link>
                                </Grid>
                            </Grid>
                        </Box>
                    </Box>
                </Grid>
                <Grid item xs={12}>
                    <Box sx={{ marginTop: 1, marginLeft: 72 }}>
                        <FacebookShareButton
                            url={shareUrl}
                            quote={title}
                        >
                            <FacebookIcon size={32} round />
                        </FacebookShareButton>
                        <TwitterShareButton
                            url={shareUrl}
                            title={title}
                        >
                            <TwitterIcon size={32} round />
                        </TwitterShareButton>
                        <WhatsappShareButton
                            url={shareUrl}
                            title={title}
                            separator=":: "
                        >
                            <WhatsappIcon size={32} round />
                        </WhatsappShareButton>
                        <LinkedinShareButton url={shareUrl}>
                            <LinkedinIcon size={32} round />
                        </LinkedinShareButton>
                    </Box>
                </Grid>
            </Grid>
        </Box>
    )
}

export default Footer;