import { Box, Button, TextField } from '@mui/material';
import { Container } from '@mui/system';
import { useState } from 'react';
import Validation from '../../services/validation_service';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import { useNavigate } from "react-router-dom";
import { UserService } from '../../services/user_service';
export default function Register(props) {

    const [registerStates, setRegisterStates] = useState({
        first_name: "",
        last_name: "",
        email: "",
        username: "",
        password: "",
        confirmPassword: ""
    });
    const [registrationErrors, setRegistrationErrors] = useState({
        first_name: "",
        last_name: "",
        email: "",
        username: "",
        password: "",
        confirmPassword: ""
    });
    const navigate = useNavigate();
    const handleChange = (e) => {
        const { id, value } = e.target
        setRegisterStates(prevState => ({
            ...prevState,
            [id]: value
        }));
        setRegistrationErrors(prevState => ({
            ...prevState,
            [id]: ""
        }))
    }

    function isValidEmail(email) {
        let isValid = /\S+@\S+\.\S+/.test(email);
        if (!isValid) {
            return "Invalid Email!";
        }
        return "";
    }

    function validateUsername(username) {
        let isValid = Validation.isUserNameTaken(username);
        if (!isValid) {
            return "Username already taken!";
        }
        return "";
    }

    function passwordValidation(password) {
        let errorStatement = "";
        if (!password || password.length === 0) {
            errorStatement = "Password is a required field";

        }
        else if (password.length < 8) {
            errorStatement = "Password must be atleast 8 characters";
        }
        return errorStatement;
    }

    function confirmPasswordValidation(password, confirmPassword) {
        let isValid = password === confirmPassword;
        if (!isValid) {
            return "Passwords must match!";
        }
        return "";
    }

    const submitHandler = (e) => {
        let firstNameError = registerStates.first_name !== "" ? "" : "First Name Required";
        let lastNameError = registerStates.last_name !== "" ? "" : "Last Name Required";
        let emailError = isValidEmail(registerStates.email);
        let userNameError = validateUsername(registerStates.username);
        let passwordError = passwordValidation(registerStates.password);
        let confirmPasswordError = confirmPasswordValidation(registerStates.confirmPassword, registerStates.password);
        if (firstNameError !== "" || lastNameError !== ""
            || emailError !== "" || userNameError !== "" ||
            passwordError !== "" || confirmPasswordError !== "") {
            setRegistrationErrors(prevState => ({
                [registrationErrors.first_name]: firstNameError,
                [registrationErrors.last_name]: lastNameError,
                [registrationErrors.email]: emailError,
                [registrationErrors.username]: userNameError,
                [registrationErrors.password]: passwordError,
                [registrationErrors.confirmPassword]: confirmPasswordError
            }));
        }
        else {
            setRegistrationErrors(prevState => ({
                [registrationErrors.first_name]: "",
                [registrationErrors.last_name]: "",
                [registrationErrors.error]: "",
                [registrationErrors.username]: "",
                [registrationErrors.password]: "",
                [registrationErrors.confirmPassword]: ""
            }));
            const response = UserService.register(
                registerStates.username,
                registerStates.email,
                registerStates.password
            );
            if (response!== null) {
                navigate("/login");
            }
        }
    }

    return (
        <Container
            sx={{
                display: 'flex',
                justifyContent: 'center',
                p: 1,
                m: 1,
            }}
        >
            {/* <Box sx={{ display: 'flex' }}>
                <div>
                    <Typography variant="h4" gutterBottom>
                        PV Validation Hub - Developer Role
                    </Typography>
                </div>
                <div>
                    <Typography variant="body1" gutterBottom>
                        Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos
                        blanditiis tenetur unde suscipit, quam beatae rerum inventore consectetur,
                        neque doloribus, cupiditate numquam dignissimos laborum fugiat deleniti? Eum
                        quasi quidem quibusdam.
                    </Typography>
                </div>
            </Box> */}
            <Box
                component="form"
                sx={{
                    '& .MuiTextField-root': { m: 1, width: '36ch' },
                    '& .MuiButtonBase-root': { m: 1 },
                    border: '1.3px solid black',
                    padding: '4em'
                }}
                noValidate
                autoComplete="off"
            >   <div>
                    <Typography variant="h4" gutterBottom>Register</Typography>
                    <Typography variant="body1"><Link href="/login">Already have an account?</Link></Typography>
                </div>
                <div>

                    <TextField
                        sx={{ '& .MuiTextField-root': { m: 1, width: '18ch' } }}
                        required
                        id="first_name"
                        label="First Name"
                        value={registerStates.first_name}
                        onChange={handleChange}
                        error={registrationErrors.first_name !== ""}
                        helperText={registrationErrors.first_name}
                    />
                </div>
                <div>
                    <TextField
                        sx={{ '& .MuiTextField-root': { m: 1, width: '36ch' } }}
                        required
                        id="last_name"
                        label="Last Name"
                        value={registerStates.last_name}
                        onChange={handleChange}
                        error={registrationErrors.last_name !== ""}
                        helperText={registrationErrors.last_name}
                    />
                </div>
                <div>
                    <TextField
                        required
                        id="username"
                        label="Username"
                        value={registerStates.username}
                        onChange={handleChange}
                        error={registrationErrors.username !== ""}
                        helperText={registrationErrors.username}
                    />
                </div>
                <div>
                    <TextField
                        id="email"
                        label="Email"
                        value={registerStates.email}
                        onChange={handleChange}
                        error={registrationErrors.email !== ""}
                        helperText={registrationErrors.email}
                    />
                </div>
                <div>
                    <TextField
                        required
                        type="password"
                        id="password"
                        label="Password"
                        value={registerStates.password}
                        onChange={handleChange}
                        error={registrationErrors.password !== ""}
                        helperText={registrationErrors.password}
                    />
                </div>
                <div>
                    <TextField
                        required
                        type="password"
                        id="confirmPassword"
                        label="Confirm Password"
                        value={registerStates.confirmPassword}
                        onChange={handleChange}
                        error={registrationErrors.confirmPassword !== ""}
                        helperText={registrationErrors.confirmPassword}
                    />
                </div>
                <div>
                    <Button variant="contained" onClick={submitHandler}>Register</Button>
                </div>
            </Box>
        </Container>
    );
}
