import React from "react";
import { render, screen, cleanup } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import Rules from "./Rules";

afterEach (()=> cleanup());

describe("Rendering", () => {
    it("Should render all the elements collectly", () => {
        render(<div id="root"><Rules/></div>, {wrapper: BrowserRouter});
        expect(screen.getByRole('heading', {level: 5})).toBeTruthy();
    });
});