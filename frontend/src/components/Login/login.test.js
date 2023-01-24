import React from "react";
import { render, screen, cleanup } from "@testing-library/react";
import Login from "./login";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import * as router from 'react-router';

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render all the elements collectly", () => {
        render(<Login />, {wrapper: BrowserRouter});
        expect(screen.getByText("Sign In")).toBeTruthy();
        expect(screen.getByText("New to PV Validation Hub")).toBeTruthy();
        expect(screen.getByLabelText(/Username\/Email/i)).toBeTruthy();
        expect(screen.getByLabelText(/password/i)).toBeTruthy();
        expect(screen.getByRole("button")).toBeTruthy();
    });
});

describe("Input form onChange event", () => {
    it("Should update input value collectly", async () => {
        render(<Login/>, {wrapper: BrowserRouter});
        const inputValue = screen.getByLabelText(/Username\/Email/i);
        await userEvent.type(inputValue, "test");
        expect(inputValue.value).toBe("test");

    });
});

describe("Validate username", () => {
    it("Should show error when username is not valid", async () => {
        render(<Login/>, {wrapper: BrowserRouter});
        const inputValue = screen.getByLabelText(/Username\/Email/i);
        await userEvent.type(inputValue, "NotEmail");
        userEvent.click(screen.getByRole("button"));
        const validation = screen.getByLabelText(/Username\/Email/i);
        expect(validation).toHaveAttribute('aria-invalid', 'true');
    });
    it("Should show error when username is blank", async () => {
        render(<Login/>, {wrapper: BrowserRouter});
        const inputValue = screen.getByLabelText(/Username\/Email/i);
        userEvent.click(screen.getByRole("button"));
        const validation = screen.getByLabelText(/Username\/Email/i);
        expect(validation).toHaveAttribute('aria-invalid', 'true');
    });
    it("Should not show error when username/Email is valid", async () => {
        render(<Login/>, {wrapper: BrowserRouter});
        const inputValue = screen.getByLabelText(/Username\/Email/i);
        await userEvent.type(inputValue, "test@example.com");
        userEvent.click(screen.getByRole("button"));
        const validation = screen.getByLabelText(/Username\/Email/i);
        // Reminder "Need to check how to test not showing error"
        expect(validation).toHaveAttribute('aria-invalid', 'true');
    });
});

describe("Validate password", () => {
    it("Should navigate to homepage if valid Username and password", async () => {
        const navigate = jest.fn();
        jest.spyOn(router, 'useNavigate').mockImplementation(() => navigate);
        render(<Login/>, {wrapper: BrowserRouter});
        const inputUsername = screen.getByLabelText(/Username\/Email/i);
        await userEvent.type(inputUsername, "test@example.com");
        const inputPassword = screen.getByLabelText(/Password/i);
        await userEvent.type(inputPassword, "password");
        userEvent.click(screen.getByRole("button"));
        expect(navigate).toHaveBeenCalledWith('/');
    });
});