import { Box, Button, Grid, Tab, Tabs, Typography } from "@mui/material";
import { Container } from "@mui/system";
import { useRef, useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { DashboardService } from "../../services/dashboard_service";
import TabPanel from "../GlobalComponents/TabPanel/TabPanel";
import Data from "./Data/Data";
import Leaderboard from "./Leaderboard/Leaderboard";
import Overview from "./Overview/Overview";

export default function Analysis() {

    const [value, setValue] = useState(0);

    const [searchParams,] = useSearchParams();

    const analysisIdRef = useRef(null);

    const [showButton, setShowButton] = useState(false);

    const [card, setCard] = useState({});

    const setValues = (index) => {
        return {
            id: `tab-${index}`,
            'aria-controls': `tabpanel-${index}`,
        };
    }

    useEffect(() => {
        if (analysisIdRef.current === null || searchParams.get("analysis_id") !== analysisIdRef.current) {
            setCard(DashboardService.getCardDetails(searchParams.get("analysis_id")));
            analysisIdRef.current = searchParams.get("analysis_id");
        }
    }, [searchParams]);

    const handleChange = (event, newValue) => {
        newValue === 2 ? setShowButton(true) : setShowButton(false);
        setValue(newValue);
    };
    return (
        <Container>
            <Box sx={{ flexGrow: 1, marginTop: 3, backgroundImage: `url(${card.image})` }}>
                <Box sx={{ flexGrow: 1, marginTop: 1 }}>
                    <Typography variant="h2" gutterBottom>
                        {card.title}
                    </Typography>
                </Box>
                <Box sx={{ flexGrow: 1, marginTop: 0.5 }}>
                    <Typography variant="body1" gutterBottom>
                        {card.description}
                    </Typography>
                </Box>
            </Box>
            <Box sx={{ width: '100%' }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Grid container spacing={2}>
                        <Grid item xs={6} md={10}>
                            <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
                                <Tab label="Overview" {...setValues(0)} />
                                <Tab label="Data" {...setValues(1)} />
                                <Tab label="Leaderboard" {...setValues(2)} />
                                <Tab label="Rules" {...setValues(3)} />
                                <Tab label="Submission" {...setValues(4)} />
                                <Tab label="Discussion" {...setValues(5)} />
                            </Tabs>
                        </Grid>
                        <Grid item xs={6} md={2}>
                            {
                                showButton ? <Button align="right" variant="contained" sx={{ backgroundColor: "black", width: "100%", height: "75%", fontSize: "small" }}>
                                    Upload Algorithm
                                </Button>
                                    : null
                            }
                        </Grid>
                    </Grid>
                </Box>
                <TabPanel value={value} index={0}>
                    <Overview
                        analysis_id={searchParams.get("analysis_id")}
                    />
                </TabPanel>
                <TabPanel value={value} index={1}>
                    <Data
                        analysis_id={searchParams.get("analysis_id")}
                    />
                </TabPanel>
                <TabPanel value={value} index={2} >
                    <Leaderboard
                        analysis_id={searchParams.get("analysis_id")}
                    />
                </TabPanel>
                <TabPanel value={value} index={3}>
                    <Typography>Rules</Typography>
                </TabPanel>
                <TabPanel value={value} index={4}>
                    <Typography>Submission</Typography>
                </TabPanel>
                <TabPanel value={value} index={5}>
                    <Typography>Discussion</Typography>
                </TabPanel>
            </Box>
        </Container>
    )
}