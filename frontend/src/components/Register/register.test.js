import React, { isValidElement } from "react";
import { render, screen, cleanup } from "@testing-library/react";
import Register from "./register";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import * as router from 'react-router';

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render all the elements collectly", () => {
        render(<Register />, {wrapper: BrowserRouter});
        // screen.debug();
        expect(screen.getByRole("heading")).toBeTruthy();
        expect(screen.getByText("Already have an account?")).toBeTruthy();
        expect(screen.getByLabelText(/First Name/i)).toBeTruthy();
        expect(screen.getByLabelText(/Last Name/i)).toBeTruthy();
        expect(screen.getByLabelText(/username/i)).toBeTruthy();
        expect(screen.getByLabelText(/email/i)).toBeTruthy();
        expect(screen.getAllByLabelText(/password/i)[0]).toBeTruthy();
        expect(screen.getAllByLabelText(/password/i)[1]).toBeTruthy();
        // expect(screen.getByLabelText(/confirmPassword/i)).toBeTruthy();
        expect(screen.getByRole("button")).toBeTruthy();
    });
});

describe("Input form onChange event", () => {
    it("Should update input value collectly", async () => {
        render(<Register/>, {wrapper: BrowserRouter});
        const inputValue = screen.getByLabelText(/Username/i);
        await userEvent.type(inputValue, "test");
        expect(inputValue.value).toBe("test");

    });
});

describe("Validate Email", () => {
    it("Should show error when email is not valid", async () => {
        render(<Register/>, {wrapper: BrowserRouter});
        const inputValue = screen.getByLabelText(/Email/i);
        await userEvent.type(inputValue, "NotEmail");
        userEvent.click(screen.getByRole("button"));
        const validation = screen.getByLabelText(/Email/i);
        expect(validation).toHaveAttribute('aria-invalid', 'true');
    });
    it("Should not show error when email is valid", async() => {
        render(<Register/>, {wrapper: BrowserRouter});
        const inputValue = screen.getByLabelText(/Email/i);
        await userEvent.type(inputValue, "test@example.com");
        userEvent.click(screen.getByRole("button"));
        const validation = screen.getByLabelText(/Email/i);
        // expect(validation).toHaveAttribute('aria-invalid', 'false');

    })
});

describe("Validate Username", () => {
    it("Should show error when username is not valid", async () => {
        render(<Register/>, {wrapper: BrowserRouter});
        const inputValue = screen.getByLabelText(/Username/i);
        await userEvent.type(inputValue, "testname");
        userEvent.click(screen.getByRole("button"));

    })
})

describe("Validate setRegError", () => {
    it("should navigate to homepage when all input forms are valid ", async () => {
        const navigate = jest.fn();
        jest.spyOn(router, 'useNavigate').mockImplementation(() => navigate);

        render(<Register/>, {wrapper: BrowserRouter});
        const firstNameInputValue = screen.getByLabelText(/First name/i);
        await userEvent.type(firstNameInputValue, "TestFirstName");
        const lastNameInputValue = screen.getByLabelText(/Last name/i);
        await userEvent.type(lastNameInputValue, "TestLastName");
        const userNameInputValue = screen.getByLabelText(/Username/i);
        await userEvent.type(userNameInputValue, "TestUserName");
        const emailInputValue = screen.getByLabelText(/Email/i);
        await userEvent.type(emailInputValue, "test@example.com");
        const passwordInputValue = screen.getAllByLabelText(/Password/i);
        await userEvent.type(passwordInputValue[0], "testpassword");
        await userEvent.type(passwordInputValue[1], "testpassword");
        userEvent.click(screen.getByRole("button"));
        expect(navigate).toHaveBeenCalledWith('/');
    });
});

describe("Validate Password", () => {
    it("should set error when password length was less than 8 charactors", async () => {
        const navigate = jest.fn();
        jest.spyOn(router, 'useNavigate').mockImplementation(() => navigate);

        render(<Register/>, {wrapper: BrowserRouter});
        const firstNameInputValue = screen.getByLabelText(/First name/i);
        await userEvent.type(firstNameInputValue, "TestFirstName");
        const lastNameInputValue = screen.getByLabelText(/Last name/i);
        await userEvent.type(lastNameInputValue, "TestLastName");
        const userNameInputValue = screen.getByLabelText(/Username/i);
        await userEvent.type(userNameInputValue, "TestUserName");
        const emailInputValue = screen.getByLabelText(/Email/i);
        await userEvent.type(emailInputValue, "test@example.com");
        const passwordInputValue = screen.getAllByLabelText(/Password/i);
        await userEvent.type(passwordInputValue[0], "test");
        await userEvent.type(passwordInputValue[1], "test");
        userEvent.click(screen.getByRole("button"));
        const validation = screen.getAllByLabelText(/password/i);
        expect(validation[0]).toHaveAttribute('aria-invalid', 'true');

    })

    it("should set error when password and confirm password were matched", async () => {
        const navigate = jest.fn();
        jest.spyOn(router, 'useNavigate').mockImplementation(() => navigate);

        render(<Register/>, {wrapper: BrowserRouter});
        const firstNameInputValue = screen.getByLabelText(/First name/i);
        await userEvent.type(firstNameInputValue, "TestFirstName");
        const lastNameInputValue = screen.getByLabelText(/Last name/i);
        await userEvent.type(lastNameInputValue, "TestLastName");
        const userNameInputValue = screen.getByLabelText(/Username/i);
        await userEvent.type(userNameInputValue, "TestUserName");
        const emailInputValue = screen.getByLabelText(/Email/i);
        await userEvent.type(emailInputValue, "test@example.com");
        const passwordInputValue = screen.getAllByLabelText(/Password/i);
        await userEvent.type(passwordInputValue[0], "test1");
        await userEvent.type(passwordInputValue[1], "test2");
        userEvent.click(screen.getByRole("button"));
        const validation = screen.getAllByLabelText(/password/i);
        expect(validation[0]).toHaveAttribute('aria-invalid', 'true');

    })
})