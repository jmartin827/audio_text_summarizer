// @ts-ignore
import React, {useState} from 'react';
import axios from 'axios';
import './App.css';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import {Box, Button, Grid, Link, styled, TextField, Typography} from '@mui/material';

function Process() {
    const [file, setFile] = useState(null);
    const [uuid, setUuid] = useState(null);
    const [status, setStatus] = useState(null);
    const [ratio, setRatio] = useState(1);
    const defaultStatus = 'Upload File To Continue';
    const [isUploading, setIsUploading] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);

    const ScrollableBox = styled(Box)`
      max-height: 400px;
      overflow-y: auto;
    `;

    axios.defaults.baseURL = process.env.REACT_APP_API_BASE;


    const onFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const onRatioChange = (event) => {
        setRatio(parseFloat(event.target.value));
    }

    const onSubmit = (event) => {
        event.preventDefault();
        const formData = new FormData();
        formData.append('in_file', file);
        // @ts-ignore
        formData.append('summary_ratio', ratio);
        setIsUploading(true);

        console.log('POST to /api/process')
        axios.post('/api/process', formData, {responseType: 'json'})
            .then(response => {
                // TODO change back end so the Key in response is descriptive and usable here for all cases.
                console.log('Received response from server:', response);
                if (response.data.Processing) {
                    const uuid = response.data.Processing;
                    setUuid(uuid);
                    setStatus('Processing');
                    pollResult(uuid);

                    setIsUploading(false);
                    setIsProcessing(true)
                }

            })
            .catch(error => {
                console.error('Error occurred during POST request:', error);
                setStatus('Error: Unable to upload');

                setIsProcessing(false);
                setIsUploading(false)
            });
    };

    const pollResult = (uuid) => {
        console.log('POST to /api/result?task_uuid=' + uuid)
        axios.get('/api/result?task_uuid=' + uuid)
            .then(response => {
                console.log('Received response from server:', response);
                //TODO refactor back and front end for better status checks
                if (response.data !== 'Processing') {
                    setStatus(response.data);
                    setIsProcessing(false);
                } else {
                    setTimeout(() => pollResult(uuid), 1000);
                }
            })
            .catch(error => {
                console.error('Error occurred during GET request:', error);
                setIsProcessing(false);
                setIsUploading(false);
            });
    };


    return (
        // <Box sx={{display: "flex", flexDirection: "column", gap: "1rem"}}>
        <form onSubmit={onSubmit}>
            <Box
                sx={{
                    padding: '2rem 4rem', border: "1px solid #ccc",
                    borderRadius: "8px",
                    backgroundColor: "#F9FAFB",
                    height: "auto",

                }}
            >
                <Grid container spacing={1} justifyContent="center">
                    <Grid item xs={2}>
                        <input
                            accept="audio/*"
                            id="contained-button-file"
                            multiple
                            type="file"
                            style={{display: "none"}}
                            onChange={onFileChange}
                            disabled={isProcessing || isUploading}
                        />
                        <label htmlFor="contained-button-file">
                            <Button
                                variant="contained"
                                color="primary"
                                startIcon={<CloudUploadIcon/>}
                                component="span"
                                disabled={isProcessing || isUploading}

                                sx={{opacity: isProcessing || isUploading ? 0.5 : 1}}
                            >
                                {isUploading ? 'Uploading...' : 'Upload'}

                            </Button>
                        </label>
                    </Grid>
                    <Grid item xs={1.3}>
                        <Button
                            variant="contained"
                            color="primary"
                            type="submit"
                            disabled={isProcessing || isUploading}
                            sx={{opacity: isProcessing || isUploading ? 0.5 : 1}}
                        >
                            {isProcessing ? 'Processing...' : 'Submit'}                        </Button>
                    </Grid>
                    <Grid item xs={1.3}>
                        <TextField
                            id="summary-ratio"
                            label="Summary Ratio"
                            fullWidth
                            InputLabelProps={{
                                shrink: true,
                            }}
                            type="number"
                            inputProps={{min: 0.1, max: 1, step: 0.1}}
                            value={ratio}
                            onChange={onRatioChange}
                        />
                    </Grid>
                </Grid>

                {/*Result and status info*/}
                <Grid container spacing={1} justifyContent="center">
                    <Grid item xs={5}>
                        {uuid && (
                            <Typography variant="body1">
                                Task UUID: {uuid}
                            </Typography>
                        )}
                    </Grid>
                </Grid>

                <Grid container spacing={1} justifyContent="center">
                    <Grid item xs={10}>
                        <ScrollableBox>
                            <Box>
                                <Typography variant="h6" gutterBottom>
                                    Status:
                                </Typography>
                                <Box
                                    border={1}
                                    borderColor="primary.main"
                                    borderRadius={2}
                                    p={2}
                                    sx={{
                                        whiteSpace: 'pre-wrap',
                                        overflowWrap: 'break-word',
                                    }}
                                >
                                    {status ? status : defaultStatus}
                                </Box>
                            </Box>
                        </ScrollableBox>
                    </Grid>
                </Grid>


                <Box sx={{
                    position: 'absolute',
                    bottom: 10,
                    left: 0,
                    right: 0,
                    display: 'flex',
                    justifyContent: 'center'
                }}>
                    <Link href="https://github.com/jmartin827/audio_text_summarizer" underline="hover">
                        Github Repository
                    </Link>
                </Box>
            </Box>


        </form>
        // TODO see why form needs a tag here and how to break this down into separate files
    )
        ;
}

export default Process;
