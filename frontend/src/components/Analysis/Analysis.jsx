import React, { useState, useEffect } from 'react';
import {
  Box, Grid, Button, Tab, Tabs, Typography, CircularProgress,
} from '@mui/material';
import { Container } from '@mui/system';
import ReactModal from 'react-modal';
import Cookies from 'universal-cookie';
import { FileUploader } from 'react-drag-drop-files';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import TabPanel from '../GlobalComponents/TabPanel/TabPanel.jsx';
import Data from './Data/Data.jsx';
// import { CommentProvider } from './Discussion/CommentContext.js';
// import Discussion from './Discussion/Discussion.jsx';
import Leaderboard from './Leaderboard/Leaderboard.jsx';
import Overview from './Overview/Overview.jsx';
import Rules from './Rules/Rules.jsx';
import Submission from './Submissions/Submission.jsx';
import BlurryPage from '../GlobalComponents/BlurryPage/blurryPage.jsx';
import AnalysisService from '../../services/analysis_service.js';
import replaceImagePaths from '../../config/mdurl.js';

export default function Analysis() {
  const navigate = useNavigate();
  const cookies = new Cookies();
  const user = cookies.get('user');

  const [value, setValue] = useState(0);
  const [uploadSuccess, setUploadSuccess] = useState(null);

  const [isOpen, setIsOpen] = useState(false);

  // disable eslint for the next line because the array is destructured
  // eslint-disable-next-line no-unused-vars
  const [isLoading, error, card, analysisId] = AnalysisService.useGetCardDetails();

  // Set the md descriptions

  const [datasetDescription, setDatasetDescription] = useState('');
  const [longDescription, setLongDescription] = useState('');
  const [rulesetDescription, setRulesetDescription] = useState('');
  const [coverImageDir, setCoverImageDir] = useState('');

  const [file, setFile] = useState(null);

  useEffect(() => {
    console.log('analysis', analysisId, typeof analysisId);
    if (analysisId !== undefined && analysisId !== null
            && (analysisId > 0 || analysisId === 'development')) {
      setCoverImageDir(`${process.env.PUBLIC_URL}/assets/${analysisId}/banner.png`);
      console.log(coverImageDir);

      fetch(`${process.env.PUBLIC_URL}/assets/${analysisId}/dataset.md`)
        .then((res) => res.text())
        .then((text) => setDatasetDescription(text))
        .catch((err) => console.log(err));

      fetch(`${process.env.PUBLIC_URL}/assets/${analysisId}/description.md`)
        .then((res) => res.text())
        .then((text) => replaceImagePaths(text, analysisId))
        .then((text) => setLongDescription(text))
        .catch((err) => console.log(err));

      fetch(`${process.env.PUBLIC_URL}/assets/${analysisId}/SubmissionInstructions.md`)
        .then((res) => res.text())
        .then((text) => replaceImagePaths(text, analysisId))
        .then((text) => setRulesetDescription(text))
        .catch((err) => console.log(err));
    } else {
      console.error('Analysis ID not found');
    }
    // eslint-disable-next-line
  }, [analysisId]);

  const closeModal = () => {
    setIsOpen(false);
    setUploadSuccess('emptyDisplay');
  };

  const openModal = () => {
    setIsOpen(true);
  };

  // lmao, you can't use "tar.gz", only "gz", anything after the last "." works
  const fileTypes = ['ZIP', 'GZ'];

  const uploadFile = (fileObject) => {
    setFile(fileObject);
  };

  const handleUpload = async () => {
    try {
      const response = await AnalysisService.uploadAlgorithm(analysisId, user.token, file);
      console.log('response:', response);
      if (response.status === 200) {
        setUploadSuccess(true);
        setFile(null);
      } else {
        setUploadSuccess(false);
      }
    } catch (errorCode) {
      console.error('Upload failed:', errorCode);
      setUploadSuccess(false);
    }
  };

  const handleActive = () => file !== null;

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    isLoading !== false ? <CircularProgress />
      : (
        <Container id="analysis">
          <Box sx={{
            flexGrow: 1,
            marginTop: 3,
            height: 200,
            backgroundImage: `url(${coverImageDir})`,
          }}
          >
            <Box sx={{ flexGrow: 1, marginTop: 4, marginLeft: 2 }}>
              <Typography color="black" variant="h4" gutterBottom>
                {card.analysis_name}
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
                    <Tab label="Instructions" />
                    {
                      // <Tab label="Discussion" />
                    }
                  </Tabs>
                </Grid>

                <Grid item xs={6} md={2}>
                  <Button
                    align="right"
                    variant="contained"
                    onClick={() => {
                      if (user === undefined || user === null) {
                        navigate('/login');
                      }
                      openModal();
                    }}
                    sx={{
                      backgroundColor: 'black',
                      width: '100%',
                      height: '70%',
                      marginTop: 1,
                    }}
                  >
                    <Typography texttransform="none">
                      Upload Algorithm
                    </Typography>
                  </Button>
                </Grid>
              </Grid>
            </Box>

            <TabPanel value={value} index={0}>
              <Overview
                title={`Overview of ${card.analysis_name}`}
                description={longDescription}
              />
            </TabPanel>

            <TabPanel value={value} index={1}>
              {
                            user === undefined || user === null
                              ? <BlurryPage />
                              : (
                                <Data
                                  dataDescription={datasetDescription}
                                />
                              )
                        }
            </TabPanel>

            <TabPanel value={value} index={2}>
              <Leaderboard
                analysisId={analysisId}
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
                            user === undefined || user == null
                              ? <BlurryPage />
                              : (
                                <Submission
                                  analysisId={analysisId}
                                  userId={user !== null || user !== undefined ? user.id : user}
                                />
                              )
                        }
            </TabPanel>
            {/*
            Disabled until discussions properly implemented
            <TabPanel value={value} index={5}>
              {user === undefined || user == null
                ? <BlurryPage />
                : (
                  <CommentProvider>
                    <Discussion />
                  </CommentProvider>
                )}

            </TabPanel>
            */}
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
            }}
            >
              <Grid container spacing={2}>
                <Grid item xs={11}>
                  <Typography sx={{ marginLeft: 10 }} variant="h5">
                    PVHub Algorithm Upload
                  </Typography>
                </Grid>
                <Grid item xs={1}>
                  <Button onClick={closeModal}>Exit</Button>
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
                {file ? `File name: ${file.name}` : 'No files staged for upload yet.'}
              </Typography>
              {uploadSuccess === true && (
              <Typography color="green" variant="body1">
                Upload Successful! Please check your developer page for the status of
                your upload, or upload another file.
              </Typography>
              )}
              {uploadSuccess === false && (
              <Typography color="red" variant="body1">
                Upload failed. Please reload the page and try again. If you continue
                to receive issues with the upload, please file an issue at our github page,
                {' '}
                <a href="https://github.com/slacgismo/pv-validation-hub">https://github.com/slacgismo/pv-validation-hub</a>
                .
              </Typography>
              )}
              <Button disabled={!handleActive()} variant="contained" onClick={handleUpload}>Upload</Button>
            </Box>
          </ReactModal>
        </Container>
      )
  );
}

// Validate Props
Analysis.propTypes = {
  card: PropTypes.shape({
    analysis_id: PropTypes.number,
    analysis_name: PropTypes.string,
  }),
};

Analysis.defaultProps = {
  card: {
    analysis_id: null,
    analysis_name: '',
  },
};
