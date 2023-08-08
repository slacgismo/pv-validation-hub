import { Box, Grid, Button, Tab, Tabs, Typography, CircularProgress } from "@mui/material";
import { Container } from "@mui/system";
import { useState, useEffect } from "react";
import TabPanel from "../GlobalComponents/TabPanel/TabPanel";
import Data from "./Data/Data";
import { CommentProvider } from "./Discussion/CommentContext";
import Discussion from "./Discussion/Discussion";
import Leaderboard from "./Leaderboard/Leaderboard";
import Overview from "./Overview/Overview";
import Rules from "./Rules/Rules";
import Submission from "./Submissions/Submission";
import CancelIcon from '@mui/icons-material/Cancel';
import ReactModal from "react-modal";
import Cookies from 'universal-cookie';
import { FileUploader } from "react-drag-drop-files";
import BlurryPage from "../GlobalComponents/BlurryPage/blurryPage";
import { AnalysisService } from "../../services/analysis_service";
import { faker } from "@faker-js/faker";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";

export default function Analysis() {
    const navigate = useNavigate();
    const cookies = new Cookies();
    let user = cookies.get("user");

    const [value, setValue] = useState(0);

    const [isOpen, setIsOpen] = useState(false);

    const [isLoading, error, card, analysis_id] = AnalysisService.useGetCardDetails();

    // Set the md descriptions

    const [datasetDescription, setDatasetDescription] = useState("");
    const [longDescription, setLongDescription] = useState("");
    const [shortDescription, setShortDescription] = useState("");
    const [rulesetDescription, setRulesetDescription] = useState("");

    useEffect(() => {
        console.log("analysis", analysis_id, typeof analysis_id)
        if (analysis_id !== undefined && analysis_id !== null && analysis_id > 0) {
            fetch(process.env.PUBLIC_URL + `/assets/${analysis_id}/dataset.md`)
            .then(res => res.text())
            .then(text => setDatasetDescription(text))
            .catch(err => console.log(err));
         
            fetch(process.env.PUBLIC_URL + `/assets/${analysis_id}/longdesc.md`)
            .then(res => res.text())
            .then(text => setLongDescription(text))
            .catch(err => console.log(err));
         
            fetch(process.env.PUBLIC_URL + `/assets/${analysis_id}/shortdesc.md`)
            .then(res => res.text())
            .then(text => setShortDescription(text))
            .catch(err => console.log(err));
         
            fetch(process.env.PUBLIC_URL + `/assets/${analysis_id}/ruleset.md`)
            .then(res => res.text())
            .then(text => setRulesetDescription(text))
            .catch(err => console.log(err));
         
        }
    }, [analysis_id]);

    const closeModal = () => {
        setIsOpen(false);
    }

    const openModal = () => {
        setIsOpen(true);
    }

    const fileTypes = ["ZIP", "IPYNB"];

    const [file, setFile] = useState(null);

    const uploadFile = (file) => {
        setFile(file);
    };

    const handleUpload = () => {
        let response = AnalysisService.uploadAlgorithm(analysis_id, user.token, file);
        closeModal();
    }

    const handleChange = (event, newValue) => {
        setValue(newValue);
    };

    return (
        isLoading !== false ? <CircularProgress /> :
            <Container id="analysis">
                <Box sx={{
                    flexGrow: 1,
                    marginTop: 3,
                    height: 200,
                    backgroundImage: `url(${faker.image.abstract(1200, 300)})`
                }}>
                    <Box sx={{ flexGrow: 1, marginTop: 4, marginLeft: 2 }}>
                        <Typography color={"white"} variant="h4" gutterBottom>
                            {card.analysis_name}
                        </Typography>
                    </Box>
                    <Box sx={{ flexGrow: 1, marginTop: 2, marginLeft: 2 }}>
                        <Typography color={"white"} variant="body2" gutterBottom>
                            <ReactMarkdown children={shortDescription} />
                        </Typography>
                    </Box>
                </Box>

                <Box sx={{ width: '100%' }}>
                    <Box sx={{ borderBottom: 1, borderColor: 'divider', marginRight: 2 }}>
                        <Grid container spacing={2}>
                            <Grid item xs={6} md={10}>
                                <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
                                    <Tab label="Overview" />
                                    <Tab label="Data" />
                                    <Tab label="Leaderboard" />
                                    <Tab label="Rules" />
                                    <Tab label="Discussion" />
                                </Tabs>
                            </Grid>

                            <Grid item xs={6} md={2}>
                                {
                                    <Button
                                        align="right"
                                        variant="contained"
                                        onClick={() => {
                                            if (user === undefined || user === null) {
                                                navigate("/login");
                                            }
                                            openModal();
                                        }}
                                        sx={{
                                            backgroundColor: "black",
                                            width: "100%",
                                            height: "70%",
                                            marginTop: 1
                                        }}>
                                        <Typography textTransform="none">
                                            Upload Algorithm
                                        </Typography>
                                    </Button>
                                }
                            </Grid>
                        </Grid>
                    </Box>

                    <TabPanel value={value} index={0}>
                        <Overview
                            title={"Overview of " + card.analysis_name}
                            description={longDescription}
                        />
                    </TabPanel>

                    <TabPanel value={value} index={1}>
                        {
                            user === undefined || user == null ?
                                <BlurryPage />
                                :
                                <Data
                                    data_description={datasetDescription}
                                />
                        }
                    </TabPanel>

                    <TabPanel value={value} index={2} >
                        <Leaderboard
                            analysis_id={analysis_id}
                        />
                    </TabPanel>

                    <TabPanel value={value} index={3}>
                        <Rules
                            title={card.analysis_name}
                            description={rulesetDescription}
                        />
                    </TabPanel>

                    <TabPanel value={value} index={4}>
                        {
                            user === undefined || user == null ?
                                <BlurryPage />
                                :
                                <Submission
                                    analysis_id={analysis_id}
                                    user_id={user != null || user != undefined ? user.id : user}
                                />
                        }
                    </TabPanel>

                    <TabPanel value={value} index={5}>
                        {user === undefined || user == null ?
                            <BlurryPage />
                            :
                            <CommentProvider>
                                <Discussion />
                            </CommentProvider>
                        }

                    </TabPanel>
                </Box>

                <ReactModal
                    isOpen={isOpen}
                    contentLabel="Upload Algorithm"
                    ariaHideApp={false}
                    parentSelector={() => document.querySelector('#root')}
                >
                    <Box sx={{
                        top: '50%',
                        position: 'absolute',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                    }}>
                        <Grid container spacing={2}>
                            <Grid item xs={11}>
                                <Typography sx={{ marginLeft: 10 }} variant="h5">
                                    PVHub Algorithm Upload
                                </Typography>
                            </Grid>
                            <Grid item xs={1}>
                                <CancelIcon
                                    sx={{
                                        "&:hover": {
                                            color: "#ADD8E6",
                                            cursor: "pointer"
                                        },
                                        color: "#18A0FB"
                                    }}
                                    onClick={() => closeModal()} />
                            </Grid>
                        </Grid>
                        <Box sx={{ marginTop: 2, marginBottom: 2 }}>
                            <FileUploader
                                multiple={false}
                                handleChange={uploadFile}
                                name="file"
                                types={fileTypes}
                            />
                        </Box>
                        <Typography sx={{ marginLeft: 20 }} color="gray" variant="body1">
                            {file ? `File name: ${file.name}` : "No files uploaded yet."}
                        </Typography>
                        <Button variant="contained" onClick={handleUpload}>Upload</Button>
                    </Box>
                </ReactModal>
            </Container>
    )
}
