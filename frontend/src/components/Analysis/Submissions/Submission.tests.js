import React from "react";
import { render, screen, cleanup } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import Submission from "./Submission";

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render each column header collectly", () => {
        render(<div id="root"><Submission/></div>, {wrapper: BrowserRouter});
        expect(screen.getByText(/Analysis ID/i)).toBeTruthy();
        expect(screen.getByText(/Ranking/i)).toBeTruthy();
        expect(screen.getByText(/Score/i)).toBeTruthy();
        expect(screen.getByText(/Submit Time/i)).toBeTruthy();
        expect(screen.getByText(/Time to Execute/i)).toBeTruthy();
        expect(screen.getByText(/Error/i)).toBeTruthy();
        expect(screen.getByText(/Algorithm/i)).toBeTruthy();
    });

    it("Should render each row collectly", () => {
        render(<div id="root"><Submission/></div>, {wrapper: BrowserRouter});
        const firstRow = screen.getAllByRole("checkbox")[0];
        expect(firstRow).toBeTruthy();
        // Check the number of items that each row has (expected 7 : number of column headers))
        expect(firstRow.getElementsByClassName("MuiTableCell-root").length).toBe(7);
    })
});