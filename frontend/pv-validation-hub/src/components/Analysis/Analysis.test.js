import React from "react";
import { render, screen, cleanup } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import * as router from 'react-router';
import Analysis from "./Analysis";
import { selectUnstyledClasses } from "@mui/base";

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render all the elements collectly", () => {
        render(<Analysis/>, {wrapper: BrowserRouter});
        expect(screen.getByRole('heading', {level: 2})).toBeTruthy();
    });
});

describe("Selecting Tabs", () => {
    it("Should show Upload Algorithm button when Leaderboard tub was chosen", async () => {
        render(<Analysis/>, {wrapper: BrowserRouter});
        const tabLearderboard = screen.getByRole('tab', {name: 'Leaderboard'});
        expect(tabLearderboard).toBeTruthy();
        await userEvent.click(tabLearderboard);
        expect(tabLearderboard).toHaveAttribute("aria-selected","true");
        expect(screen.getByRole('button', {name: 'Upload Algorithm'})).toBeTruthy();
    });
});