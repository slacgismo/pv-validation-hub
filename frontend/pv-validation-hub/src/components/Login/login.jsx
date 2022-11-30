import { useState } from "react";
import { Box, Button, TextField } from '@mui/material';
import { Container } from "@mui/system";
import Validation from '../../services/validation_service';
import { useNavigate } from "react-router-dom";
import Cookies from 'universal-cookie';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import { UserService } from "../../services/user_service";

export default function Login() {

    const cookies = new Cookies();

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
            const loginResponse = UserService.login(username, password);
            if (loginResponse != null) {
                cookies.set("user", loginResponse.user_id, { path: '/', sameSite: "strict" });
                //cookies.set("user", "juliusomo", { path: '/', sameSite: "strict" });
                navigate("/dashboard");
            }
            else{
                cookies.set("user", "juliusomo", { path: '/', sameSite: "strict", maxAge: 7200000 });
                navigate("/dashboard");
            }
        }
        else {
            setLoginErrors(prevState => ({
                [username]: usernameError,
                [password]: password === "" ? "We need a password" : ""
            }))
        }

    }

    return (
        <Container
            sx={{
                display: 'flex',
                justifyContent: 'center',
                p: 1,
                m: 1,
            }}>
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
                <div>
                    <Typography variant="h4" gutterBottom>Sign In</Typography>
                    <Typography variant="body1"><Link href="/register">New to PV Validation Hub</Link></Typography>
                </div>
                <div>
                    <TextField
                        required
                        id="username"
                        label="Username/Email"
                        value={loginStates.username}
                        onChange={handleChange}
                        error={loginErrors.username !== ""}
                        helperText={loginErrors.username}
                    />
                </div>
                <div>
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
                </div>
                <div>
                    <Button variant="contained" onClick={submitHandler}>Login</Button>
                </div>
            </Box>
        </Container>
    )
}

// Login.propTypes = {
//     setToken: PropTypes.func.isRequired
// }