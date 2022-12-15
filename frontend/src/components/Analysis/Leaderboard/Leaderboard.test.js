import React from "react";
import { render, screen, cleanup } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import userEvent from "@testing-library/user-event";
import * as router from 'react-router';
import Leaderboard from "./Leaderboard";

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render the table and each column collectly", () => {
        render(<Leaderboard/>, {wrapper: BrowserRouter});
        expect(screen.getByRole('table')).toBeTruthy();
        expect(screen.getByText(/Ranking/i)).toBeTruthy();
        expect(screen.getByText(/Developer Group/i)).toBeTruthy();
        expect(screen.getByText(/Submission/i)).toBeTruthy();
    });

    it("Should render each row collectly", () => {
        render(<div id="root"><Leaderboard/></div>, {wrapper: BrowserRouter});
        const firstRow = screen.getAllByRole("checkbox")[0];
        expect(firstRow).toBeTruthy();
        // Check the number of items that each row has (expected 3 : number of column headers))
        expect(firstRow.getElementsByClassName("MuiTableCell-root").length).toBe(3);
    });
});