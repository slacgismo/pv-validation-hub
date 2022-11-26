import React from "react";
import { render, screen, cleanup } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import * as router from 'react-router';
import Leaderboard from "./Leaderboard";

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render all the elements collectly", () => {
        render(<Leaderboard/>, {wrapper: BrowserRouter});
        expect(screen.getByRole('table')).toBeTruthy();
    });
});