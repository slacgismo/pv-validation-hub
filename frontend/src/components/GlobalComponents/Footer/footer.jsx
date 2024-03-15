import React from 'react';
import { Grid, Link, Typography } from '@mui/material';
import { Box } from '@mui/system';

import {
  FacebookIcon,
  FacebookShareButton,
  LinkedinIcon,
  LinkedinShareButton,
  TwitterIcon,
  TwitterShareButton,
  WhatsappIcon,
  WhatsappShareButton,
} from 'react-share';

function Footer() {
  const shareUrl = 'https://pv-validation-hub.org';
  const title = 'PV Validation Hub';
  return (
    <Box sx={{
      height: 150,
      minHeight: 100,
      maxHeight: 200,
    }}
    >
      <Grid container spacing={2} alignItems="center" justify="center">
        <Grid item xs={12}>
          <Box display="flex" justifyContent="center" alignItems="center" sx={{ borderBottom: 1, borderColor: 'divider', marginTop: 4 }}>
            <Grid item xs={2} />
            <Grid container spacing={2} xs={8}>
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
                <Box alignItems="center" justifyContent="center">
                  <Typography
                    display="block"
                    align="center"
                    variant="h6"
                    noWrap
                    href="/"
                    sx={{
                      mr: 2,
                      fontFamily: 'sans-serif',
                      fontWeight: 700,
                      color: 'black',
                      textDecoration: 'none',
                    }}
                  >
                    PVHub
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
            <Grid item xs={2} />
          </Box>
        </Grid>
        <Grid item xs={12}>
          <Box display="flex" justifyContent="center" alignItems="center">
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
  );
}

export default Footer;
