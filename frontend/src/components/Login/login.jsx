import { useState } from "react";
import { Grid, Alert, Box, Button, TextField } from '@mui/material';
import Validation from '../../services/validation_service';
import { useNavigate } from "react-router-dom";
import Cookies from 'universal-cookie';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import client from "../../services/api_service";

export default function Login() {

    const cookies = new Cookies();

    const [showAlert, setShowAlert] = useState(false);

    const navigate = useNavigate();
    const [loginStates, setLoginStates] = useState({
        username: "",
        password: "",
    });

    const [loginErrors, setLoginErrors] = useState({
        username: "",
        password: ""
    })

    const handleChange = (e) => {
        const { id, value } = e.target
        setLoginStates(prevState => ({
            ...prevState,
            [id]: value
        }));
        setLoginErrors(prevState => ({
            ...prevState,
            [id]: ""
        }))
    }

    function isEmail(username) {
        if (/\S+@\S+\.\S+/.test(username)) {
            return true;
        }
        return false;
    }

    function validateUsername(username) {
        let isValid = false;
        let output = "";
        if (username === "") {
            output = "Username can't be empty";
        }
        else {
            if (isEmail(username)) {
                isValid = Validation.isEmailInUse(username);
                output = "Email not found";
            }
            else {
                isValid = Validation.isUserNameTaken(username);
                output = "Username not found";
            }
        }
        if (isValid) {
            output = "";
        }
        return output;
    }

    const submitHandler = (e) => {
        let username = loginStates.username;
        let password = loginStates.password;
        let usernameError = validateUsername(username);

        if (usernameError === "" && password !== "") {
            client.post("/login", {
                username: username,
                password: password
            }).then(response => {
                cookies.set("user", {
                    token : response.data.token,
                },
                { path: '/', sameSite: "strict" });
                navigate("/");
            }).catch(error => {
                setShowAlert(true);
                setTimeout(() => { setShowAlert(false) }, 3000);
            })
        }
        else {
            setLoginErrors(prevState => ({
                [username]: usernameError,
                [password]: password === "" ? "We need a password" : ""
            }))
        }

    }

    return (
        <Grid container justifyContent="center" alignItems="center" sx={{ mt: '10px' }}>
            {
                showAlert &&
                <Alert severity="error">Login Failed</Alert>
            }
            <Box
                component="form"
                sx={{
                    '& .MuiTextField-root': { m: 1, width: '35ch' },
                    '& .MuiButtonBase-root': { m: 1 },
                    border: '1px solid black',
                    padding: '4em'
                }}
                noValidate
                autoComplete="off"
            >
                <Box>
                    <Typography variant="h4" gutterBottom>Sign In</Typography>
                    <Typography variant="body1"><Link href="/register">New to PV Validation Hub</Link></Typography>
                </Box>
                <Box>
                    <TextField
                        required
                        id="username"
                        label="Username"
                        value={loginStates.username}
                        onChange={handleChange}
                        error={loginErrors.username !== ""}
                        helperText={loginErrors.username}
                    />
                </Box>
                <Box>
                    <TextField
                        required
                        type="password"
                        id="password"
                        label="Password"
                        value={loginStates.password}
                        onChange={handleChange}
                        error={loginErrors.password !== ""}
                        helperText={loginErrors.password}
                    />
                </Box>
                <Box>
                    <Button variant="contained" onClick={submitHandler}>Login</Button>
                </Box>
            </Box>
        </Grid>
    )
}
