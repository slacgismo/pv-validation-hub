import { Box, Grid, Typography, Button } from "@mui/material";
import { Container } from "@mui/system";
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import CardMedia from '@mui/material/CardMedia';
import CardContent from '@mui/material/CardContent';
import Avatar from '@mui/material/Avatar';
import { DashboardService } from "../../services/dashboard_service";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { useEffect } from "react";
import CircularProgress from '@mui/material/CircularProgress';
import { faker } from "@faker-js/faker";

export default function Dashboard() {
    const navigate = useNavigate();
    const [analysisId, setAnalysisId] = useState();

    useEffect(() => {
        if (analysisId != null) {
            navigate("/analysis/" + analysisId);
        }
    }, [analysisId, navigate]);

    const handleCardClick = (card_id, card_title) => {
        setAnalysisId(card_id);
    };

    const [isLoading, isError, cardDetails] = DashboardService.useGetAnalysisSet("/analysis/home");

    return (
        <Container>
            <Box sx={{ flexGrow: 1, marginTop: 3 }}>
                <Typography variant="h2" gutterBottom>
                    Analytical Tasks
                </Typography>
            </Box>

            <Grid container spacing={2}>
                <Grid item>
                    <Box sx={{ flexGrow: 1, marginTop: 3 }}>
                        <Typography variant="body1" gutterBottom>
                            The Validation Hub is intended to be a clearinghouse for the transfer of novel algorithms and software from the research community to industry. The primary function of the Hub will be for developers to submit executable code which will run on hosted data sets. Developers will receive private reports on the accuracy and performance (e.g., run-time) of the submitted algorithms, and public high level summaries will be hosted. These summaries will indicate the organization who submitted the algorithm (e.g., links to GitHub pages, documentation websites, etc.), high-level accuracy metrics, and standardized performance metrics. These results will be stored in a publicly available database, accessible through the Hub, with the ability for users to sort and filter the results. In short, the Hub will be presented to public users as a collection of interactive leaderboards, organized around specific analysis tasks pertinent to the PV data science community. These tasks include things such as the estimation of various PV loss factors and the detection of various operational issues, to be defined in this document.
                        </Typography>
                    </Box>
                </Grid>
            </Grid>

            <Box sx={{ flexGrow: 1, marginTop: 3, marginBottom: 10 }}>
                {
                    isLoading ?
                        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                            <CircularProgress />
                        </Box>
                        :
                        <Grid container spacing={{ xs: 2, md: 3 }} columns={{ xs: 4, sm: 8, md: 12 }} alignItems="stretch">
                            {
                                cardDetails.map((card, index) => (
                                    <CustomizedCard index={index} card={card} onClick={handleCardClick} />
                                ))
                            }
                        </Grid>
                }
            </Box>
        </Container>
    )
}

function CustomizedCard({ index, card, onClick }) {
    return (
        <Grid item xs={2} sm={4} md={4} key={index}>
            <Card sx={{ maxWidth: 345, height: 380 }} key={card.analysis_id} onClick={() => onClick(card.analysis_id, card.analysis_name)}>
                <CardHeader
                    avatar={
                        <Avatar
                            src={faker.image.avatar()}
                            aria-label="Analysis"
                        />
                    }
                    sx={{ height: 61 }}
                    title={card.analysis_name}
                />
                <CardMedia
                    component="img"
                    height="194"
                    src={faker.image.abstract(640,480,true)}
                    alt={card.analysis_name}
                />
                <CardContent>
                    <Typography variant="body2" color="text.secondary">
                        {card.short_description != undefined && card.short_description.length > 100 ? card.short_description.slice(0, 100) + "....." : card.short_description}
                    </Typography>
                </CardContent>
            </Card>
        </Grid>
    )
}
