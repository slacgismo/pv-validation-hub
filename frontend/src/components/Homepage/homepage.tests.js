/**
 * @jest-environment jsdom
 */
import React from "react";
import { render, screen, cleanup } from "@testing-library/react";
import Homepage from "./Homepage";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import * as router from 'react-router';

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render all the elements collectly", () => {
        render(<Homepage />, {wrapper: BrowserRouter});
        expect(screen.getByRole("heading", {name: /PV Validation HUB/i})).toBeTruthy();
        expect(screen.getAllByRole("button", {name: /Join Today/i})[0]).toBeTruthy();
        expect(screen.getAllByRole("button", {name: /Join Today/i})[1]).toBeTruthy();
        expect(screen.getByAltText(/PV Validation Hub/i)).toBeTruthy();
        expect(screen.getByRole("button", {name: /Contact Us/i})).toBeTruthy();
    });
});

describe("The buttons for register", () => {
    it("Should navigate register page when the Join Today button on the top was pressed", async () => {
        const navigate = jest.fn();
        jest.spyOn(router, 'useNavigate').mockImplementation(() => navigate);
        render(<Homepage />, {wrapper: BrowserRouter});

        // Check if the Join Today Button on the top works
        const topJoinButton = screen.getAllByRole("button", {name: /Join Today/i})[0];
        await userEvent.click(topJoinButton);
        expect(navigate).toHaveBeenCalledWith('/register');
    });

    it("Should navigate register page when the Join Today button on the bottom was pressed", async () => {
        const navigate = jest.fn();
        jest.spyOn(router, 'useNavigate').mockImplementation(() => navigate);
        render(<Homepage />, {wrapper: BrowserRouter});

        // Check if the Join Today Button on the bottom works
        const bottomJoinButton = screen.getAllByRole("button", {name: /Join Today/i})[1];
        await userEvent.click(bottomJoinButton);
        expect(navigate).toHaveBeenCalledWith('/register');

    });
});

describe("The button for contacting us", () => {
    let windowSpy;

    beforeEach(() => {
    windowSpy = jest.spyOn(window, "open");
    });

    afterEach(() => {
    windowSpy.mockRestore();
    });

    it('Should navigate mailto screen when the button was pressed', async () => {
        const mockPathname = jest.fn();
        Object.defineProperty(window, 'location', {
            writable: true,
            value: {
                get pathname() {
                return mockPathname();
            },},
        });

        render(<Homepage/>, {wrapper: BrowserRouter});
        const contactUsButton = screen.getByRole("button", {name: /Contact Us/i});
        await userEvent.click(contactUsButton);
        expect(mockPathname).toHaveBeenCalled();
    });
});