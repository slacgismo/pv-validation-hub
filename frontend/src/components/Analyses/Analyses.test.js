import React from "react";
import { render, screen, cleanup } from "@testing-library/react";
import Dashboard from "./Dashboard";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import * as router from 'react-router';

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render all the elements collectly", () => {
        render(<Dashboard/>, {wrapper: BrowserRouter});
        expect(screen.getByRole('heading', {level: 2})).toBeTruthy();
        expect(screen.getAllByRole('button', {Name: 'settings'})).toBeTruthy();
        expect(screen.getAllByRole('button', {Name: "add to favorites"})).toBeTruthy();
        expect(screen.getAllByRole('button', {Name: "share"})).toBeTruthy();
    });
});

describe("Analysis Cards", () => {
    it("Should navigate to each analysis page when the card was clicked", async () => {
        const navigate = jest.fn();
        jest.spyOn(router, 'useNavigate').mockImplementation(() => navigate);

        render(<Dashboard/>, {wrapper: BrowserRouter});

        const buttonSettings = screen.getAllByRole('button', {Name: 'settings'})[0];
        await userEvent.click(buttonSettings)
        expect(navigate).toHaveBeenCalled();
    });
});
