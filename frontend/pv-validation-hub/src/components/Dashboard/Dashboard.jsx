import { Box, Grid, Typography } from "@mui/material";
import { Container } from "@mui/system";
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import CardMedia from '@mui/material/CardMedia';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Avatar from '@mui/material/Avatar';
import IconButton from '@mui/material/IconButton';
import FavoriteIcon from '@mui/icons-material/Favorite';
import ShareIcon from '@mui/icons-material/Share';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { DashboardService } from "../../services/dashboard_service";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { useEffect } from "react";

export default function Dashboard() {

    const navigate = useNavigate();

    const [analysisId, setAnalysisId] = useState();

    useEffect(() => {
        if (analysisId != null) {
          navigate("/analysis?analysis_id=" + analysisId);
        }
      }, [analysisId, navigate]);

    const handleCardClick = (card_id, card_title) => {
        setAnalysisId(card_id);
      };
    const cardDetails = DashboardService.getAnalysisSet();
    const render_card = (card, index) => {
        return (
            <Grid item xs={2} sm={4} md={4} key={index}>
                <Card sx={{ maxWidth: 345 }} key={card.id} onClick={() => handleCardClick(card.id, card.title)}>
                    <CardHeader
                        avatar={
                            <Avatar sx={{ backgroundImage: card.user_avatar }} aria-label="Analysis">
                                {card.user_initial}
                            </Avatar>
                        }
                        action={
                            <IconButton aria-label="settings">
                                <MoreVertIcon />
                            </IconButton>
                        }
                        title={card.title}
                        subheader={card.sub_title}
                    />
                    <CardMedia
                        component="img"
                        height="194"
                        image={card.image}
                        alt={card.title}
                    />
                    <CardContent>
                        <Typography variant="body2" color="text.secondary">
                            {card.description}
                        </Typography>
                    </CardContent>
                    <CardActions disableSpacing>
                        <IconButton aria-label="add to favorites">
                            <FavoriteIcon />
                        </IconButton>
                        <IconButton aria-label="share">
                            <ShareIcon />
                        </IconButton>
                    </CardActions>
                </Card>
            </Grid>
        )
    }
    return (
        <Container
        >
            <Box sx={{ flexGrow: 1, marginTop: 3 }}>
                <Typography variant="h2" gutterBottom>
                    Analysis Sets
                </Typography>
            </Box>
            <Box sx={{ flexGrow: 1, marginTop: 3 }}>
                <Typography variant="body1" gutterBottom>
                    The Validation Hub is intended to be a clearinghouse for the transfer of novel algorithms and software from the research community to industry. The primary function of the Hub will be for developers to submit executable code which will run on hosted data sets. Developers will receive private reports on the accuracy and performance (e.g., run-time) of the submitted algorithms, and public high level summaries will be hosted. These summaries will indicate the organization who submitted the algorithm (e.g., links to GitHub pages, documentation websites, etc.), high-level accuracy metrics, and standardized performance metrics. These results will be stored in a publicly available database, accessible through the Hub, with the ability for users to sort and filter the results. In short, the Hub will be presented to public users as a collection of interactive leaderboards, organized around specific analysis tasks pertinent to the PV data science community. These tasks include things such as the estimation of various PV loss factors and the detection of various operational issues, to be defined in this document.
                </Typography>
            </Box>
            <Box sx={{ flexGrow: 1, marginTop: 3 }}>
                <Grid container spacing={{ xs: 2, md: 3 }} columns={{ xs: 4, sm: 8, md: 12 }}>
                    {cardDetails.map(render_card)}
                </Grid>
            </Box>
        </Container >
    )
}